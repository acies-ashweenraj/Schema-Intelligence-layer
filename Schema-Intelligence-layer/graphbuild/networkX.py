import json
import time
import networkx as nx
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
import pickle


# ============================================================================
# ENUMS FOR SEMANTIC CLASSIFICATION
# ============================================================================

class TableRole(Enum):
    """Classification of table roles in data warehouse."""
    HUB = "hub"
    DIMENSION = "dimension"
    FACT = "fact"
    BRIDGE = "bridge"
    DETAIL = "detail"
    STAGING = "staging"
    UNKNOWN = "unknown"


class RelationshipCardinality(Enum):
    """Relationship cardinality types."""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:M"
    MANY_TO_ONE = "M:1"
    MANY_TO_MANY = "M:M"
    UNKNOWN = "unknown"


class ColumnRole(Enum):
    """Semantic role of columns."""
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    MEASURE = "measure"
    ATTRIBUTE = "attribute"
    TEMPORAL = "temporal"
    GEOSPATIAL = "geospatial"
    TEXT = "text"
    STATUS = "status"
    AUDIT = "audit"
    UNKNOWN = "unknown"


class BusinessDomain(Enum):
    """Business domains represented in database."""
    EHS_COMPLIANCE = "ehs_compliance"
    INCIDENT_TRACKING = "incident_tracking"
    RISK_MANAGEMENT = "risk_management"
    OPERATIONAL_SAFETY = "operational_safety"
    PERSONNEL_MGMT = "personnel_management"
    FACILITY_OPS = "facility_operations"


# ============================================================================
# DATA CLASSES FOR SEMANTIC ENRICHMENT
# ============================================================================

@dataclass
class BusinessRule:
    """Business rule for a column or table."""
    rule_id: str
    description: str
    rule_type: str
    applies_to: str
    target: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ColumnMetadata:
    """Enhanced column metadata."""
    name: str
    data_type: str
    nullable: bool
    is_key: bool
    null_pct: float
    distinct_pct: float
    min_val: Optional[str] = None
    max_val: Optional[str] = None
    column_role: ColumnRole = ColumnRole.UNKNOWN
    description: Optional[str] = None
    business_rules: List[BusinessRule] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['column_role'] = self.column_role.value
        d['business_rules'] = [br.to_dict() for br in self.business_rules]
        return d


@dataclass
class TableMetadata:
    """Enhanced table metadata."""
    name: str
    row_count: int
    column_count: int
    primary_key: List[str]
    risk_profile: str
    cluster: str
    has_temporal: bool
    has_geospatial: bool
    table_role: TableRole = TableRole.UNKNOWN
    domain: Optional[BusinessDomain] = None
    description: Optional[str] = None
    columns: List[ColumnMetadata] = field(default_factory=list)
    business_rules: List[BusinessRule] = field(default_factory=list)
    data_quality_score: float = 0.95
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['table_role'] = self.table_role.value
        d['domain'] = self.domain.value if self.domain else None
        d['columns'] = [c.to_dict() for c in self.columns]
        d['business_rules'] = [br.to_dict() for br in self.business_rules]
        return d


@dataclass
class RelationshipMetadata:
    """Enhanced relationship metadata."""
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    confidence: float
    evidence: str
    cardinality: RelationshipCardinality = RelationshipCardinality.UNKNOWN
    semantic_role: Optional[str] = None
    impact_level: str = "referential_integrity"
    semantic_meaning: Optional[str] = None
    
    def to_dict(self) -> Dict:
        d = asdict(self)
        d['cardinality'] = self.cardinality.value
        return d


# ============================================================================
# ENHANCED GRAPH BUILDER
# ============================================================================

