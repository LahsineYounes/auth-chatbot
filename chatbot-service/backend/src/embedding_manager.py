from sentence_transformers import SentenceTransformer
from typing import List, Optional
import numpy as np

class EmbeddingManager:
    """
    Manages the loading of a sentence embedding model and generation of text embeddings.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the EmbeddingManager and loads the specified sentence embedding model.

        Args:
            model_name (str): The name of the sentence-transformer model to load.
            Defaults to 'all-MiniLM-L6-v2'.
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.dimension: Optional[int] = None

        try:
            # Load the sentence transformer model
            self.model = SentenceTransformer(self.model_name)
            if self.model:
                # Get the embedding dimension
                self.dimension = self.model.get_sentence_embedding_dimension()
                print(f"Embedding model '{self.model_name}' loaded successfully. Dimension: {self.dimension}")
            else:
                # This case should ideally not be reached if SentenceTransformer raises an error on failure
                print(f"Failed to load embedding model '{self.model_name}' - model object is None.")
        except Exception as e:
            print(f"Error loading embedding model '{self.model_name}': {e}")
            # Depending on application needs, could re-raise, or set a flag indicating failure.
            # For now, self.model and self.dimension will remain None.

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates an embedding for the given text using the loaded model.

        Args:
            text (str): The input text to embed.

        Returns:
            Optional[List[float]]: The generated embedding as a list of floats,
            or None if the model is not loaded or an error occurs.
        """
        if not self.model:
            print("Embedding model not loaded. Cannot generate embedding.")
            return None

        if not isinstance(text, str):
            print(f"Invalid input type for embedding. Expected str, got {type(text)}.")
            return None

        try:
            # Encode the text.
            # normalize_embeddings=True is often recommended for similarity search.
            # convert_to_tensor=False returns numpy.ndarray.
            embedding_array = self.model.encode(text, convert_to_tensor=False, normalize_embeddings=True)

            # Convert numpy array to list of floats
            return embedding_array.tolist()
        except Exception as e:
            # Log the error and the problematic text (or a snippet of it)
            print(f"Error generating embedding for text '{text[:100]}...': {e}")
            return None

if __name__ == '__main__':
    # This block provides example usage and allows for quick testing when the script is run directly.
    print("----- Testing EmbeddingManager -----")

    # Test with default model
    default_manager = EmbeddingManager()
    if default_manager.model and default_manager.dimension is not None:
        print(f"Default model '{default_manager.model_name}' (dim: {default_manager.dimension}) loaded.")
        sample_text_1 = "Hello world, this is a test sentence."
        embedding_1 = default_manager.generate_embedding(sample_text_1)
        if embedding_1:
            print(f"Embedding for '{sample_text_1}': {embedding_1[:3]}... (length: {len(embedding_1)})")
        else:
            print(f"Failed to generate embedding for '{sample_text_1}'.")

        # Test generating embedding for an empty string
        embedding_empty = default_manager.generate_embedding("")
        if embedding_empty:
            print(f"Embedding for empty string: {embedding_empty[:3]}... (length: {len(embedding_empty)})")
        else:
            print("Failed to generate embedding for an empty string.")
    else:
        print(f"Failed to initialize EmbeddingManager with default model or get dimension.")

    print("\n----- Testing with a potentially different model (e.g., if you specify one) -----")
    # Test with a specific model (ensure it's a valid model name from sentence-transformers)
    # For example, 'paraphrase-MiniLM-L3-v2' is another small model.
    # Note: This might download the model if not already cached.
    specific_manager = EmbeddingManager(model_name='paraphrase-MiniLM-L3-v2')
    if specific_manager.model and specific_manager.dimension is not None:
        print(f"Specific model '{specific_manager.model_name}' (dim: {specific_manager.dimension}) loaded.")
        sample_text_2 = "Sentence embeddings are useful for semantic search."
        embedding_2 = specific_manager.generate_embedding(sample_text_2)
        if embedding_2:
            print(f"Embedding for '{sample_text_2}': {embedding_2[:3]}... (length: {len(embedding_2)})")
        else:
            print(f"Failed to generate embedding for '{sample_text_2}'.")
    else:
        print(f"Failed to initialize EmbeddingManager with specific model '{specific_manager.model_name}'.")

    print("\n----- Testing error case: Model not loaded (simulated by None) -----")
    error_manager = EmbeddingManager(model_name="non_existent_model_for_testing_error_handling")
    # This should have printed an error during __init__
    if not error_manager.model:
        print("Simulating model load failure: model is None, as expected.")
    test_text_for_error = "Text for model that failed to load."
    embedding_error = error_manager.generate_embedding(test_text_for_error)
    if embedding_error is None:
        print(f"Generating embedding with no model returned None, as expected.")
    else:
        print(f"ERROR: Embedding generated even when model should not be loaded.")

    print("\n----- Testing error case: Invalid input type -----")
    if default_manager.model: # Re-use default manager if it loaded successfully
        invalid_input_embedding = default_manager.generate_embedding(12345) # type: ignore
        if invalid_input_embedding is None:
            print("Generating embedding with invalid input (integer) returned None, as expected.")
        else:
            print("ERROR: Embedding generated for invalid input type.")

    print("----- EmbeddingManager tests finished -----")
