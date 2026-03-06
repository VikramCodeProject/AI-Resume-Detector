"""
Vector Database Integration
Semantic Resume Similarity Detection & Plagiarism Detection
Pinecone/Weaviate Support
"""

from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from logging import getLogger
import numpy as np
from functools import lru_cache
import os

logger = getLogger(__name__)


class EmbeddingConfig(BaseModel):
    """Embedding configuration"""
    
    model_name: str = "all-MiniLM-L6-v2"
    model_dimension: int = 384
    max_text_length: int = 512


class SimilarResume(BaseModel):
    """Similar resume result"""
    
    resume_id: str
    similarity_score: float
    candidate_name: str
    job_title: str


class PlagiarismResult(BaseModel):
    """Plagiarism detection result"""
    
    plagiarism_score: float
    similar_resumes: List[SimilarResume]
    ai_generated_risk: float
    recommendation: str


class EmbeddingManager:
    """
    Embedding Manager
    Converts resume text to vector embeddings using SentenceTransformers
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding manager
        
        Args:
            model_name: SentenceTransformer model name
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            self.dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded embedding model: {model_name} (dimension: {self.dimension})")
        except ImportError as e:
            logger.error(f"sentence-transformers not installed: {str(e)}")
            raise
    
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for text
        
        Args:
            text: Resume text to embed
            
        Returns:
            Embedding vector (float list)
        """
        try:
            # Truncate to max length
            text = text[:512]
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for batch of texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            texts = [t[:512] for t in texts]  # Truncate
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Batch embedding error: {str(e)}")
            raise


class VectorDatabaseClient:
    """
    Abstract Vector Database Client
    Supports Pinecone and Weaviate
    """
    
    def __init__(self, provider: str = "pinecone"):
        """
        Initialize vector DB client
        
        Args:
            provider: "pinecone" or "weaviate"
        """
        self.provider = provider
        self.client = None
    
    def index(self, resume_id: str, embedding: List[float], metadata: Dict) -> None:
        """Store embedding in vector DB"""
        raise NotImplementedError
    
    def search(self, query_embedding: List[float], top_k: int = 10) -> List[Dict]:
        """Search for similar embeddings"""
        raise NotImplementedError
    
    def delete(self, resume_id: str) -> None:
        """Delete embedding from vector DB"""
        raise NotImplementedError


class PineconeClient(VectorDatabaseClient):
    """
    Pinecone Vector Database Client
    """
    
    def __init__(self, api_key: str = None, index_name: str = "resume-verification"):
        """
        Initialize Pinecone client
        
        Args:
            api_key: Pinecone API key
            index_name: Index name
        """
        super().__init__(provider="pinecone")
        
        try:
            import pinecone
            
            api_key = api_key or os.getenv("PINECONE_API_KEY")
            environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
            
            pinecone.init(api_key=api_key, environment=environment)
            self.index = pinecone.Index(index_name)
            
            logger.info(f"Connected to Pinecone index: {index_name}")
        except ImportError:
            logger.error("pinecone not installed")
            raise
        except Exception as e:
            logger.error(f"Pinecone initialization error: {str(e)}")
            raise
    
    def index_resume(self, resume_id: str, embedding: List[float], metadata: Dict) -> None:
        """
        Index resume embedding in Pinecone
        
        Args:
            resume_id: Unique resume ID
            embedding: Embedding vector
            metadata: Additional metadata
        """
        try:
            self.index.upsert(
                vectors=[
                    (
                        resume_id,
                        embedding,
                        {
                            "resume_id": resume_id,
                            "candidate_name": metadata.get("candidate_name"),
                            "job_title": metadata.get("job_title"),
                            "company": metadata.get("company"),
                            "timestamp": metadata.get("timestamp")
                        }
                    )
                ]
            )
            logger.info(f"Indexed resume {resume_id} in Pinecone")
        except Exception as e:
            logger.error(f"Pinecone indexing error: {str(e)}")
            raise
    
    def search_similar(self, query_embedding: List[float], top_k: int = 10) -> List[Tuple[str, float]]:
        """
        Search for similar resumes
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (resume_id, similarity_score) tuples
        """
        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            similar = [
                (match.id, match.score)
                for match in results['matches']
            ]
            
            logger.debug(f"Found {len(similar)} similar resumes")
            return similar
        except Exception as e:
            logger.error(f"Pinecone search error: {str(e)}")
            raise
    
    def delete_resume(self, resume_id: str) -> None:
        """Delete resume from index"""
        try:
            self.index.delete(ids=[resume_id])
            logger.info(f"Deleted resume {resume_id} from Pinecone")
        except Exception as e:
            logger.error(f"Pinecone deletion error: {str(e)}")
            raise


