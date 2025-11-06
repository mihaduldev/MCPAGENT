"""
Multi-agent orchestration system with specialized agents
"""

from typing import List, Dict, Any, Optional, Literal
from enum import Enum

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import BaseTool

from src.config import settings
from src.config.logging import get_logger
from src.infrastructure.llm.llm_factory import create_llm

logger = get_logger(__name__)


class AgentType(str, Enum):
    """Agent types"""
    RESEARCH = "research"
    CODING = "coding"
    DATA_ANALYSIS = "data_analysis"
    GENERAL = "general"


class Agent:
    """Specialized agent with specific tools and capabilities"""
    
    def __init__(
        self,
        agent_type: AgentType,
        tools: List[BaseTool],
        name: str,
        description: str,
        system_prompt: Optional[str] = None
    ):
        """
        Initialize agent
        
        Args:
            agent_type: Type of agent
            tools: List of tools available to agent
            name: Agent name
            description: Agent description
            system_prompt: Custom system prompt
        """
        self.agent_type = agent_type
        self.tools = tools
        self.name = name
        self.description = description
        self.system_prompt = system_prompt or self._get_default_prompt()
        
        # Create LLM instance
        self.llm = create_llm()
        
        # Create agent executor
        self.executor = create_react_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
        
        logger.info(f"Agent '{self.name}' initialized with {len(tools)} tools")
    
    def _get_default_prompt(self) -> str:
        """Get default system prompt based on agent type"""
        prompts = {
            AgentType.RESEARCH: (
                "You are a research assistant specialized in finding, analyzing, "
                "and synthesizing information from various sources. You excel at "
                "web research, document analysis, and knowledge synthesis."
            ),
            AgentType.CODING: (
                "You are a coding assistant specialized in writing, debugging, "
                "and explaining code. You are proficient in multiple programming "
                "languages and software engineering best practices."
            ),
            AgentType.DATA_ANALYSIS: (
                "You are a data analysis specialist. You excel at statistical "
                "analysis, data visualization, and deriving insights from data. "
                "You can work with various data formats and analysis tools."
            ),
            AgentType.GENERAL: (
                "You are a helpful AI assistant with access to various tools. "
                "Use the tools when appropriate to provide accurate and helpful "
                "responses to user queries."
            )
        }
        return prompts.get(self.agent_type, prompts[AgentType.GENERAL])
    
    async def invoke(
        self,
        query: str,
        history: Optional[List[BaseMessage]] = None
    ) -> Dict[str, Any]:
        """
        Invoke agent with query
        
        Args:
            query: User query
            history: Conversation history
            
        Returns:
            Agent response with metadata
        """
        try:
            # Build messages
            messages = list(history) if history else []
            messages.append(HumanMessage(content=query))
            
            # Invoke agent
            result = await self.executor.ainvoke({"messages": messages})
            
            # Extract response
            final_message = result["messages"][-1]
            response = final_message.content if isinstance(final_message, AIMessage) else str(final_message)
            
            # Collect tool usage
            tools_used = []
            for msg in result["messages"]:
                if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
                    for call in msg.tool_calls or []:
                        tools_used.append(call.get("name", "unknown"))
            
            # Extract token usage from result if available
            # LangGraph/LangChain agents may store token usage in various places
            token_usage = None
            
            # Check result dict for token_usage
            if isinstance(result, dict) and "token_usage" in result:
                token_usage = result["token_usage"]
            
            # Check final message for response_metadata
            if not token_usage and hasattr(final_message, "response_metadata") and final_message.response_metadata:
                token_usage = final_message.response_metadata.get("token_usage")
            
            # Check all messages for token usage (some agents store it in intermediate messages)
            if not token_usage:
                for msg in reversed(result["messages"]):
                    if hasattr(msg, "response_metadata") and msg.response_metadata:
                        usage = msg.response_metadata.get("token_usage")
                        if usage:
                            token_usage = usage
                            break
                    
                    # Also check for usage_metadata (alternative format)
                    if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        usage_obj = msg.usage_metadata
                        if hasattr(usage_obj, "prompt_tokens"):
                            token_usage = {
                                "prompt_tokens": usage_obj.prompt_tokens,
                                "completion_tokens": usage_obj.completion_tokens,
                                "total_tokens": getattr(usage_obj, "total_token_count", 
                                                       usage_obj.prompt_tokens + usage_obj.completion_tokens)
                            }
                            break
            
            return {
                "response": response,
                "agent": self.name,
                "agent_type": self.agent_type.value,
                "tools_used": list(set(tools_used)),
                "token_usage": token_usage,
                "success": True
            }
        
        except Exception as e:
            logger.error(f"Agent '{self.name}' execution error: {e}")
            return {
                "response": f"Agent error: {str(e)}",
                "agent": self.name,
                "agent_type": self.agent_type.value,
                "tools_used": [],
                "success": False,
                "error": str(e)
            }


class MultiAgentOrchestrator:
    """Orchestrator for managing multiple specialized agents"""
    
    def __init__(self):
        """Initialize multi-agent orchestrator"""
        self.agents: Dict[AgentType, Agent] = {}
        self.enabled = settings.enable_multi_agent
        logger.info(f"Multi-agent orchestrator initialized (enabled={self.enabled})")
    
    def register_agent(self, agent: Agent) -> None:
        """Register an agent"""
        self.agents[agent.agent_type] = agent
        logger.info(f"Registered agent: {agent.name} ({agent.agent_type.value})")
    
    def get_agent(self, agent_type: AgentType) -> Optional[Agent]:
        """Get agent by type"""
        return self.agents.get(agent_type)
    
    async def route_query(
        self,
        query: str,
        agent_type: Optional[AgentType] = None,
        history: Optional[List[BaseMessage]] = None
    ) -> Dict[str, Any]:
        """
        Route query to appropriate agent
        
        Args:
            query: User query
            agent_type: Specific agent type (if None, auto-select)
            history: Conversation history
            
        Returns:
            Agent response
        """
        # If specific agent requested, use it
        if agent_type and agent_type in self.agents:
            agent = self.agents[agent_type]
            return await agent.invoke(query, history)
        
        # Auto-select agent based on query
        selected_type = self._select_agent(query)
        agent = self.agents.get(selected_type, self.agents.get(AgentType.GENERAL))
        
        if not agent:
            return {
                "response": "No agent available",
                "success": False,
                "error": "No agent configured"
            }
        
        return await agent.invoke(query, history)
    
    def _select_agent(self, query: str) -> AgentType:
        """Select appropriate agent based on query content"""
        query_lower = query.lower()
        
        # Simple keyword-based routing (can be improved with classification)
        if any(word in query_lower for word in ["search", "research", "find", "lookup", "what is"]):
            return AgentType.RESEARCH
        elif any(word in query_lower for word in ["code", "programming", "function", "debug", "implement"]):
            return AgentType.CODING
        elif any(word in query_lower for word in ["data", "analyze", "statistics", "chart", "graph"]):
            return AgentType.DATA_ANALYSIS
        else:
            return AgentType.GENERAL
    
    def list_agents(self) -> List[Dict[str, str]]:
        """List all registered agents"""
        return [
            {
                "name": agent.name,
                "type": agent.agent_type.value,
                "description": agent.description,
                "tool_count": len(agent.tools)
            }
            for agent in self.agents.values()
        ]


# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()


def get_orchestrator() -> MultiAgentOrchestrator:
    """Get orchestrator instance (for dependency injection)"""
    return orchestrator

