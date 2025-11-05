"""
Prometheus metrics for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

from src.config import settings


class MetricsRegistry:
    """Central metrics registry"""
    
    def __init__(self):
        """Initialize metrics"""
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_count = Counter(
            'mcpagent_requests_total',
            'Total request count',
            ['method', 'endpoint', 'status_code'],
            registry=self.registry
        )
        
        self.request_latency = Histogram(
            'mcpagent_request_latency_seconds',
            'Request latency in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # LLM metrics
        self.llm_requests = Counter(
            'mcpagent_llm_requests_total',
            'Total LLM requests',
            ['provider', 'model', 'status'],
            registry=self.registry
        )
        
        self.llm_tokens = Counter(
            'mcpagent_llm_tokens_total',
            'Total tokens used',
            ['provider', 'model', 'type'],  # type: prompt/completion
            registry=self.registry
        )
        
        self.llm_cost = Counter(
            'mcpagent_llm_cost_usd',
            'Total cost in USD',
            ['provider', 'model'],
            registry=self.registry
        )
        
        self.llm_latency = Histogram(
            'mcpagent_llm_latency_seconds',
            'LLM request latency',
            ['provider', 'model'],
            registry=self.registry
        )
        
        # Agent metrics
        self.agent_executions = Counter(
            'mcpagent_agent_executions_total',
            'Total agent executions',
            ['agent_type', 'status'],
            registry=self.registry
        )
        
        self.tool_calls = Counter(
            'mcpagent_tool_calls_total',
            'Total tool calls',
            ['tool_name', 'status'],
            registry=self.registry
        )
        
        # RAG metrics
        self.rag_queries = Counter(
            'mcpagent_rag_queries_total',
            'Total RAG queries',
            ['status'],
            registry=self.registry
        )
        
        self.rag_retrievals = Histogram(
            'mcpagent_rag_documents_retrieved',
            'Number of documents retrieved',
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'mcpagent_cache_hits_total',
            'Cache hits',
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'mcpagent_cache_misses_total',
            'Cache misses',
            registry=self.registry
        )
        
        # Database metrics
        self.db_queries = Counter(
            'mcpagent_db_queries_total',
            'Database queries',
            ['operation', 'status'],
            registry=self.registry
        )
        
        # Active sessions
        self.active_sessions = Gauge(
            'mcpagent_active_sessions',
            'Number of active sessions',
            registry=self.registry
        )


# Global metrics registry
metrics_registry = MetricsRegistry()