class EnhancedGraphBuilder:
    """Builds enhanced NetworkX knowledge graph with 7 semantic layers."""
    
    def __init__(self, semantic_layer_path: Path):
        """Initialize builder."""
        self.semantic_layer_path = semantic_layer_path
        self.graph = nx.DiGraph()
        self.logger = self._setup_logging()
        
        with open(semantic_layer_path, 'r') as f:
            self.semantic_layer = json.load(f)
        
        self.tables: Dict[str, TableMetadata] = {}
        self.relationships: List[RelationshipMetadata] = []
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging."""
        logger = logging.getLogger('EnhancedGraphBuilder')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def build(self) -> nx.DiGraph:
        """Build complete enhanced graph."""
        self.logger.info("\n" + "="*70)
        self.logger.info("PHASE 1.7: ENHANCED KNOWLEDGE GRAPH BUILDER")
        self.logger.info("="*70)
        
        self.logger.info("\nStep 1: Loading and enriching semantic layer...")
        self._load_and_enrich_tables()
        self._enrich_relationships()
        
        self.logger.info("\nStep 2: Classifying tables by business role...")
        self._classify_table_roles()
        
        self.logger.info("\nStep 3: Extracting business rules...")
        self._extract_business_rules()
        
        self.logger.info("\nStep 4: Calculating data quality metrics...")
        self._calculate_data_quality()
        
        self.logger.info("\nStep 5: Building 7-layer semantic graph...")
        self._build_graph_layers()
        
        self.logger.info("\nStep 6: Adding semantic enrichment...")
        self._add_semantic_enrichment()
        
        self.logger.info("\nStep 7: Analyzing graph structure...")
        self._analyze_graph_structure()
        
        return self.graph
    
    def _load_and_enrich_tables(self):
        """Load tables from semantic layer and enrich metadata."""
        tables_raw = self.semantic_layer.get("tables", {})
        
        if isinstance(tables_raw, list):
            tables_raw = {t.get("name"): t for t in tables_raw}
        
        for table_name, table_data in tables_raw.items():
            columns = [
                ColumnMetadata(
                    name=col.get("name"),
                    data_type=col.get("data_type"),
                    nullable=col.get("nullable", True),
                    is_key=col.get("is_key", False),
                    null_pct=col.get("null_pct", 0.0),
                    distinct_pct=col.get("distinct_pct", 0.0),
                    min_val=col.get("min"),
                    max_val=col.get("max")
                )
                for col in table_data.get("columns", [])
            ]
            
            table = TableMetadata(
                name=table_name,
                row_count=table_data.get("row_count", 0),
                column_count=table_data.get("column_count", 0),
                primary_key=table_data.get("primary_key", []),
                risk_profile=table_data.get("risk_profile", "unknown"),
                cluster=table_data.get("cluster", "unknown"),
                has_temporal=table_data.get("has_temporal", False),
                has_geospatial=table_data.get("has_geospatial", False),
                description=table_data.get("description"),
                columns=columns,
                data_quality_score=0.95
            )
            
            self.tables[table_name] = table
            self.logger.info(f"✅ Loaded table: {table_name} ({table.column_count} columns)")
    
    def _enrich_relationships(self):
        """Enrich relationships with semantic metadata."""
        for table_name, table_data in self.semantic_layer.get("tables", {}).items():
            for rel in table_data.get("relationships", []):
                relationship = RelationshipMetadata(
                    source_table=rel.get("source_table"),
                    source_column=rel.get("source_column"),
                    target_table=rel.get("target_table"),
                    target_column=rel.get("target_column"),
                    confidence=rel.get("confidence", 0.0),
                    evidence=rel.get("evidence", "unknown")
                )
                
                relationship.cardinality = self._detect_cardinality(
                    relationship.source_table,
                    relationship.target_table,
                    relationship.source_column,
                    relationship.target_column
                )
                
                relationship.semantic_role = self._assign_semantic_role(
                    relationship.source_table,
                    relationship.target_table
                )
                
                relationship.semantic_meaning = (
                    f"Each {relationship.source_table} references one {relationship.target_table} "
                    f"via {relationship.source_column} -> {relationship.target_column}"
                )
                
                self.relationships.append(relationship)
        
        self.logger.info(f"✅ Enriched {len(self.relationships)} relationships")
    
    def _classify_table_roles(self):
        """Classify tables by their business role."""
        for table_name, table in self.tables.items():
            incoming = sum(
                1 for rel in self.relationships 
                if rel.target_table == table_name
            )
            outgoing = sum(
                1 for rel in self.relationships 
                if rel.source_table == table_name
            )
            
            if incoming == 0 and outgoing > 0:
                if "incident" in table_name.lower():
                    table.table_role = TableRole.HUB
                elif "facility" in table_name.lower() or "employee" in table_name.lower():
                    table.table_role = TableRole.DIMENSION
                else:
                    table.table_role = TableRole.DIMENSION
            elif incoming > 0 and outgoing == 0:
                table.table_role = TableRole.DETAIL
            elif incoming > 0 and outgoing > 0:
                if table_name.endswith("_details"):
                    table.table_role = TableRole.DETAIL
                else:
                    table.table_role = TableRole.FACT
            else:
                table.table_role = TableRole.DIMENSION
            
            if "incident" in table_name.lower():
                table.domain = BusinessDomain.INCIDENT_TRACKING
            elif "corrective" in table_name.lower():
                table.domain = BusinessDomain.EHS_COMPLIANCE
            elif "facility" in table_name.lower():
                table.domain = BusinessDomain.FACILITY_OPS
            elif "employee" in table_name.lower():
                table.domain = BusinessDomain.PERSONNEL_MGMT
            
            self.logger.info(
                f"✅ Classified {table_name}: {table.table_role.value} "
                f"({incoming}↑ / {outgoing}↓)"
            )
    
    def _extract_business_rules(self):
        """Extract business rules from schema and data patterns."""
        for table_name, table in self.tables.items():
            for col in table.columns:
                rules = []
                
                if col.is_key:
                    rules.append(BusinessRule(
                        rule_id=f"BR_{table_name}_{col.name}_001",
                        description=f"{col.name} must be unique",
                        rule_type="uniqueness",
                        applies_to="column",
                        target=f"{table_name}.{col.name}"
                    ))
                
                if not col.nullable:
                    rules.append(BusinessRule(
                        rule_id=f"BR_{table_name}_{col.name}_002",
                        description=f"{col.name} cannot be NULL",
                        rule_type="domain_constraint",
                        applies_to="column",
                        target=f"{table_name}.{col.name}"
                    ))
                
                if "status" in col.name.lower() and col.distinct_pct < 10:
                    rules.append(BusinessRule(
                        rule_id=f"BR_{table_name}_{col.name}_003",
                        description=f"{col.name} is an enumeration with {col.distinct_pct:.1f}% distinct values",
                        rule_type="domain_constraint",
                        applies_to="column",
                        target=f"{table_name}.{col.name}"
                    ))
                
                col.business_rules = rules
        
        self.logger.info(f"✅ Extracted business rules from schema")
    
    def _calculate_data_quality(self):
        """Calculate data quality score for each table."""
        for table_name, table in self.tables.items():
            scores = []
            
            for col in table.columns:
                completeness = (100.0 - col.null_pct) / 100.0
                uniqueness = col.distinct_pct / 100.0 if col.is_key else 1.0
                consistency = 0.95 if col.distinct_pct < 5 else 1.0
                score = (completeness * 0.5) + (uniqueness * 0.3) + (consistency * 0.2)
                scores.append(score)
            
            table.data_quality_score = sum(scores) / len(scores) if scores else 0.95
    
    def _build_graph_layers(self):
        """Build 7-layer semantic graph."""
        client_id = self.semantic_layer.get("client_id", "database")
        
        self.graph.add_node(
            client_id,
            node_type="client",
            layer=0,
            description="Database root node"
        )
        
        domains = set(
            table.domain for table in self.tables.values() 
            if table.domain
        )
        for domain in domains:
            domain_id = f"domain_{domain.value}"
            self.graph.add_node(
                domain_id,
                node_type="domain",
                layer=1,
                domain=domain.value
            )
            self.graph.add_edge(client_id, domain_id, relation="contains_domain")
        
        entities = {}
        for table in self.tables.values():
            if table.domain:
                entity_key = f"entity_{table.domain.value}"
                if entity_key not in entities:
                    entities[entity_key] = {
                        'domain': table.domain,
                        'tables': []
                    }
                entities[entity_key]['tables'].append(table.name)
        
        for entity_id, entity_info in entities.items():
            self.graph.add_node(
                entity_id,
                node_type="business_entity",
                layer=2,
                domain=entity_info['domain'].value
            )
            domain_id = f"domain_{entity_info['domain'].value}"
            self.graph.add_edge(domain_id, entity_id, relation="defines_entity")
        
        for table_name, table in self.tables.items():
            self.graph.add_node(
                table_name,
                node_type="table",
                layer=3,
                table_role=table.table_role.value,
                row_count=table.row_count,
                column_count=table.column_count,
                description=table.description,
                data_quality_score=table.data_quality_score,
                has_temporal=table.has_temporal,
                has_geospatial=table.has_geospatial
            )
            
            if table.domain:
                entity_id = f"entity_{table.domain.value}"
                self.graph.add_edge(entity_id, table_name, relation="has_table")
        
        for table_name, table in self.tables.items():
            for col in table.columns:
                col_id = f"{table_name}:{col.name}"
                col_role = self._detect_column_role(col, table)
                
                self.graph.add_node(
                    col_id,
                    node_type="column",
                    layer=4,
                    column_name=col.name,
                    data_type=col.data_type,
                    nullable=col.nullable,
                    column_role=col_role.value,
                    null_pct=col.null_pct,
                    distinct_pct=col.distinct_pct
                )
                
                self.graph.add_edge(table_name, col_id, relation="has_column")
        
        for table_name, table in self.tables.items():
            quality_id = f"quality_{table_name}"
            self.graph.add_node(
                quality_id,
                node_type="metric",
                layer=5,
                metric_type="data_quality",
                score=table.data_quality_score
            )
            self.graph.add_edge(table_name, quality_id, relation="has_metric")
        
        for rel in self.relationships:
            rel_id = f"{rel.source_table}→{rel.target_table}"
            self.graph.add_edge(
                rel.source_table,
                rel.target_table,
                key=rel_id,
                relation_type="foreign_key",
                cardinality=rel.cardinality.value,
                semantic_role=rel.semantic_role,
                confidence=rel.confidence,
                evidence=rel.evidence,
                semantic_meaning=rel.semantic_meaning
            )
        
        self.logger.info(
            f"✅ Built 7-layer graph: {self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )
    
    def _add_semantic_enrichment(self):
        """Add semantic enrichment to graph."""
        for table_name, table in self.tables.items():
            if table_name in self.graph:
                attrs = self.graph.nodes[table_name]
                attrs['table_metadata'] = table.to_dict()
    
    def _analyze_graph_structure(self):
        """Analyze graph structure."""
        out_degrees = dict(self.graph.out_degree())
        hubs = sorted(
            [(n, d) for n, d in out_degrees.items() if self.graph.nodes[n].get('node_type') == 'table'],
            key=lambda x: x[1],
            reverse=True
        )
        
        self.logger.info("\n📊 GRAPH ANALYSIS")
        self.logger.info(f"   Total nodes: {self.graph.number_of_nodes()}")
        self.logger.info(f"   Total edges: {self.graph.number_of_edges()}")
        self.logger.info(f"   Graph density: {nx.density(self.graph):.3f}")
        
        if hubs:
            self.logger.info(f"\n🔗 HUB TABLES (most connected)")
            for table_name, degree in hubs[:3]:
                self.logger.info(f"   • {table_name}: {degree} relationships")
    
    def save_graph(self, output_path: Path):
        """Save graph to .gpickle format."""
        with open(output_path, 'wb') as f:
            pickle.dump(self.graph, f, pickle.HIGHEST_PROTOCOL)
        self.logger.info(f"✅ Graph saved to {output_path}")
    
    def save_graph_summary(self, output_path: Path):
        """Save human-readable graph summary."""
        summary = {
            "graph_statistics": {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges(),
                "density": float(nx.density(self.graph)),
                "avg_clustering_coefficient": float(nx.average_clustering(self.graph.to_undirected()))
            },
            "nodes_by_layer": {
                "layer_0_client": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 0]),
                "layer_1_domains": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 1]),
                "layer_2_entities": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 2]),
                "layer_3_tables": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 3]),
                "layer_4_columns": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 4]),
                "layer_5_metrics": len([n for n, attrs in self.graph.nodes(data=True) if attrs.get('layer') == 5]),
            },
            "tables": {
                table_name: table.to_dict()
                for table_name, table in self.tables.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.logger.info(f"✅ Summary saved to {output_path}")
    
    def _detect_cardinality(self, source_table: str, target_table: str,
                           source_col: str, target_col: str) -> RelationshipCardinality:
        """Detect relationship cardinality."""
        source_table_obj = self.tables.get(source_table)
        target_table_obj = self.tables.get(target_table)
        
        if not source_table_obj or not target_table_obj:
            return RelationshipCardinality.UNKNOWN
        
        source_col_obj = next(
            (c for c in source_table_obj.columns if c.name == source_col),
            None
        )
        target_col_obj = next(
            (c for c in target_table_obj.columns if c.name == target_col),
            None
        )
        
        if not source_col_obj or not target_col_obj:
            return RelationshipCardinality.UNKNOWN
        
        if target_col_obj.is_key and not source_col_obj.is_key:
            return RelationshipCardinality.MANY_TO_ONE
        
        return RelationshipCardinality.ONE_TO_MANY
    
    def _assign_semantic_role(self, source_table: str, target_table: str) -> str:
        """Assign semantic role to relationship."""
        if "detail" in source_table.lower() or "details" in source_table.lower():
            return "detail_to_header"
        elif target_table in [t for t in self.tables if self.tables[t].table_role == TableRole.DIMENSION]:
            return "child_to_parent"
        else:
            return "reference"
    
    def _detect_column_role(self, col: ColumnMetadata, table: TableMetadata) -> ColumnRole:
        """Detect semantic role of column."""
        if col.is_key:
            return ColumnRole.PRIMARY_KEY
        elif col.name.endswith("_id") or col.name.startswith("fk_"):
            return ColumnRole.FOREIGN_KEY
        elif col.data_type in ["TIMESTAMP", "DATE", "TIME"]:
            return ColumnRole.TEMPORAL
        elif col.name in ["latitude", "longitude", "coordinates"]:
            return ColumnRole.GEOSPATIAL
        elif "status" in col.name.lower():
            return ColumnRole.STATUS
        elif col.name in ["created_at", "updated_at", "created_by", "updated_by", "last_updated_at"]:
            return ColumnRole.AUDIT
        elif col.data_type in ["INTEGER", "NUMERIC", "DECIMAL", "FLOAT"]:
            return ColumnRole.MEASURE
        elif col.data_type in ["VARCHAR", "TEXT"]:
            return ColumnRole.TEXT
        else:
            return ColumnRole.ATTRIBUTE


# ============================================================================
# PHASE 1.7 EXECUTION FUNCTION
# ============================================================================

def run_phase_1_7_build_graph(
    client_id: str,
    semantic_layer_path: Path,
    output_dir: Path
) -> nx.DiGraph:
    """
    Run Phase 1.7: Build enhanced NetworkX knowledge graph.
    
    Args:
        client_id: Client identifier
        semantic_layer_path: Path to semantic_layer_complete.json
        output_dir: Output directory for graph files
    
    Returns:
        NetworkX DiGraph with 7-layer semantic enrichment
    """
    
    if not semantic_layer_path.exists():
        raise FileNotFoundError(f"Semantic layer not found: {semantic_layer_path}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    builder = EnhancedGraphBuilder(semantic_layer_path)
    graph = builder.build()
    
    graph_path = output_dir / "knowledge_graph_enhanced.gpickle"
    summary_path = output_dir / "knowledge_graph_summary.json"
    
    builder.save_graph(graph_path)
    builder.save_graph_summary(summary_path)
    
    return graph
