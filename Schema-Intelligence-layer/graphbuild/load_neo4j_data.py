import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from src.GraphBuilder.graph_store_neo4j import Neo4jConfig, Neo4jGraphStore


load_dotenv()


def load_semantic_layer_to_neo4j(client_id: str, semantic_layer_path: str):
    """
    Load semantic layer JSON into Neo4j graph.
    
    Args:
        client_id: Client identifier (e.g., "c1_oil_gas", "c1ehs_oilgas")
        semantic_layer_path: Path to semantic_layer_complete.json
    """
    
    # 1. Load JSON file
    print(f"\n📂 Loading semantic layer from: {semantic_layer_path}")
    if not os.path.exists(semantic_layer_path):
        print(f"❌ File not found: {semantic_layer_path}")
        sys.exit(1)
    
    with open(semantic_layer_path, 'r') as f:
        semantic_layer = json.load(f)
    
    print(f"✅ Loaded semantic layer JSON")
    print(f"   - Tables: {len(semantic_layer.get('tables', []))}")
    print(f"   - Columns: {len(semantic_layer.get('columns', []))}")
    print(f"   - Relationships: {len(semantic_layer.get('relationships', []))}")
    
    # 2. Connect to Neo4j
    print(f"\n🔗 Connecting to Neo4j...")
    try:
        config = Neo4jConfig(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD"),
            database="neo4j",
        )
        
        if not config.password:
            print("❌ NEO4J_PASSWORD not found in .env file")
            sys.exit(1)
        
        store = Neo4jGraphStore(config)
        print(f"✅ Connected to Neo4j at {config.uri}")
    except Exception as e:
        print(f"❌ Failed to connect to Neo4j: {e}")
        sys.exit(1)
    
    # 3. Initialize schema (create constraints and indexes)
    print(f"\n🔧 Initializing Neo4j schema...")
    try:
        store.initialize_schema()
        print(f"✅ Schema initialized")
    except Exception as e:
        print(f"❌ Failed to initialize schema: {e}")
        store.close()
        sys.exit(1)
    
    # 4. Load semantic layer into Neo4j
    print(f"\n⏳ Loading semantic layer into Neo4j for client: {client_id}")
    try:
        store.load_semantic_layer(semantic_layer, client_id)
        print(f"✅ Semantic layer loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load semantic layer: {e}")
        store.close()
        sys.exit(1)
    
    # 5. Verify with statistics
    print(f"\n📊 Verifying data loaded...")
    try:
        stats = store.get_graph_stats(client_id)
        print(f"\n✅ Neo4j Graph Statistics for {client_id}:")
        print(f"   Tables:       {stats.get('tables', 0)}")
        print(f"   Columns:      {stats.get('columns', 0)}")
        print(f"   Relationships: {stats.get('relationships', 0)}")
        print(f"\n✅ Data successfully loaded into Neo4j!")
    except Exception as e:
        print(f"❌ Failed to verify: {e}")
        store.close()
        sys.exit(1)
    
    store.close()


if __name__ == "__main__":
    # Configuration
    client_id = "c1ehs_oilgas"  # Change this to your client ID
    semantic_layer_path = "artifacts/c1ehs_oilgas/semantic_layer_complete.json"  # Adjust path if needed
    
    print("=" * 70)
    print("Neo4j Semantic Layer Loader")
    print("=" * 70)
    
    if not os.path.exists(semantic_layer_path):
        print(f"Attempting to load from the specified path: {semantic_layer_path}")

    
    load_semantic_layer_to_neo4j(client_id, semantic_layer_path)
