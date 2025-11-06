"""
MCP (Model Context Protocol) client for MCPAGENT
"""
try:
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
except ImportError:
    ClientSession = None
    streamablehttp_client = None

try:
    from langchain_mcp_adapters.tools import load_mcp_tools as langchain_load_mcp_tools
except ImportError:
    langchain_load_mcp_tools = None
from typing import List, Optional, Dict
from langchain_core.tools import BaseTool
from pathlib import Path
import json

from src.config import settings
from src.config.logging import get_logger

logger = get_logger(__name__)


class MCPClientManager:
    """Context manager to maintain MCP sessions"""
    
    def __init__(self, mcp_servers: List[Dict], timeout: int = 30):
        """
        Initialize with a list of MCP server configurations
        
        Args:
            mcp_servers: List of server configs with 'name', 'url', optional 'headers'
            timeout: Timeout for MCP connections
        """
        self.mcp_servers = mcp_servers
        self.timeout = timeout
        self.sessions = []
        self.tools: List[BaseTool] = []
        
    async def __aenter__(self):
        """Load tools from all configured MCP servers and keep sessions alive"""
        
        if ClientSession is None or streamablehttp_client is None:
            logger.warning("MCP package not installed. Cannot load MCP tools.")
            return []
        
        if langchain_load_mcp_tools is None:
            logger.warning("langchain-mcp-adapters not installed. Cannot load MCP tools.")
            return []
        
        logger.info(f"Connecting to {len(self.mcp_servers)} MCP server(s)...")
        
        for server_config in self.mcp_servers:
            server_name = server_config.get("name", "Unknown")
            server_url = server_config["url"]
            server_headers = server_config.get("headers", {})
            api_key = server_config.get("api_key")
            
            # Normalize URL
            final_url = server_url.rstrip('/')
            if final_url.endswith('/sse'):
                final_url = final_url[:-4]
            if not final_url.endswith('/mcp'):
                final_url = final_url.rstrip('/') + '/mcp'
            
            logger.info(f"Loading tools from {server_name} ({final_url})")
            
            try:
                # Prepare connection params
                server_params = {"url": final_url}
                
                # Build headers
                headers = dict(server_headers) if server_headers else {}
                if api_key:
                    api_key_header = server_config.get("api_key_header", "x-api-key")
                    headers[api_key_header] = api_key
                
                if headers:
                    server_params["headers"] = headers
                
                # Connect to server
                client = streamablehttp_client(**server_params)
                read, write, _ = await client.__aenter__()
                session = ClientSession(read, write)
                await session.__aenter__()
                await session.initialize()
                
                # Load tools
                tools = await langchain_load_mcp_tools(session)
                self.tools.extend(tools)
                self.sessions.append((client, session))
                
                logger.info(f"✓ Loaded {len(tools)} tool(s) from {server_name}")
                for tool in tools:
                    logger.debug(f"  - {tool.name}: {tool.description}")
                    
            except Exception as e:
                logger.error(f"Failed to load {server_name} MCP tools: {e}")
                # Continue with other servers
                continue
        
        logger.info(f"Total MCP tools loaded: {len(self.tools)}")
        return self.tools
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up all sessions"""
        if not self.sessions:
            return
        
        logger.info("Closing MCP sessions...")
        import asyncio
        
        for client, session in reversed(self.sessions):
            if session:
                try:
                    await asyncio.wait_for(
                        session.__aexit__(exc_type, exc_val, exc_tb),
                        timeout=1.0
                    )
                except Exception:
                    pass
            
            if client:
                try:
                    await asyncio.wait_for(
                        client.__aexit__(exc_type, exc_val, exc_tb),
                        timeout=1.0
                    )
                except Exception:
                    pass
        
        self.sessions.clear()
        logger.info("All MCP sessions closed")


async def load_mcp_tools(config_file: Optional[Path] = None) -> List[BaseTool]:
    """
    Load MCP tools from configuration file
    
    Args:
        config_file: Path to mcp_servers.json config file
        
    Returns:
        List of LangChain tools from MCP servers
    """
    if config_file is None:
        config_file = Path("config/mcp_servers.json")
    
    if not config_file.exists():
        logger.warning(f"MCP config file not found: {config_file}")
        return []
    
    try:
        with open(config_file, 'r') as f:
            mcp_servers = json.load(f)
        
        # Filter enabled servers
        enabled_servers = [s for s in mcp_servers if s.get("enabled", True)]
        
        if not enabled_servers:
            logger.warning("No enabled MCP servers in configuration")
            return []
        
        # Load tools using context manager
        async with MCPClientManager(enabled_servers) as tools:
            return list(tools)  # Return copy of tools
            
    except Exception as e:
        logger.error(f"Error loading MCP tools: {e}")
        return []

