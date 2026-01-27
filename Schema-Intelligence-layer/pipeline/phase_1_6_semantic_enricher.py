import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from groq import Groq
import logging
from src.core.tracker import APICallTracker
import os


class SemanticLayerEnricher:
    """Enriches semantic layer with Groq LLM descriptions."""
    
    def __init__(self, groq_api_key: str, api_tracker=None):
        """Initialize Groq client and API tracker."""
        self.client = Groq(api_key=groq_api_key)
        self.api_tracker = api_tracker
        self.logger = self._setup_logging()
        
        # Groq model configuration
        self.model = os.getenv("GROQ_MODEL", "meta-llama/llama-4-maverick-17b-128e-instruct")
        self.max_tokens = 500
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger('SemanticLayerEnricher')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def generate_table_description(self, table_name: str, 
                                  table_schema: Dict[str, Any],
                                  sample_data: Dict[str, Any]) -> str:
        """
        Generate description for a table using its schema and sample data.
        
        Args:
            table_name: Name of the table
            table_schema: Table schema (columns, types, relationships)
            sample_data: Sample data statistics for the table
        
        Returns:
            Generated description string
        """
        # Build schema context
        columns_text = "\n".join([
            f"  - {col['name']} ({col.get('data_type', 'UNKNOWN')})"
            for col in table_schema.get('columns', [])[:10]  # Limit to 10 columns
        ])
        
        # Build sample data context
        sample_context = ""
        if sample_data:
            sample_context = f"""
Sample Data Statistics:
  - Row count: {sample_data.get('row_count', 'Unknown')}
  - Primary key: {sample_data.get('primary_key', 'Unknown')}
  - Notable patterns: {sample_data.get('notable_patterns', 'None')}"""
        
        prompt = f"""You are an EHS (Environmental, Health, and Safety) domain expert for Oil & Gas operations.

Generate a concise business definition for this database table:

**Table Name:** {table_name}

**Schema (first 10 columns):**
{columns_text}

{sample_context}

Provide a 2-3 sentence definition that explains:
1. What this table represents and its business purpose
2. Key entities or relationships it tracks
3. How it's used for EHS compliance or incident tracking

Keep it concise, technical, and domain-specific."""

        try:
            start = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            latency_ms = (time.time() - start) * 1000
            description = response.choices[0].message.content.strip()
            
            # Log API call
            if self.api_tracker:
                self.api_tracker.log_call(
                    table_name=table_name,
                    column_name="[TABLE_DESCRIPTION]",
                    model=self.model,
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    latency_ms=latency_ms,
                    success=True
                )
            
            self.logger.info(
                f"✅ Table description: {table_name} "
                f"({latency_ms:.0f}ms, {response.usage.total_tokens} tokens)"
            )
            
            return description
        
        except Exception as e:
            self.logger.error(f"❌ Failed to generate description for {table_name}: {str(e)}")
            
            if self.api_tracker:
                self.api_tracker.log_call(
                    table_name=table_name,
                    column_name="[TABLE_DESCRIPTION]",
                    model=self.model,
                    input_tokens=0,
                    output_tokens=0,
                    latency_ms=0,
                    success=False,
                    error=str(e)
                )
            
            return f"[Error generating description: {str(e)}]"


def run_phase_1_6_enrichment(
    client_id: str,
    artifacts_dir: Path,
    groq_config: Dict[str, str],
    api_tracker=None
) -> Path:
    """
    Run Phase 1.6: Enrich semantic layer with Groq LLM descriptions.
    
    Process:
    1. Load semantic_layer_complete.json
    2. Load 02_data_profile.json for sample data context
    3. For each table in semantic layer:
       a. Get table schema and sample data
       b. Call Groq LLM for description
       c. Append description to semantic layer
       d. Save checkpoint
    4. Return path to updated semantic_layer_complete.json
    
    Args:
        client_id: Client identifier
        artifacts_dir: Root artifacts directory
        groq_config: Groq configuration {"api_key": "..."}
        api_tracker: Optional APICallTracker for logging
    
    Returns:
        Path to updated semantic_layer_complete.json
    """
    
    # Setup paths
    client_dir = artifacts_dir / client_id
    semantic_layer_path = client_dir / "semantic_layer_complete.json"
    data_profile_path = client_dir / "02_data_profile.json"
    
    if not semantic_layer_path.exists():
        raise FileNotFoundError(f"Semantic layer not found: {semantic_layer_path}")
    
    if not data_profile_path.exists():
        raise FileNotFoundError(f"Data profile not found: {data_profile_path}")
    
    logger = logging.getLogger('Phase1_6')
    logger.info("\n" + "="*70)
    logger.info("PHASE 1.6: SEMANTIC LAYER ENRICHMENT")
    logger.info("="*70)
    
    # Load existing files
    logger.info(f"\n📂 Loading semantic layer from {semantic_layer_path}")
    with open(semantic_layer_path, 'r') as f:
        semantic_layer = json.load(f)
    
    logger.info(f"📊 Loading data profile from {data_profile_path}")
    with open(data_profile_path, 'r') as f:
        data_profile = json.load(f)
    
    # Create enricher
    enricher = SemanticLayerEnricher(
        groq_api_key=groq_config["api_key"],
        api_tracker=api_tracker
    )
    
    # Get list of tables
    tables = list(semantic_layer.get("tables", {}).values())
    total_tables = len(tables)
    
    logger.info(f"\n📋 Found {total_tables} tables to enrich")
    logger.info("\n" + "="*70)
    logger.info("ENRICHING TABLES")
    logger.info("="*70)
    
    # Process each table
    for idx, table in enumerate(tables, 1):
        table_name = table.get("name", "Unknown")
        
        logger.info(f"\n[{idx}/{total_tables}] Processing table: {table_name}")
        
        # Get sample data for this table
        table_profile = data_profile.get(table_name, {})
        
        # Get table schema
        table_schema = {
            "columns": table.get("columns", []),
            "role": table.get("role", "Unknown"),
            "relationships": table.get("relationships", [])
        }
        
        # Generate description
        description = enricher.generate_table_description(
            table_name,
            table_schema,
            table_profile
        )
        
        # Append description to table
        table["description"] = description
        table["description_generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        table["description_source"] = "groq-llama-3-70b"
        
        # Save checkpoint after each table
        with open(semantic_layer_path, 'w') as f:
            json.dump(semantic_layer, f, indent=2)
        
        logger.info(f"   ✅ Description added and checkpoint saved")
        
        # Rate limiting
        time.sleep(0.5)
    
    logger.info("\n" + "="*70)
    logger.info("✅ ENRICHMENT COMPLETE")
    logger.info("="*70)
    
    # Final summary
    logger.info(f"\n📊 ENRICHMENT SUMMARY:")
    logger.info(f"   Total tables: {total_tables}")
    logger.info(f"   Tables enriched: {sum(1 for t in tables if t.get('description'))}")
    logger.info(f"   Output file: {semantic_layer_path}")
    
    # Get statistics from api_tracker
    if api_tracker:
        summary = api_tracker.get_summary()
        logger.info(f"\n💰 API METRICS:")
        logger.info(f"   Total calls: {summary['total_calls']}")
        logger.info(f"   Success rate: {summary['success_rate']*100:.1f}%")
        logger.info(f"   Total cost: ${summary['total_cost_usd']:.6f}")
        logger.info(f"   Avg latency: {summary['avg_latency_ms']:.2f}ms")
    
    return semantic_layer_path

