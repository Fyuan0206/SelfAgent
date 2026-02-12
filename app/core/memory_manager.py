import os
import json
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from datetime import datetime
from loguru import logger
from app.core.agent import SelfAgent  # For summarization if needed

class MemoryManager:
    def __init__(self, persist_path: str = "./data/chroma_db"):
        """Initialize ChromaDB client"""
        self.client = chromadb.PersistentClient(path=persist_path)
        
        # Create or get collection for user memories
        self.collection = self.client.get_or_create_collection(
            name="user_memories",
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_memory(self, user_id: str, content: str, role: str, metadata: Dict[str, Any] = None):
        """Add a new memory entry"""
        if metadata is None:
            metadata = {}
            
        metadata.update({
            "user_id": user_id,
            "role": role,
            "timestamp": datetime.now().isoformat(),
            "type": "conversation"
        })
        
        # ID generation
        memory_id = f"{user_id}_{datetime.now().timestamp()}"
        
        self.collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        logger.info(f"Added memory for user {user_id}: {content[:50]}...")

    def search_memory(self, user_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Semantic search for memories"""
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where={"user_id": user_id}
        )
        
        memories = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                memories.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results["distances"] else 0
                })
        
        return memories

    def get_recent_memories(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get most recent memories (simple retrieval by timestamp not supported natively efficiently in all vector DBs, 
        but we can filter. For now, Chroma doesn't support sort by metadata easily without fetching.
        We will just fetch all and sort python side for this prototype or use a separate SQL/JSON store for history.
        
        Actually, for 'Memory', vector search is the key. 
        For 'History', we should stick to the SQL or JSON file.
        This MemoryManager is for Long Term Memory (RAG).
        """
        # Retrieve random/latest is tricky in Vector DB. 
        # We assume this function is for retrieving CONTEXT based on query.
        pass

    async def compress_and_archive(self, user_id: str, history_messages: List[Dict], agent_instance: Any):
        """
        Compress recent history into a summary and store in vector DB.
        This should be called when session ends or history is too long.
        """
        if not history_messages:
            return

        # Prepare text for summarization
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_messages])
        
        # Use the agent to summarize
        prompt = f"""
        请对以下对话历史进行摘要总结，提取关键信息（用户的偏好、性格特点、主要经历、当前情绪状态）。
        摘要应该简洁明了，便于未来检索。
        
        对话历史:
        {conversation_text}
        
        摘要:
        """
        
        # We need a way to call the LLM. 
        # Since SelfAgent has the LLM client, we can reuse it.
        # But SelfAgent might be complex to instantiate here.
        # We'll assume the caller passes the agent instance or we use a simple call.
        
        try:
            # Simple simulation of agent call if not passed
            # In real impl, we should use the agent's internal LLM
            if hasattr(agent_instance, 'client'):
                response = agent_instance.client.chat.completions.create(
                    model=agent_instance.model_type,
                    messages=[{"role": "user", "content": prompt}]
                )
                summary = response.choices[0].message.content
            else:
                summary = "无法生成摘要 (Agent未初始化)"
                
            # Store summary in Vector DB
            self.add_memory(
                user_id=user_id,
                content=summary,
                role="system",
                metadata={"type": "summary", "original_msg_count": len(history_messages)}
            )
            logger.info(f"Compressed memory for {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to compress memory: {e}")
            return None
