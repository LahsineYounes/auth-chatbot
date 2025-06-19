import json
import uuid
from pathlib import Path
from typing import List, Dict, Any

# Adjust imports if running as a script directly from this directory vs. as part of a larger package
# When running with `python -m src.ingest_data` from `backend` directory, these should work.
# If running `python src/ingest_data.py` directly from `backend`, Python might not resolve modules with "."
# For simplicity in development, ensure PYTHONPATH is set or run as a module.
try:
    from .embedding_manager import EmbeddingManager
    from .vector_db_manager import VectorDBManager
except ImportError:
    # Fallback for direct script execution (e.g., python src/ingest_data.py from backend directory)
    # This assumes embedding_manager.py and vector_db_manager.py are in the same directory (src)
    print("Attempting fallback imports for direct script execution.")
    from embedding_manager import EmbeddingManager
    from vector_db_manager import VectorDBManager


# --- Constants ---
COLLECTION_NAME = "est_sale_documents_v2" # Added _v2 to distinguish from potential old versions
# Assuming this script is in 'src' and 'data' is a sibling directory to 'src'
# Path(__file__).parent = src directory
# Path(__file__).parent.parent = backend directory
# RULES_FILE_PATH = Path(__file__).parent.parent / "data/rules.json"
# The problem description stated: `RULES_FILE_PATH = Path(__file__).parent / "data/rules.json"`
# This implies rules.json is in src/data/rules.json. Let's assume there's a data folder under src for now.
# If rules.json is in backend/data/, then Path(__file__).parent.parent / "data/rules.json" is correct.
# Let's stick to the problem's path for now, assuming src/data/rules.json
RULES_DATA_DIR = Path(__file__).parent / "data"
RULES_FILE_PATH = RULES_DATA_DIR / "rules.json"


# --- Data Loading Function ---
def load_data_from_rules(file_path: Path) -> List[Dict[str, str]]:
    """
    Loads question-answer rules from a JSON file.
    The JSON file is expected to have a top-level key "questions",
    which contains a list of objects, each with "pattern" and "answer".

    Args:
        file_path (Path): The path to the JSON rules file.

    Returns:
        List[Dict[str, str]]: A list of rule dictionaries, or an empty list if an error occurs.
    """
    try:
        if not file_path.exists():
            print(f"Error: Rules file not found at {file_path}")
            return []
        with file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            # The rules seem to be under a 'questions' key in the provided example structure for RulesManager
            rules = data.get("questions", [])
            if not rules: # If "questions" key is missing or empty, try to load as a direct list of rules
                 print(f"Warning: 'questions' key not found or empty in {file_path}. Trying to load as a list.")
                 if isinstance(data, list):
                     rules = data # Assume the file is a list of rules directly
                 else:
                     print(f"Error: Data in {file_path} is not a list of rules and 'questions' key is missing/empty.")
                     return []
            print(f"Successfully loaded {len(rules)} rules from {file_path}.")
            return rules
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while loading {file_path}: {e}")
        return []

