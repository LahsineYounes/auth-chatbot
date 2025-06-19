import uuid
from typing import List, Dict, Optional, Any

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Distance, VectorParams, CollectionInfo, ScoredPoint
# For older versions, it might be from qdrant_client.http.models for some of these

class VectorDBManager:
    """
    Manages interactions with a Qdrant vector database.
    """
    def __init__(self, host: str = "qdrant_db", grpc_port: int = 6333, http_port: int = 6334, api_key: Optional[str] = None):
        """
        Initializes the QdrantClient.

        Args:
            host (str): Hostname of the Qdrant instance.
            grpc_port (int): gRPC port of the Qdrant instance.
            http_port (int): HTTP port of the Qdrant instance (for potential REST fallbacks or alternative connections).
            api_key (Optional[str]): API key for Qdrant Cloud (if applicable).
        """
        self.host = host
        self.grpc_port = grpc_port # QdrantClient uses gRPC by default if host and port are given
        self.http_port = http_port
        self.client: Optional[QdrantClient] = None

        try:
            # For QdrantClient, providing host and port implies gRPC.
            # For HTTP, one might use url=f"http://{host}:{http_port}"
            # For Qdrant Cloud, api_key and url (e.g., cloud_url) would be used.
            self.client = QdrantClient(host=self.host, port=self.grpc_port, api_key=api_key)
            # Perform a simple operation to confirm connectivity, e.g., list collections
            self.client.get_collections()
            print(f"Successfully connected to Qdrant at {self.host}:{self.grpc_port} (gRPC).")
        except Exception as e:
            print(f"Error connecting to Qdrant at {self.host}:{self.grpc_port} (gRPC): {e}")
            print(f"Attempting connection via HTTP on port {self.http_port} as a fallback/alternative...")
            try:
                self.client = QdrantClient(url=f"http://{self.host}:{self.http_port}", api_key=api_key)
                self.client.get_collections() # Test HTTP connection
                print(f"Successfully connected to Qdrant at {self.host}:{self.http_port} (HTTP).")
            except Exception as e_http:
                print(f"Error connecting to Qdrant via HTTP on {self.host}:{self.http_port}: {e_http}")
                self.client = None # Ensure client is None if connection failed

    def create_collection_if_not_exists(self, collection_name: str, vector_size: int, distance_metric: Distance = Distance.COSINE) -> bool:
        """
        Creates a Qdrant collection if it doesn't already exist.

        Args:
            collection_name (str): Name of the collection.
            vector_size (int): Dimension of the vectors to be stored.
            distance_metric (Distance): Distance metric for vector comparison (default: COSINE).

        Returns:
            bool: True if collection was created or already exists and is valid, False otherwise.
        """
        if not self.client:
            print("Qdrant client not initialized. Cannot create collection.")
            return False
        try:
            collections_response = self.client.get_collections()
            existing_collections = [col_desc.name for col_desc in collections_response.collections]

            if collection_name in existing_collections:
                print(f"Collection '{collection_name}' already exists.")
                # Optionally, verify if the existing collection has the correct vector_size and distance
                # coll_info = self.client.get_collection(collection_name)
                # if coll_info.config.params.vectors.size != vector_size or coll_info.config.params.vectors.distance != distance_metric:
                # print(f"Warning: Collection '{collection_name}' exists but has different configuration.")
                # return False # Or handle as an error/update strategy
                return True

            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=distance_metric)
            )
            print(f"Collection '{collection_name}' created successfully with vector size {vector_size} and {distance_metric} distance.")
            return True
        except Exception as e:
            print(f"Error creating or checking collection '{collection_name}': {e}")
            return False

    def ingest_points(self, collection_name: str, vectors: List[List[float]], payloads: List[Optional[Dict[str, Any]]], ids: Optional[List[Any]] = None) -> bool:
        """
        Ingests (upserts) points (vectors and their payloads) into the specified collection.

        Args:
            collection_name (str): Name of the collection.
            vectors (List[List[float]]): List of vector embeddings.
            payloads (List[Optional[Dict[str, Any]]]): List of payloads (metadata) for each vector.
            ids (Optional[List[Any]]): Optional list of IDs for each point. If None, UUIDs are generated.

        Returns:
            bool: True if points were successfully upserted, False otherwise.
        """
        if not self.client:
            print("Qdrant client not initialized. Cannot ingest points.")
            return False
        if not vectors:
            print("No vectors provided for ingestion.")
            return False
        if len(vectors) != len(payloads):
            print("Mismatch between number of vectors and payloads.")
            return False

        point_ids: List[Any]
        if ids:
            if len(ids) != len(vectors):
                print("Mismatch between number of provided IDs and vectors.")
                return False
            point_ids = ids
        else:
            point_ids = [uuid.uuid4().hex for _ in vectors]

        points_to_upsert = [
            PointStruct(id=id_val, vector=vector, payload=payload if payload is not None else {})
            for id_val, vector, payload in zip(point_ids, vectors, payloads)
        ]

        try:
            self.client.upsert(collection_name=collection_name, points=points_to_upsert, wait=True)
            print(f"Successfully upserted {len(points_to_upsert)} points into '{collection_name}'.")
            return True
        except Exception as e:
            print(f"Error upserting points into '{collection_name}': {e}")
            return False

    def search(self, collection_name: str, query_vector: List[float], limit: int = 5, score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Performs a similarity search in the specified collection.

        Args:
            collection_name (str): Name of the collection.
            query_vector (List[float]]): The vector to search for.
            limit (int): Maximum number of results to return.
            score_threshold (Optional[float]): Minimum score threshold for results.

        Returns:
            List[Dict[str, Any]]: A list of search results, each as a dictionary.
        """
        if not self.client:
            print("Qdrant client not initialized. Cannot perform search.")
            return []
        try:
            search_result: List[ScoredPoint] = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )

            transformed_results = [
                {"id": hit.id, "score": hit.score, "payload": hit.payload, "vector": hit.vector}
                for hit in search_result
            ]
            return transformed_results
        except Exception as e:
            print(f"Error searching in collection '{collection_name}': {e}")
            return []

    def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves information about a specific collection.

        Args:
            collection_name (str): Name of the collection.

        Returns:
            Optional[Dict[str, Any]]: Dictionary with collection info, or None if error.
        """
        if not self.client:
            print("Qdrant client not initialized. Cannot get collection info.")
            return None
        try:
            collection_info: CollectionInfo = self.client.get_collection(collection_name=collection_name)
            # Convert CollectionInfo to a dictionary for easier use, if needed
            # For now, returning the object itself or specific parts might be fine
            # Example: return collection_info.dict() if using Pydantic models directly
            return {
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count,
                "points_count": collection_info.points_count,
                "segments_count": collection_info.segments_count,
                "config": {
                    "params": {
                        "vectors": {
                            "size": collection_info.config.params.vectors.size,
                            "distance": collection_info.config.params.vectors.distance.value # Use .value for Enum
                        }
                    },
                    "hnsw_config": collection_info.config.hnsw_config.dict() if collection_info.config.hnsw_config else None,
                    "optimizer_config": collection_info.config.optimizer_config.dict() if collection_info.config.optimizer_config else None,
                    "wal_config": collection_info.config.wal_config.dict() if collection_info.config.wal_config else None,
                },
                "payload_schema": collection_info.payload_schema
            }

        except Exception as e:
            print(f"Error getting info for collection '{collection_name}': {e}")
            return None

    def delete_collection(self, collection_name: str) -> bool:
        """
        Deletes a collection. (Use with caution)

        Args:
            collection_name (str): Name of the collection to delete.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        if not self.client:
            print("Qdrant client not initialized. Cannot delete collection.")
            return False
        try:
            self.client.delete_collection(collection_name=collection_name)
            print(f"Collection '{collection_name}' deleted successfully.")
            return True
        except Exception as e:
            print(f"Error deleting collection '{collection_name}': {e}")
            return False

if __name__ == '__main__':
    print("----- Testing VectorDBManager -----")
    # Assuming Qdrant is running on localhost via Docker as 'qdrant_db'
    # For local direct script testing, you might use host="localhost" if qdrant is directly accessible
    # When run from within the chatbot-service container, "qdrant_db" should resolve.
    db_manager = VectorDBManager(host="localhost") # Use "localhost" for local script test, "qdrant_db" for in-container

    if db_manager.client:
        test_collection_name = "test_collection_123"
        test_vector_size = 10  # Small dimension for testing

        print(f"\n1. Attempting to create collection '{test_collection_name}' with vector size {test_vector_size}.")
        created = db_manager.create_collection_if_not_exists(test_collection_name, test_vector_size)
        if created:
            print(f"Collection '{test_collection_name}' ready.")
        else:
            print(f"Failed to ensure collection '{test_collection_name}' is ready. Aborting further tests for this collection.")
            # Attempt to clean up if creation failed but somehow collection exists partially
            db_manager.delete_collection(test_collection_name)


        if created: # Proceed only if collection creation was successful
            print("\n2. Getting collection info:")
            info = db_manager.get_collection_info(test_collection_name)
            if info:
                print(f"Info for '{test_collection_name}': Points count = {info.get('points_count')}")
            else:
                print(f"Could not get info for '{test_collection_name}'.")

            print("\n3. Ingesting points:")
            sample_vectors = [[float(i) for i in range(test_vector_size)] for _ in range(3)] # 3 sample vectors
            sample_vectors[0][0] = 1.1 # Make them slightly different
            sample_vectors[1][1] = 2.2
            sample_vectors[2][2] = 3.3
            sample_payloads = [
                {"text": "This is document 1 about apples.", "source": "doc_A"},
                {"text": "Document 2 is about bananas.", "source": "doc_B"},
                {"text": "The third document discusses carrots and apples.", "source": "doc_C"}
            ]
            ingest_success = db_manager.ingest_points(test_collection_name, sample_vectors, sample_payloads)
            if ingest_success:
                print("Points ingested.")
            else:
                print("Failed to ingest points.")

            print("\n4. Getting collection info after ingestion:")
            info_after_ingest = db_manager.get_collection_info(test_collection_name)
            if info_after_ingest:
                print(f"Info for '{test_collection_name}': Points count = {info_after_ingest.get('points_count')}")

            print("\n5. Searching points:")
            # Query vector similar to the first sample vector
            query_vec = [float(i) for i in range(test_vector_size)]
            query_vec[0] = 1.0

            search_results = db_manager.search(test_collection_name, query_vec, limit=2)
            if search_results:
                print(f"Search results for query similar to first vector (top {len(search_results)}):")
                for i, result in enumerate(search_results):
                    print(f"  Result {i+1}: ID={result['id']}, Score={result['score']:.4f}, Payload={result['payload']}")
            else:
                print("No search results or error during search.")

            print("\n6. Deleting collection for cleanup:")
            delete_success = db_manager.delete_collection(test_collection_name)
            if delete_success:
                print(f"Collection '{test_collection_name}' successfully deleted.")
            else:
                print(f"Failed to delete collection '{test_collection_name}'.")
    else:
        print("Failed to initialize VectorDBManager client. Cannot run tests.")

    print("\n----- VectorDBManager tests finished -----")
