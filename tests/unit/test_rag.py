"""
Unit tests for RAG system
"""

import pytest
from unittest.mock import Mock, patch

from src.core.rag import EnhancedRAGSystem


class TestEnhancedRAGSystem:
    """Test RAG system functionality"""
    
    @pytest.fixture
    def rag_system(self):
        """Create RAG system instance"""
        with patch('src.core.rag.enhanced_rag.OpenAIEmbeddings'):
            with patch('src.core.rag.enhanced_rag.Chroma'):
                rag = EnhancedRAGSystem()
                return rag
    
    def test_initialization(self, rag_system):
        """Test RAG system initializes correctly"""
        assert rag_system is not None
    
    @pytest.mark.asyncio
    async def test_add_text(self, rag_system):
        """Test adding text to vector store"""
        texts = ["Test document 1", "Test document 2"]
        
        with patch.object(rag_system, 'add_documents') as mock_add:
            mock_add.return_value = {"success": True, "chunks_created": 2}
            result = await rag_system.add_text(texts)
            
            assert result["success"] is True
            assert mock_add.called
    
    def test_retrieve(self, rag_system):
        """Test document retrieval"""
        with patch.object(rag_system, 'retriever') as mock_retriever:
            mock_retriever.invoke.return_value = [Mock(page_content="Test")]
            
            docs = rag_system.retrieve("test query")
            
            assert len(docs) > 0
            mock_retriever.invoke.assert_called_once()
    
    def test_get_collection_stats(self, rag_system):
        """Test getting collection statistics"""
        with patch.object(rag_system, 'vector_store'):
            stats = rag_system.get_collection_stats()
            
            assert "available" in stats