# --- Main Ingestion Logic ---
def run_ingestion():
    """
    Runs the data ingestion process:
    1. Initializes EmbeddingManager and VectorDBManager.
    2. Creates the Qdrant collection if it doesn't exist.
    3. Loads data from the rules.json file.
    4. Generates embeddings for the 'answer' part of each rule.
    5. Ingests the embeddings and payloads into Qdrant.
    """
    print("Starting data ingestion process...")

    # 1. Initialize Managers
    print("\nInitializing EmbeddingManager...")
    embedding_manager = EmbeddingManager() # Uses default model 'all-MiniLM-L6-v2'
    if not embedding_manager.model or embedding_manager.dimension is None:
        print("Error: Embedding model failed to load. Aborting ingestion.")
        return

    print(f"EmbeddingManager initialized with model '{embedding_manager.model_name}' (Dimension: {embedding_manager.dimension}).")

    print("\nInitializing VectorDBManager...")
    # VectorDBManager defaults to host="qdrant_db", grpc_port=6333
    # For local testing outside docker, ensure Qdrant is accessible at localhost:6333
    # db_host = "localhost" if not os.getenv("DOCKER_ENV") else "qdrant_db"
    # For now, defaults to "qdrant_db" as per VectorDBManager's constructor
    vector_db_manager = VectorDBManager()
    if not vector_db_manager.client:
        print("Error: VectorDBManager client failed to initialize. Aborting ingestion.")
        return
    print("VectorDBManager initialized.")

    # 2. Create Qdrant Collection
    print(f"\nEnsuring collection '{COLLECTION_NAME}' exists with vector size {embedding_manager.dimension}...")
    collection_created_or_exists = vector_db_manager.create_collection_if_not_exists(
        collection_name=COLLECTION_NAME,
        vector_size=embedding_manager.dimension
        # Uses default Distance.COSINE from VectorDBManager
    )
    if not collection_created_or_exists:
        print(f"Error: Failed to create or verify collection '{COLLECTION_NAME}'. Aborting ingestion.")
        return
    print(f"Collection '{COLLECTION_NAME}' is ready.")

    # 3. Load Data
    print(f"\nLoading data from rules file: {RULES_FILE_PATH}...")
    # Create dummy rules.json if it doesn't exist for testing
    if not RULES_FILE_PATH.parent.exists():
        RULES_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        print(f"Created directory {RULES_FILE_PATH.parent}")
    if not RULES_FILE_PATH.exists():
        print(f"Warning: Rules file {RULES_FILE_PATH} not found. Creating a dummy file for testing ingestion flow.")
        dummy_rules_data = {
            "questions": [
                {"pattern": "What is your name?", "answer": "I am a friendly assistant chatbot."},
                {"pattern": "What can you do?", "answer": "I can answer questions based on the information I have."},
                {"pattern": "What is FastAPI?", "answer": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints."}
            ]
        }
        try:
            with RULES_FILE_PATH.open('w', encoding='utf-8') as f:
                json.dump(dummy_rules_data, f, indent=2)
            print(f"Dummy rules file created at {RULES_FILE_PATH}")
        except Exception as e:
            print(f"Could not create dummy rules file: {e}")


    rule_items = load_data_from_rules(RULES_FILE_PATH)
    if not rule_items:
        print("No data loaded from rules file. Nothing to ingest.")
        return
    print(f"Loaded {len(rule_items)} items from rules file.")

    # 4. Prepare data for ingestion
    print("\nPreparing data for ingestion (generating embeddings)...")
    ids: List[str] = []
    vectors: List[List[float]] = []
    payloads: List[Dict[str, Any]] = []

    processed_count = 0
    successfully_embedded_count = 0

    for item in rule_items:
        processed_count += 1
        text_chunk = item.get('answer')
        source_question = item.get('pattern')

        if not text_chunk:
            print(f"Warning: Skipping item due to missing 'answer': {item}")
            continue
        if not source_question: # Allow missing pattern, but log it
            print(f"Warning: Item has missing 'pattern' (using answer as main content): {item}")
            source_question = "N/A"


        embedding = embedding_manager.generate_embedding(text_chunk)

        if embedding:
            payload: Dict[str, Any] = {
                "text_chunk": text_chunk,
                "source_question": source_question,
                "source_file": RULES_FILE_PATH.name # Store only the filename
            }
            ids.append(str(uuid.uuid4())) # Generate a unique ID for each point
            vectors.append(embedding)
            payloads.append(payload)
            successfully_embedded_count +=1
        else:
            print(f"Warning: Failed to generate embedding for text chunk: '{text_chunk[:50]}...'")
            # Optionally, decide if you want to ingest items even if embedding fails (e.g. with zero vector)
            # For now, we skip items that fail embedding.

    print(f"Processed {processed_count} items. Successfully generated embeddings for {successfully_embedded_count} items.")

    # 5. Ingest into Qdrant
    if vectors: # Only ingest if there's something to ingest
        print(f"\nIngesting {len(vectors)} points into collection '{COLLECTION_NAME}'...")
        success = vector_db_manager.ingest_points(
            collection_name=COLLECTION_NAME,
            vectors=vectors,
            payloads=payloads,
            ids=ids
        )
        if success:
            print(f"Successfully ingested {len(vectors)} points.")
        else:
            print("Ingestion failed or partially failed. Check logs from VectorDBManager.")
    else:
        print("No vectors were generated. Nothing to ingest into Qdrant.")

    print("\nData ingestion process finished.")

    # Optional: Get collection info after ingestion
    collection_info = vector_db_manager.get_collection_info(COLLECTION_NAME)
    if collection_info:
        print(f"\nCollection '{COLLECTION_NAME}' info after ingestion: {collection_info.get('points_count')} points.")


# --- Script Execution ---
if __name__ == '__main__':
    # This allows the script to be run directly.
    # For example: python -m src.ingest_data (from backend directory)
    # Or: python src/ingest_data.py (from backend directory, if fallbacks work or PYTHONPATH is set)

    # Ensure the data directory exists (as per RULES_DATA_DIR)
    if not RULES_DATA_DIR.exists():
        print(f"Data directory {RULES_DATA_DIR} does not exist. Creating it.")
        RULES_DATA_DIR.mkdir(parents=True, exist_ok=True)
        # Note: This doesn't create the rules.json itself here,
        # load_data_from_rules or the ingestion logic handles dummy creation if needed.

    run_ingestion()