class ResumeVectorService:
    """
    Resume Vector Search Service
    Coordinates embedding generation, storage, and similarity detection
    """
    
    def __init__(
        self,
        vector_provider: str = "pinecone",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector service
        
        Args:
            vector_provider: "pinecone" or "weaviate"
            embedding_model: SentenceTransformer model
        """
        self.embedding_manager = EmbeddingManager(embedding_model)
        
        if vector_provider == "pinecone":
            self.vector_db = PineconeClient()
        else:
            raise ValueError(f"Unsupported vector provider: {vector_provider}")
    
    def index_resume(
        self,
        resume_id: str,
        resume_text: str,
        candidate_name: str,
        job_title: str,
        company: str = None,
        timestamp: str = None
    ) -> None:
        """
        Index resume for similarity search
        
        Args:
            resume_id: Unique resume ID
            resume_text: Full resume text
            candidate_name: Candidate name
            job_title: Job title
            company: Company name
            timestamp: Upload timestamp
        """
        try:
            # Generate embedding
            embedding = self.embedding_manager.embed(resume_text)
            
            # Store in vector DB
            metadata = {
                "candidate_name": candidate_name,
                "job_title": job_title,
                "company": company,
                "timestamp": timestamp
            }
            
            self.vector_db.index_resume(resume_id, embedding, metadata)
            logger.info(f"Resume {resume_id} indexed for similarity search")
            
        except Exception as e:
            logger.error(f"Resume indexing error: {str(e)}")
            raise
    
    def detect_plagiarism(
        self,
        resume_text: str,
        similarity_threshold: float = 0.85
    ) -> PlagiarismResult:
        """
        Detect plagiarism by finding similar resumes
        
        Args:
            resume_text: Resume text to check
            similarity_threshold: Plagiarism threshold (0-1)
            
        Returns:
            PlagiarismResult with details
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_manager.embed(resume_text)
            
            # Search for similar resumes
            similar_results = self.vector_db.search_similar(query_embedding, top_k=15)
            
            # Filter by threshold
            plagiarism_score = 0.0
            similar_resumes = []
            
            for resume_id, similarity in similar_results:
                if similarity >= similarity_threshold:
                    plagiarism_score = max(plagiarism_score, similarity)
                    similar_resumes.append(SimilarResume(
                        resume_id=resume_id,
                        similarity_score=float(similarity),
                        candidate_name="",
                        job_title=""
                    ))
            
            # Calculate AI-generated risk based on similarity patterns
            ai_risk = self._calculate_ai_generated_risk(similar_results)
            
            # Generate recommendation
            if plagiarism_score >= 0.95:
                recommendation = "CRITICAL: Likely plagiarized or AI-generated"
            elif plagiarism_score >= 0.85:
                recommendation = "HIGH: Suspicious similarity detected"
            elif plagiarism_score >= 0.70:
                recommendation = "MEDIUM: Some similarity detected, review required"
            else:
                recommendation = "LOW: Appears authentic"
            
            return PlagiarismResult(
                plagiarism_score=plagiarism_score,
                similar_resumes=similar_resumes,
                ai_generated_risk=ai_risk,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Plagiarism detection error: {str(e)}")
            raise
    
    def _calculate_ai_generated_risk(self, similarity_results: List[Tuple[str, float]]) -> float:
        """
        Calculate AI-generated resume risk
        AI-generated resumes tend to have unusual similarity patterns
        
        Args:
            similarity_results: List of (id, score) tuples from search
            
        Returns:
            Risk score 0-1
        """
        if not similarity_results:
            return 0.0
        
        scores = [s for _, s in similarity_results[:10]]
        
        # High risk if too many high-similarity matches (= template-like)
        high_similarity_count = sum(1 for s in scores if s > 0.8)
        
        # Calculate risk
        if high_similarity_count >= 5:
            risk = min(0.9, high_similarity_count * 0.15)
        else:
            risk = 0.0
        
        return risk
    
    def find_similar_resumes(
        self,
        resume_text: str,
        top_k: int = 10
    ) -> List[SimilarResume]:
        """
        Find similar resumes
        
        Args:
            resume_text: Query resume text
            top_k: Number of results to return
            
        Returns:
            List of similar resumes
        """
        try:
            query_embedding = self.embedding_manager.embed(resume_text)
            similar_results = self.vector_db.search_similar(query_embedding, top_k=top_k)
            
            results = [
                SimilarResume(
                    resume_id=resume_id,
                    similarity_score=float(score),
                    candidate_name="",
                    job_title=""
                )
                for resume_id, score in similar_results
            ]
            
            return results
            
        except Exception as e:
            logger.error(f"Similar resume search error: {str(e)}")
            raise


@lru_cache()
def get_vector_service() -> ResumeVectorService:
    """Get vector service singleton"""
    return ResumeVectorService()
