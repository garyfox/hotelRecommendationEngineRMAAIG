"""
Vector storage functionality for the hotel recommendation system.
"""
import os
import json
import uuid
import faiss
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from config import VECTOR_CONFIG, DATA_DIR


class VectorStore:
    """
    Manages storage and retrieval of vector embeddings.
    """

    def __init__(self):
        """Initialize the vector store."""
        self.vector_dim = VECTOR_CONFIG["vector_dimension"]
        self.db_path = Path(VECTOR_CONFIG["vector_db_path"])
        self.metadata_path = self.db_path / "metadata.json"

        # Create storage directory if it doesn't exist
        self.db_path.mkdir(exist_ok=True, parents=True)

        # Initialize or load the index
        self._index = self._load_or_create_index()

        # Initialize or load metadata
        self._metadata = self._load_or_create_metadata()

    def _load_or_create_index(self) -> faiss.IndexFlatIP:
        """
        Load the FAISS index or create a new one if it doesn't exist.

        Returns:
            faiss.IndexFlatIP: The FAISS index
        """
        index_path = self.db_path / "index.faiss"

        if index_path.exists():
            try:
                index = faiss.read_index(str(index_path))
                return index
            except Exception as e:
                print(f"Error loading index: {str(e)}. Creating new index.")

        # Create a new index for inner product (cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(self.vector_dim)
        return index

    def _load_or_create_metadata(self) -> Dict[str, Dict[str, Any]]:
        """
        Load metadata or create new metadata if it doesn't exist.

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary mapping vector IDs to metadata
        """
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading metadata: {str(e)}. Creating new metadata.")

        return {}

    def store(self, vector: np.ndarray, metadata: Dict[str, Any] = None) -> str:
        """
        Store a vector with optional metadata.

        Args:
            vector: The vector to store
            metadata: Optional metadata to associate with the vector

        Returns:
            str: The ID of the stored vector
        """
        # Generate a unique ID
        vector_id = str(uuid.uuid4())

        # Ensure vector is a numpy array with the right shape
        vector = np.array(vector).astype('float32').reshape(1, -1)

        # Add to the index
        self._index.add(vector)

        # Store metadata
        if metadata is None:
            metadata = {}

        # Get the index of the added vector
        vector_index = self._index.ntotal - 1

        # Store metadata with both ID and index for retrieval
        self._metadata[vector_id] = {
            **metadata,
            "_index": vector_index,
        }

        # Save the index and metadata
        self._save()

        return vector_id

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
        """
        Search for similar vectors.

        Args:
            query_vector: The query vector
            top_k: Number of results to return

        Returns:
            List[Tuple[str, float, Dict[str, Any]]]: List of (id, similarity, metadata) tuples
        """
        # Ensure query vector is a numpy array with the right shape
        query_vector = np.array(query_vector).astype('float32').reshape(1, -1)

        # Search in the index
        scores, indices = self._index.search(query_vector, top_k)

        # Get the metadata for the search results
        results = []

        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            # Skip if no valid index
            if idx == -1:
                continue

            # Find the vector ID with this index
            vector_id = None
            for vid, meta in self._metadata.items():
                if meta.get("_index") == idx:
                    vector_id = vid
                    break

            if vector_id is not None:
                # Clone metadata dict and remove internal fields
                metadata = self._metadata[vector_id].copy()
                if "_index" in metadata:
                    del metadata["_index"]

                results.append((vector_id, float(score), metadata))

        return results

    def get(self, vector_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a vector by ID.

        Args:
            vector_id: The ID of the vector

        Returns:
            Optional[Dict[str, Any]]: The metadata or None if not found
        """
        if vector_id in self._metadata:
            # Clone metadata dict and remove internal fields
            metadata = self._metadata[vector_id].copy()
            if "_index" in metadata:
                del metadata["_index"]

            return metadata

        return None

    def _save(self) -> None:
        """Save the index and metadata to disk."""
        # Save the index
        index_path = self.db_path / "index.faiss"
        faiss.write_index(self._index, str(index_path))

        # Save the metadata
        with open(self.metadata_path, 'w') as f:
            json.dump(self._metadata, f)


# Singleton instance
_store = None


def get_vector_store() -> VectorStore:
    """
    Get the vector store instance.

    Returns:
        VectorStore: The vector store
    """
    global _store

    if _store is None:
        _store = VectorStore()

    return _store


def store_vector(question_id: str, vector: np.ndarray) -> str:
    """
    Store a vector with question ID as metadata.

    Args:
        question_id: The ID of the question
        vector: The vector to store

    Returns:
        str: The ID of the stored vector
    """
    store = get_vector_store()

    metadata = {
        "question_id": question_id,
        "timestamp": str(uuid.uuid1()),  # Includes timestamp
    }

    vector_id = store.store(vector, metadata)
    return vector_id


def search_vectors(query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[str, float, Dict[str, Any]]]:
    """
    Search for similar vectors.

    Args:
        query_vector: The query vector
        top_k: Number of results to return

    Returns:
        List[Tuple[str, float, Dict[str, Any]]]: List of (id, similarity, metadata) tuples
    """
    store = get_vector_store()
    return store.search(query_vector, top_k)
