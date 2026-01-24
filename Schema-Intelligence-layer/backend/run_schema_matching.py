import os
import json
from dotenv import load_dotenv
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.hybrid_ensemble_matcher import run_hybrid_mapping

# Load environment variables from .env file
load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SOURCE_DB = os.getenv("SOURCE_DB")
TARGET_DB = os.getenv("TARGET_DB")

# Get Qdrant configuration from environment variables
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))

# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def main():
    # Source Database Configuration
    src_cfg = DBConfig(
        db_type="postgres",
        host=DB_HOST,
        port=DB_PORT,
        database=SOURCE_DB,
        username=DB_USER,
        password=DB_PASSWORD,
        schema_name="public", # Assuming 'public' schema, adjust if needed
    )

    # Target Database Configuration
    tgt_cfg = DBConfig(
        db_type="postgres",
        host=DB_HOST,
        port=DB_PORT,
        database=TARGET_DB,
        username=DB_USER,
        password=DB_PASSWORD,
        schema_name="public", # Assuming 'public' schema, adjust if needed
    )

    # Groq Configuration
    groq_cfg = GroqConfig(api_key=GROQ_API_KEY)

    print(f"Running hybrid mapping from {SOURCE_DB} to {TARGET_DB}...")
    try:
        result = run_hybrid_mapping(
            src_cfg=src_cfg,
            tgt_cfg=tgt_cfg,
            qdrant_host=QDRANT_HOST,
            qdrant_port=QDRANT_PORT,
            groq_cfg=groq_cfg,
            output_format="csv",  # Output format as CSV
            top_k_dense=5,
        )

        if isinstance(result, dict):
            output_filename = f"hybrid_mapping_output_{SOURCE_DB}_to_{TARGET_DB}.json"
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            print(f"Hybrid mapping results saved to {output_filename}")
        else:
            print("Hybrid mapping completed.")
            if result:
                print("Result:", result)


    except Exception as e:
        print(f"Error running hybrid mapping: {e}")

if __name__ == "__main__":
    main()
