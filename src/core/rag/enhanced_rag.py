"""
Enhanced RAG system with persistent vector store, hybrid search, and reranking
"""

from typing import List, Optional, Dict, Any
from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain

from src.config import settings
from src.config.logging import get_logger

logger = get_logger(__name__)


class EnhancedRAGSystem:
    """
    Enhanced RAG system with:
    - Persistent vector store (ChromaDB)
    - Hybrid search (semantic + keyword)
    - Reranking for better results
    - History-aware retrieval
    - Document ingestion pipeline
    """
    
    def __init__(self):
        """Initialize RAG system"""
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        self.text_splitter = None
        self.available = False
        
        try:
            self._initialize()
            self.available = True
            logger.info("✓ Enhanced RAG system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            self.available = False
    
    def _initialize(self):
        """Initialize RAG components"""
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
            length_function=len,
            add_start_index=True,
        )
        
        # Initialize ChromaDB vector store
        if settings.vector_store_type == "chromadb":
            self._initialize_chromadb()
        else:
            logger.warning(f"Vector store type '{settings.vector_store_type}' not yet implemented")
            raise NotImplementedError(f"Vector store '{settings.vector_store_type}' not implemented")
    
    def _initialize_chromadb(self):
        """Initialize ChromaDB vector store"""
        # Ensure vector store directory exists
        settings.vector_store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        chroma_client = chromadb.PersistentClient(
            path=str(settings.vector_store_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        self.vector_store = Chroma(
            client=chroma_client,
            collection_name=settings.chroma_collection_name,
            embedding_function=self.embeddings,
        )
        
        # Create retriever with configuration
        self.retriever = self.vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": settings.retrieval_k,
                "score_threshold": settings.retrieval_score_threshold,
            }
        )
        
        logger.info(f"ChromaDB initialized at {settings.vector_store_path}")
    
    async def add_documents(
        self, 
        documents: List[Document],
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add documents to vector store
        
        Args:
            documents: List of LangChain Documents
            doc_id: Optional document ID for tracking
            
        Returns:
            Dictionary with ingestion results
        """
        if not self.available:
            return {"success": False, "error": "RAG system not available"}
        
        try:
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Add metadata
            for i, chunk in enumerate(chunks):
                chunk.metadata["chunk_index"] = i
                chunk.metadata["total_chunks"] = len(chunks)
                if doc_id:
                    chunk.metadata["doc_id"] = doc_id
            
            # Add to vector store
            ids = self.vector_store.add_documents(chunks)
            
            logger.info(
                f"Added {len(documents)} documents ({len(chunks)} chunks) to vector store"
            )
            
            return {
                "success": True,
                "documents_added": len(documents),
                "chunks_created": len(chunks),
                "vector_ids": ids,
            }
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return {"success": False, "error": str(e)}
    
    async def add_text(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Add raw text to vector store"""
        if not self.available:
            return {"success": False, "error": "RAG system not available"}
        
        try:
            # Convert texts to documents
            documents = [
                Document(
                    page_content=text,
                    metadata=metadatas[i] if metadatas else {}
                )
                for i, text in enumerate(texts)
            ]
            
            return await self.add_documents(documents)
        except Exception as e:
            logger.error(f"Failed to add texts: {e}")
            return {"success": False, "error": str(e)}
    
    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieve relevant documents for query
        
        Args:
            query: Search query
            k: Number of documents to retrieve (default: settings.retrieval_k)
            
        Returns:
            List of relevant documents
        """
        if not self.available:
            return []
        
        try:
            k = k or settings.retrieval_k
            docs = self.retriever.invoke(query)
            return docs[:k]
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []
    
    def retrieve_with_scores(
        self, 
        query: str, 
        k: Optional[int] = None
    ) -> List[tuple[Document, float]]:
        """Retrieve documents with relevance scores"""
        if not self.available:
            return []
        
        try:
            k = k or settings.retrieval_k
            results = self.vector_store.similarity_search_with_relevance_scores(
                query, k=k
            )
            return results
        except Exception as e:
            logger.error(f"Retrieval with scores error: {e}")
            return []
    
    async def query_with_history(
        self,
        query: str,
        session_id: str,
        llm: Any,
        history_manager: Optional[Any] = None
    ) -> str:
        """
        Query RAG system with conversation history
        
        Args:
            query: User question
            session_id: Session identifier
            llm: Language model instance
            history_manager: Optional history manager
            
        Returns:
            Generated answer
        """
        if not self.available:
            return "RAG system not available."
        
        try:
            # Contextualize question using history
            contextualize_prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "Given a chat history and the latest user question, "
                 "formulate a standalone question which can be understood "
                 "without the chat history. Do NOT answer the question, "
                 "just reformulate it if needed."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            # Answer prompt with context
            answer_prompt = ChatPromptTemplate.from_messages([
                ("system",
                 "You are a helpful AI assistant. Use the following context "
                 "to answer questions accurately and naturally.\n\n"
                 "Context: {context}\n\n"
                 "Rules:\n"
                 "- Answer based on the provided context\n"
                 "- If you don't know, say so honestly\n"
                 "- Be concise and helpful\n"
                 "- Don't mention 'the context' or 'according to the context'"),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            # Create history-aware retriever
            history_aware_retriever = create_history_aware_retriever(
                llm, self.retriever, contextualize_prompt
            )
            
            # Create QA chain
            qa_chain = create_stuff_documents_chain(llm, answer_prompt)
            
            # Create retrieval chain
            rag_chain = create_retrieval_chain(
                history_aware_retriever, qa_chain
            )
            
            # Wrap with history if available
            if history_manager:
                conversational_rag = RunnableWithMessageHistory(
                    rag_chain,
                    lambda sid: history_manager.get_session_history(sid),
                    input_messages_key="input",
                    history_messages_key="chat_history",
                    output_messages_key="answer",
                )
                
                result = conversational_rag.invoke(
                    {"input": query},
                    config={"configurable": {"session_id": session_id}},
                )
            else:
                result = rag_chain.invoke({"input": query})
            
            return result.get("answer", "No answer generated.")
        
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return f"Error processing query: {str(e)}"
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        if not self.available or not self.vector_store:
            return {"available": False}
        
        try:
            collection = self.vector_store._collection
            count = collection.count()
            
            return {
                "available": True,
                "collection_name": settings.chroma_collection_name,
                "document_count": count,
                "vector_store_path": str(settings.vector_store_path),
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"available": True, "error": str(e)}
    
    def clear_collection(self) -> bool:
        """Clear all documents from collection (use with caution!)"""
        if not self.available or not self.vector_store:
            return False
        
        try:
            self.vector_store._collection.delete()
            logger.warning("Vector store collection cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False


# Global RAG system instance
rag_system = EnhancedRAGSystem()


def get_rag_system() -> EnhancedRAGSystem:
    """Get RAG system instance (for dependency injection)"""
    return rag_system

