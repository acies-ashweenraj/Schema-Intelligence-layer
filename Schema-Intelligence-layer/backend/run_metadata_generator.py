import json
import os
from dotenv import load_dotenv
from schema_matching_toolkit import DBConfig, GroqConfig
from schema_matching_toolkit.schema_metadata_generator import generate_schema_metadata

# Load environment variables from .env file
load_dotenv()

# Get database configuration from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
TARGET_DB = os.getenv("TARGET_DB")
SOURCE_DB = os.getenv("SOURCE_DB")

# Get Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Generate metadata for ashween_client (TARGET_DB) ---
print(f"Generating metadata for database: {TARGET_DB}")
db_cfg_target = DBConfig(
    db_type="postgres",
    host=DB_HOST,
    port=DB_PORT,
    database=TARGET_DB,
    username=DB_USER,
    password=DB_PASSWORD,
    schema_name="public", # Assuming 'public' schema, adjust if needed
)

groq_cfg = GroqConfig(api_key=GROQ_API_KEY)

try:
    metadata_target = generate_schema_metadata(
        db_cfg=db_cfg_target,
        groq_cfg=groq_cfg,
        output_format="json" # Ensure output format is json
    )

    # WORKAROUND: Add the 'table' key for compatibility with the loader.
    if 'tables' in metadata_target:
        metadata_target['table'] = metadata_target['tables']

    output_filename_target = f"schema_metadata_{TARGET_DB}.json"
    with open(output_filename_target, "w", encoding="utf-8") as f:
        json.dump(metadata_target, f, indent=2)
    print(f"Saved schema metadata for {TARGET_DB} to {output_filename_target}")
except Exception as e:
    print(f"Error generating metadata for {TARGET_DB}: {e}")

print("-" * 50)

# --- Generate metadata for ashween_master (SOURCE_DB) ---
print(f"Generating metadata for database: {SOURCE_DB}")
db_cfg_source = DBConfig(
    db_type="postgres",
    host=DB_HOST,
    port=DB_PORT,
    database=SOURCE_DB,
    username=DB_USER,
    password=DB_PASSWORD,
    schema_name="public", # Assuming 'public' schema, adjust if needed
)

try:
    metadata_source = generate_schema_metadata(
        db_cfg=db_cfg_source,
        groq_cfg=groq_cfg,
        output_format="json" # Ensure output format is json
    )

    # WORKAROUND: Add the 'table' key for compatibility with the loader.
    if 'tables' in metadata_source:
        metadata_source['table'] = metadata_source['tables']

    output_filename_source = f"schema_metadata_{SOURCE_DB}.json"
    with open(output_filename_source, "w", encoding="utf-8") as f:
        json.dump(metadata_source, f, indent=2)
    print(f"Saved schema metadata for {SOURCE_DB} to {output_filename_source}")
except Exception as e:
    print(f"Error generating metadata for {SOURCE_DB}: {e}")

