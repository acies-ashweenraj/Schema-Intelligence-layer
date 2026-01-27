import json
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from sqlalchemy.engine import Engine
from datetime import datetime, date
import decimal
import re
from collections import Counter

class CustomEncoder(json.JSONEncoder):
    """JSON encoder for special types."""
    def default(self, obj):
        if isinstance(obj, (decimal.Decimal, np.integer)):
            return float(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, (np.floating, np.ndarray)):
            return float(obj)
        return super().default(obj)


class PandasDataProfiler:
    """
    Profile columns using Pandas vectorized operations.
    
    Load each table ONCE into memory, compute all column stats in parallel.
    """
    
    def __init__(self, engine: Engine, batch_size: int = 50000):
        """
        Initialize profiler.
        
        Args:
            engine: SQLAlchemy engine
            batch_size: Rows per batch for large tables (default: 50K)
        """
        self.engine = engine
        self.batch_size = batch_size
        self.profiled_tables = {}
        
    def profile_all(self, schema_graph: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Profile all tables and columns.
        
        Flow:
            1. For each table:
               a. Load entire table into Pandas once (with chunking for large tables)
               b. For each column:
                  - Compute all stats vectorized (null%, distinct, min/max, samples, etc.)
                  - Detect patterns (ID, Date, Enum)
                  - Flag anomalies
            2. Return consolidated profile
        
        Args:
            schema_graph: Output from phase_1_1_schema_extractor
            
        Returns:
            Dictionary mapping "table.column" → statistics
        """
        print("\n" + "="*80)
        print("PHASE 1.2: DATA PROFILING (PANDAS VECTORIZED)")
        print("="*80)
        
        profile_data = {}
        total_tables = len(schema_graph.get("tables", {}))
        
        for idx, (table_name, table_info) in enumerate(schema_graph.get("tables", {}).items(), 1):
            print(f"\n[{idx}/{total_tables}] Profiling table: {table_name}")
            
            # ✅ LOAD TABLE ONCE (not per column!)
            df = self._load_table_to_pandas(table_name)
            
            if df is None or df.empty:
                print(f"   ⚠️  Empty table, skipping")
                continue
            
            print(f"   ✓ Loaded {len(df):,} rows × {len(df.columns)} columns")
            
            # ✅ PROFILE ALL COLUMNS IN ONE PASS
            profile_data[table_name] = {}
            
            for col_info in table_info.get("columns", []):
                col_name = col_info["name"]
                col_type = col_info.get("type", "UNKNOWN")
                
                # ✅ Vectorized profiling (no SQL!)
                stats = self._profile_column_vectorized(df, col_name, col_type)
                profile_data[table_name][col_name] = stats
            
            # Memory cleanup for large tables
            del df
            
            print(f"   ✓ Profiled {len(table_info.get('columns', []))} columns")
        
        print(f"\n✅ Total: {sum(len(cols) for cols in profile_data.values())} columns profiled")
        return profile_data
    
    def _load_table_to_pandas(self, table_name: str) -> Optional[pd.DataFrame]:
        """
        Load entire table into Pandas DataFrame.
        
        For large tables (> batch_size), reads in chunks to avoid memory issues.
        
        Args:
            table_name: Name of table to load
            
        Returns:
            DataFrame or None if table is empty/doesn't exist
        """
        try:
            # Try to load with chunking for large tables
            chunks = []
            query = f"SELECT * FROM {table_name}"
            
            with self.engine.connect() as conn:
                # Get row count first
                count_query = f"SELECT COUNT(*) FROM {table_name}"
                total_rows = conn.execute(count_query).scalar() or 0
                
                if total_rows == 0:
                    return pd.DataFrame()
                
                # Load in chunks if large table
                if total_rows > self.batch_size:
                    print(f"   (Large table: {total_rows:,} rows, loading in chunks)")
                    
                    for chunk in pd.read_sql(query, conn, chunksize=self.batch_size):
                        chunks.append(chunk)
                    
                    df = pd.concat(chunks, ignore_index=True)
                else:
                    # Small table: load at once
                    df = pd.read_sql(query, conn)
                
                return df
                
        except Exception as e:
            print(f"   ❌ Error loading {table_name}: {e}")
            return None
    
    def _profile_column_vectorized(self, df: pd.DataFrame, col_name: str, col_type: str) -> Dict[str, Any]:
        """
        Profile a single column using Pandas vectorized operations (NO SQL!).
        
        Computes:
        - Null percentage
        - Distinct count
        - Min/max (numeric only)
        - Mean/median/std (numeric only)
        - Top 10 values + frequencies (categorical)
        - Pattern detection (ID, Date, Enum)
        - Sample values (first 10 non-null)
        
        Args:
            df: DataFrame containing the column
            col_name: Column name
            col_type: SQL data type
            
        Returns:
            Dictionary of statistics
        """
        try:
            series = df[col_name]
            total_rows = len(df)
            null_count = series.isna().sum()
            null_pct = round(100 * null_count / total_rows, 2) if total_rows > 0 else 0
            non_null = series.dropna()
            non_null_count = len(non_null)
            
            # Base stats
            stats = {
                "total_rows": int(total_rows),
                "null_count": int(null_count),
                "null_pct": float(null_pct),
                "non_null_count": int(non_null_count),
                "distinct_count": int(series.nunique()),
                "data_type": col_type,
            }
            
            # ✅ NUMERIC STATS (if column is numeric)
            numeric_series = pd.to_numeric(non_null, errors='coerce').dropna()
            
            if len(numeric_series) > 0:  # Has numeric values
                stats.update({
                    "min": float(numeric_series.min()),
                    "max": float(numeric_series.max()),
                    "mean": float(numeric_series.mean()),
                    "median": float(numeric_series.median()),
                    "std": float(numeric_series.std()),
                    "q25": float(numeric_series.quantile(0.25)),
                    "q75": float(numeric_series.quantile(0.75)),
                })
            
            # ✅ CATEGORICAL STATS (if low cardinality)
            distinct_count = stats["distinct_count"]
            
            if distinct_count < 100 and non_null_count > 0:
                # Compute top 10 values + frequencies
                value_counts = non_null.value_counts().head(10)
                stats["top_values"] = [
                    {"value": str(val), "count": int(count)}
                    for val, count in value_counts.items()
                ]
                
                # Cardinality ratio
                cardinality_ratio = distinct_count / non_null_count if non_null_count > 0 else 0
                stats["cardinality_ratio"] = round(cardinality_ratio, 4)
            
            # ✅ SAMPLE VALUES (first 10 non-null)
            sample_values = non_null.head(10).tolist()
            stats["sample_values"] = [str(v)[:100] for v in sample_values]  # Truncate to 100 chars
            
            # ✅ PATTERN DETECTION (ID, Date, Enum)
            stats["patterns"] = self._detect_patterns_vectorized(non_null)
            
            # ✅ ANOMALY DETECTION
            stats["anomalies"] = self._detect_anomalies_vectorized(series, numeric_series)
            
            return stats
            
        except Exception as e:
            print(f"   ⚠️  Error profiling column {col_name}: {e}")
            return {"error": str(e), "total_rows": 0}
    
    def _detect_patterns_vectorized(self, series: pd.Series) -> Dict[str, Any]:
        """
        Detect patterns using Pandas string methods (vectorized).
        
        Detects:
        - ID patterns (numeric, UUID, prefixed)
        - Date patterns (ISO, US, EU formats)
        - Enum-like (low cardinality)
        - Email pattern
        """
        patterns = {
            "id_pattern": None,
            "date_pattern": None,
            "email_pattern": False,
            "enum_like": False,
            "is_binary": False,
        }
        
        if len(series) == 0:
            return patterns
        
        # Convert to string for pattern matching
        str_series = series.astype(str)
        sample = str_series.head(100)  # Sample first 100 for pattern detection
        
        # ✅ ID PATTERNS
        if sample.str.match(r'^\d+$').any():
            patterns["id_pattern"] = "numeric_id"
        elif sample.str.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', na=False).any():
            patterns["id_pattern"] = "uuid"
        elif sample.str.match(r'^[A-Z]{2,4}-\d{3,}$', na=False).any():
            patterns["id_pattern"] = "prefixed_id"
        
        # ✅ DATE PATTERNS
        if sample.str.match(r'^\d{4}-\d{2}-\d{2}', na=False).any():
            patterns["date_pattern"] = "ISO_8601"
        elif sample.str.match(r'^\d{2}/\d{2}/\d{4}', na=False).any():
            patterns["date_pattern"] = "US_DATE"
        elif sample.str.match(r'^\d{2}-\d{2}-\d{4}', na=False).any():
            patterns["date_pattern"] = "EU_DATE"
        
        # ✅ EMAIL PATTERN
        email_regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        if sample.str.match(email_regex, na=False).any():
            patterns["email_pattern"] = True
        
        # ✅ BINARY/BOOLEAN (only 2 distinct values)
        if series.nunique() == 2:
            patterns["is_binary"] = True
        
        # ✅ ENUM-LIKE (low cardinality)
        if series.nunique() < 20:
            patterns["enum_like"] = True
        
        return patterns
    
    def _detect_anomalies_vectorized(self, series: pd.Series, numeric_series: pd.Series) -> Dict[str, Any]:
        """
        Detect anomalies using Pandas vectorized operations.
        
        Detects:
        - Outliers (IQR method for numeric)
        - Mixed types
        - Duplicate rates
        """
        anomalies = {
            "has_outliers": False,
            "outlier_count": 0,
            "duplicate_rate": 0.0,
            "type_mismatch": False,
        }
        
        # ✅ NUMERIC OUTLIERS (IQR method)
        if len(numeric_series) > 0:
            Q1 = numeric_series.quantile(0.25)
            Q3 = numeric_series.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = (numeric_series < lower_bound) | (numeric_series > upper_bound)
            anomalies["outlier_count"] = int(outliers.sum())
            anomalies["has_outliers"] = bool(outliers.any())
        
        # ✅ DUPLICATE RATE
        total_non_null = series.notna().sum()
        if total_non_null > 0:
            duplicate_count = total_non_null - series.nunique()
            anomalies["duplicate_rate"] = round(duplicate_count / total_non_null, 4)
        
        # ✅ TYPE MISMATCH (numeric column with many NaNs after coercion)
        if len(numeric_series) < len(series.dropna()) * 0.5:
            anomalies["type_mismatch"] = True
        
        return anomalies
    
    def save(self, data: Dict, output_path: str) -> None:
        """Save profile data to JSON file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, cls=CustomEncoder)
        
        print(f"💾 Saved: {output_path}")