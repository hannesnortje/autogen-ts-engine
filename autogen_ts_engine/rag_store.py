"""RAG (Retrieval-Augmented Generation) store using ChromaDB."""

import hashlib
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

from .schemas import RAGConfig


class RAGStore:
    """RAG store for semantic search and context retrieval."""
    
    def __init__(self, vector_db_path: str, config: RAGConfig):
        self.config = config
        self.vector_db_path = Path(vector_db_path)
        self.vector_db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.vector_db_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize sentence transformer
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="project_docs",
            metadata={"description": "Project documentation and code snippets"}
        )
        
        # Track indexed files to avoid re-indexing
        self.indexed_files = set()
    
    def index_directory(self, directory: Path, file_patterns: Optional[List[str]] = None) -> None:
        """Index all files in a directory."""
        if file_patterns is None:
            file_patterns = ["*.ts", "*.js", "*.md", "*.txt", "*.json"]
        
        for pattern in file_patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file() and not self._should_skip_file(file_path):
                    self.index_file(file_path)
    
    def index_file(self, file_path: Path) -> None:
        """Index a single file."""
        if file_path in self.indexed_files:
            return
        
        try:
            content = file_path.read_text(encoding='utf-8')
            if not content.strip():
                return
            
            # Chunk the content
            chunks = self._chunk_content(content, file_path)
            
            # Add chunks to collection
            for i, chunk in enumerate(chunks):
                chunk_id = f"{file_path.name}_{i}_{self._hash_content(chunk)}"
                metadata = {
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "chunk_index": i,
                    "file_type": file_path.suffix
                }
                
                self.collection.add(
                    documents=[chunk],
                    metadatas=[metadata],
                    ids=[chunk_id]
                )
            
            self.indexed_files.add(file_path)
            
        except Exception as e:
            print(f"Failed to index {file_path}: {e}")
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """Retrieve relevant documents for a query."""
        if top_k is None:
            top_k = self.config.top_k
        
        try:
            # Query the collection
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k
            )
            
            # Format results
            documents = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    documents.append({
                        'content': doc,
                        'metadata': metadata,
                        'distance': results['distances'][0][i] if results['distances'] else 0.0
                    })
            
            return documents
            
        except Exception as e:
            print(f"Failed to retrieve documents: {e}")
            return []
    
    def retrieve_with_context(self, query: str, context: str = "", top_k: Optional[int] = None) -> str:
        """Retrieve documents and format them as context for LLM."""
        documents = self.retrieve(query, top_k)
        
        if not documents:
            return ""
        
        # Format context
        context_parts = []
        if context:
            context_parts.append(f"Current context: {context}")
        
        context_parts.append("Relevant documentation:")
        
        for i, doc in enumerate(documents):
            metadata = doc['metadata']
            file_name = metadata.get('file_name', 'unknown')
            context_parts.append(f"\n--- {file_name} ---\n{doc['content']}")
        
        return "\n".join(context_parts)
    
    def summarize_conversation(self, messages: List[Dict]) -> str:
        """Summarize a conversation for context."""
        if not messages:
            return ""
        
        # Extract key information from messages
        summary_parts = []
        
        for msg in messages[-5:]:  # Last 5 messages
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                summary_parts.append(f"User asked: {content[:100]}...")
            elif role == 'assistant':
                summary_parts.append(f"Assistant responded: {content[:100]}...")
        
        return "Recent conversation:\n" + "\n".join(summary_parts)
    
    def clear_index(self) -> None:
        """Clear the entire index."""
        self.client.delete_collection("project_docs")
        self.collection = self.client.create_collection(
            name="project_docs",
            metadata={"description": "Project documentation and code snippets"}
        )
        self.indexed_files.clear()
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the index."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "indexed_files": len(self.indexed_files),
                "collection_name": self.collection.name
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _chunk_content(self, content: str, file_path: Path) -> List[str]:
        """Split content into chunks."""
        chunks = []
        
        # Different chunking strategies based on file type
        if file_path.suffix in ['.ts', '.js']:
            chunks = self._chunk_code(content)
        elif file_path.suffix == '.md':
            chunks = self._chunk_markdown(content)
        else:
            chunks = self._chunk_text(content)
        
        # Filter out empty chunks and limit size
        filtered_chunks = []
        for chunk in chunks:
            chunk = chunk.strip()
            if chunk and len(chunk) <= self.config.max_doc_tokens * 4:  # Rough token estimate
                filtered_chunks.append(chunk)
        
        return filtered_chunks
    
    def _chunk_code(self, content: str) -> List[str]:
        """Chunk code by functions, classes, and logical blocks."""
        chunks = []
        
        # Split by function/class definitions
        lines = content.split('\n')
        current_chunk = []
        
        for line in lines:
            current_chunk.append(line)
            
            # Check for function/class boundaries
            if (re.match(r'^\s*(export\s+)?(function|class|interface|type|const|let|var)\s+', line) and 
                current_chunk and len(current_chunk) > 5):
                
                chunks.append('\n'.join(current_chunk[:-1]))
                current_chunk = [line]
        
        # Add remaining content
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks
    
    def _chunk_markdown(self, content: str) -> List[str]:
        """Chunk markdown by headers and sections."""
        chunks = []
        
        # Split by headers
        sections = re.split(r'^#{1,6}\s+', content, flags=re.MULTILINE)
        
        for section in sections:
            if section.strip():
                chunks.append(section.strip())
        
        return chunks
    
    def _chunk_text(self, content: str) -> List[str]:
        """Chunk text by paragraphs and sentences."""
        chunks = []
        
        # Split by paragraphs
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            if paragraph.strip():
                chunks.append(paragraph.strip())
        
        return chunks
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped during indexing."""
        skip_patterns = [
            r'node_modules',
            r'\.git',
            r'\.env',
            r'package-lock\.json',
            r'yarn\.lock',
            r'pnpm-lock\.yaml',
            r'\.log$',
            r'\.tmp$',
            r'\.cache$'
        ]
        
        file_str = str(file_path)
        return any(re.search(pattern, file_str) for pattern in skip_patterns)
    
    def _hash_content(self, content: str) -> str:
        """Create a hash of content for ID generation."""
        return hashlib.md5(content.encode()).hexdigest()[:8]
