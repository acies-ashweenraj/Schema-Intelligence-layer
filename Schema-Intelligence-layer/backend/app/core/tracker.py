import json
import os
from datetime import datetime
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import time

class APICallTracker:
    """
    Track and monitor Groq API calls with cost calculation.
    Saves all data to log files with append functionality.
    """
    
    def __init__(self, log_dir: str = "artifacts/logs"):
        """
        Initialize tracker with log directory.
        
        Args:
            log_dir: Directory to store all log files
        """
        self.calls = []
        self.total_cost = 0.0
        self.total_tokens = {"input": 0, "output": 0}
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize log files
        self.calls_log_file = self.log_dir / "api_calls.jsonl"
        self.summary_log_file = self.log_dir / "api_summary.json"
        self.errors_log_file = self.log_dir / "api_errors.log"
        self.cost_log_file = self.log_dir / "api_costs.csv"
        
        # Initialize CSV header if not exists
        self._init_cost_log_csv()
        
        self.logger.info(f"APICallTracker initialized. Log directory: {self.log_dir}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup Python logging to file and console."""
        
        logger = logging.getLogger('APICallTracker')
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler for all logs
        fh = logging.FileHandler(
            self.log_dir / f"tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _init_cost_log_csv(self):
        """Initialize CSV file with headers if not exists."""
        if not self.cost_log_file.exists():
            with open(self.cost_log_file, 'w') as f:
                f.write("timestamp,table_name,column_name,model,input_tokens,output_tokens,"
                       "total_tokens,latency_ms,cost_usd,success,error\n")
            self.logger.info(f"Created cost log CSV: {self.cost_log_file}")
    
    def log_call(self, table_name: str, column_name: str, model: str,
                 input_tokens: int, output_tokens: int, latency_ms: float,
                 success: bool = True, error: Optional[str] = None):
        """
        Log each API call with full metrics.
        Appends to multiple log files simultaneously.
        
        Args:
            table_name: Database table name
            column_name: Column name being processed
            model: LLM model used (e.g., "meta-llama/llama-3-70b-instruct")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            latency_ms: API call latency in milliseconds
            success: Whether call succeeded
            error: Error message if failed
        """
        
        timestamp = datetime.now().isoformat()
        
        # Calculate cost (Groq pricing as of Jan 2026)
        # input: $0.05 per 1M tokens
        # output: $0.15 per 1M tokens
        input_cost = (input_tokens / 1_000_000) * 0.05
        output_cost = (output_tokens / 1_000_000) * 0.15
        call_cost = input_cost + output_cost
        
        # Create call record
        call_record = {
            "timestamp": timestamp,
            "table": table_name,
            "column": column_name,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "latency_ms": latency_ms,
            "cost_usd": call_cost,
            "success": success,
            "error": error
        }
        
        # Add to in-memory list
        self.calls.append(call_record)
        self.total_cost += call_cost
        self.total_tokens["input"] += input_tokens
        self.total_tokens["output"] += output_tokens
        
        # 1. Append to JSONL file (one JSON per line)
        self._append_to_jsonl(call_record)
        
        # 2. Append to CSV file
        self._append_to_csv(call_record)
        
        # 3. Log to text file (if error)
        if not success:
            self._log_error(call_record)
        
        # 4. Update summary JSON
        self._update_summary_json()
        
        # 5. Log to Python logger
        if success:
            self.logger.info(
                f"API Call: {table_name}.{column_name} | "
                f"Tokens: {input_tokens + output_tokens} | "
                f"Cost: ${call_cost:.6f} | "
                f"Latency: {latency_ms}ms"
            )
        else:
            self.logger.error(
                f"API Call FAILED: {table_name}.{column_name} | "
                f"Error: {error}"
            )
    
    def _append_to_jsonl(self, record: Dict):
        """Append call record to JSONL file (one JSON object per line)."""
        try:
            with open(self.calls_log_file, 'a') as f:
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSONL: {e}")
    
    def _append_to_csv(self, record: Dict):
        """Append call record to CSV file."""
        try:
            with open(self.cost_log_file, 'a') as f:
                f.write(
                    f"{record['timestamp']},"
                    f"{record['table']},"
                    f"{record['column']},"
                    f"{record['model']},"
                    f"{record['input_tokens']},"
                    f"{record['output_tokens']},"
                    f"{record['total_tokens']},"
                    f"{record['latency_ms']},"
                    f"{record['cost_usd']:.6f},"
                    f"{record['success']},"
                    f"\"{record['error'] or ''}\"\n"
                )
        except Exception as e:
            self.logger.error(f"Failed to write CSV: {e}")
    
    def _log_error(self, record: Dict):
        """Append error details to errors log file."""
        try:
            with open(self.errors_log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Timestamp: {record['timestamp']}\n")
                f.write(f"Table: {record['table']}\n")
                f.write(f"Column: {record['column']}\n")
                f.write(f"Error: {record['error']}\n")
                f.write(f"Model: {record['model']}\n")
                f.write(f"{ '='*80}\n")
        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")
    
    def _update_summary_json(self):
        """Update summary JSON file with current statistics."""
        try:
            summary = self.get_summary()
            with open(self.summary_log_file, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write summary: {e}")
    
    def get_summary(self) -> Dict:
        """Get aggregated statistics."""
        if not self.calls:
            return {
                "total_calls": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0,
                "total_tokens": self.total_tokens,
                "total_cost_usd": self.total_cost,
                "avg_latency_ms": 0
            }
        
        successful = sum(1 for c in self.calls if c["success"])
        failed = sum(1 for c in self.calls if not c["success"])
        
        return {
            "total_calls": len(self.calls),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.calls) if self.calls else 0,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_latency_ms": sum(c["latency_ms"] for c in self.calls) / len(self.calls) if self.calls else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def export_to_json(self, filepath: str = None):
        """Export all calls and summary to JSON file."""
        if filepath is None:
            filepath = self.log_dir / f"api_calls_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "summary": self.get_summary(),
                    "calls": self.calls
                }, f, indent=2)
            self.logger.info(f"Exported API calls to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")
    
    def get_stats_by_table(self) -> Dict:
        """Get statistics aggregated by table."""
        stats = {}
        for call in self.calls:
            table = call['table']
            if table not in stats:
                stats[table] = {
                    "calls": 0,
                    "successful": 0,
                    "failed": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0
                }
            
            stats[table]["calls"] += 1
            if call["success"]:
                stats[table]["successful"] += 1
            else:
                stats[table]["failed"] += 1
            stats[table]["total_tokens"] += call["total_tokens"]
            stats[table]["total_cost"] += call["cost_usd"]
        
        return stats
    
    def get_stats_by_model(self) -> Dict:
        """Get statistics aggregated by model."""
        stats = {}
        for call in self.calls:
            model = call['model']
            if model not in stats:
                stats[model] = {
                    "calls": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "avg_latency_ms": 0
                }
            
            stats[model]["calls"] += 1
            stats[model]["total_tokens"] += call["total_tokens"]
            stats[model]["total_cost"] += call["cost_usd"]
        
        # Calculate averages
        for model in stats:
            latencies = [c["latency_ms"] for c in self.calls if c["model"] == model]
            stats[model]["avg_latency_ms"] = sum(latencies) / len(latencies) if latencies else 0
        
        return stats
    
    def print_summary(self):
        """Print formatted summary to console and log."""
        summary = self.get_summary()
        
        output = f"""
{'='*80}
API CALL TRACKER SUMMARY
{'='*80}
Total Calls:        {summary['total_calls']}
Successful:         {summary['successful']}
Failed:             {summary['failed']}
Success Rate:       {summary['success_rate']*100:.2f}%
Total Tokens:       {summary['total_tokens']['input'] + summary['total_tokens']['output']:,}
  - Input:          {summary['total_tokens']['input']:,}
  - Output:         {summary['total_tokens']['output']:,}
Total Cost:         ${summary['total_cost_usd']:.6f}
Avg Latency:        {summary['avg_latency_ms']:.2f}ms
Last Updated:       {summary.get('last_updated', 'N/A')}
{'='*80}
"""
        
        print(output)
        self.logger.info(output)
        
        # Also save to file
        summary_text_file = self.log_dir / "summary.txt"
        with open(summary_text_file, 'a') as f:
            f.write(output + '\n')
    
    def load_existing_calls(self) -> int:
        """Load existing calls from JSONL file into memory."""
        if not self.calls_log_file.exists():
            return 0
        
        count = 0
        try:
            with open(self.calls_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        self.calls.append(record)
                        self.total_cost += record['cost_usd']
                        self.total_tokens['input'] += record['input_tokens']
                        self.total_tokens['output'] += record['output_tokens']
                        count += 1
            
            self.logger.info(f"Loaded {count} existing calls from {self.calls_log_file}")
        except Exception as e:
            self.logger.error(f"Failed to load existing calls: {e}")
        
        return count

class QueryMetricsTracker:
    """
    Track and monitor NL2SQL query generation metrics.
    Logs all natural language queries and generated SQL with detailed metrics.
    """
    
    def __init__(self, log_dir: str = "artifacts/query_logs"):
        """
        Initialize query tracker with log directory.
        
        Args:
            log_dir: Directory to store all query log files
        """
        self.queries = []
        self.total_cost = 0.0
        self.total_tokens = {"input": 0, "output": 0}
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize log files
        self.queries_log_file = self.log_dir / "nl2sql_queries.jsonl"
        self.summary_log_file = self.log_dir / "query_summary.json"
        self.errors_log_file = self.log_dir / "query_errors.log"
        self.performance_log_file = self.log_dir / "query_performance.csv"
        self.sql_log_file = self.log_dir / "generated_sql.sql"
        
        # Initialize CSV headers
        self._init_csv_headers()
        
        self.logger.info(f"QueryMetricsTracker initialized. Log directory: {self.log_dir}")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup Python logging to file and console."""
        
        logger = logging.getLogger('QueryMetricsTracker')
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()
        
        # File handler
        fh = logging.FileHandler(
            self.log_dir / f"query_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
        
        return logger
    
    def _init_csv_headers(self):
        """Initialize CSV files with headers if not exists."""
        
        # Performance CSV
        if not self.performance_log_file.exists():
            with open(self.performance_log_file, 'w') as f:
                f.write("timestamp,nl_query,sql_query,success,execution_time_ms,"
                       "input_tokens,output_tokens,total_tokens,cost_usd,"
                       "confidence,retry_attempt,error,table_count,complexity\n")
            self.logger.info(f"Created performance log CSV: {self.performance_log_file}")
    
    def log_query(self, 
                  nl_query: str,
                  sql_query: str,
                  success: bool,
                  input_tokens: int,
                  output_tokens: int,
                  latency_ms: float,
                  confidence: float = None,
                  retry_attempt: int = 1,
                  error: Optional[str] = None,
                  table_count: int = None,
                  complexity: str = "medium",
                  metadata: Dict = None):
        """
        Log a natural language query and its generated SQL.
        
        Args:
            nl_query: Natural language query from user
            sql_query: Generated SQL query
            success: Whether query generation succeeded
            input_tokens: Tokens used in prompt
            output_tokens: Tokens in generated SQL
            latency_ms: API call latency in milliseconds
            confidence: Confidence score (0-1)
            retry_attempt: Which attempt this is (for self-correction)
            error: Error message if failed
            table_count: Number of tables involved
            complexity: Query complexity (simple/medium/complex)
            metadata: Additional metadata dict
        """
        
        timestamp = datetime.now().isoformat()
        
        # Calculate cost (Groq pricing)
        input_cost = (input_tokens / 1_000_000) * 0.05
        output_cost = (output_tokens / 1_000_000) * 0.15
        call_cost = input_cost + output_cost
        
        # Create query record
        query_record = {
            "timestamp": timestamp,
            "nl_query": nl_query,
            "sql_query": sql_query,
            "success": success,
            "execution_time_ms": latency_ms,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "cost_usd": call_cost,
            "confidence": confidence,
            "retry_attempt": retry_attempt,
            "error": error,
            "table_count": table_count,
            "complexity": complexity,
            "metadata": metadata or {}
        }
        
        # Add to in-memory list
        self.queries.append(query_record)
        self.total_cost += call_cost
        self.total_tokens["input"] += input_tokens
        self.total_tokens["output"] += output_tokens
        
        # 1. Append to JSONL file
        self._append_to_jsonl(query_record)
        
        # 2. Append to CSV file
        self._append_to_csv(query_record)
        
        # 3. Append SQL to SQL log
        self._append_to_sql_log(query_record)
        
        # 4. Log errors
        if not success:
            self._log_error(query_record)
        
        # 5. Update summary
        self._update_summary_json()
        
        # 6. Log to Python logger
        if success:
            self.logger.info(
                f"Query generated: '{nl_query[:50]}...' | "
                f"Tokens: {input_tokens + output_tokens} | "
                f"Cost: ${call_cost:.6f} | "
                f"Confidence: {f'{confidence:.2f}' if confidence is not None else 'N/A'} | "
                f"Attempt: {retry_attempt}"
            )
        else:
            self.logger.error(
                f"Query generation FAILED: '{nl_query[:50]}...' | "
                f"Error: {error} | "
                f"Attempt: {retry_attempt}"
            )
    
    def _append_to_jsonl(self, record: Dict):
        """Append query record to JSONL file."""
        try:
            with open(self.queries_log_file, 'a') as f:
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to write JSONL: {e}")
    
    def _append_to_csv(self, record: Dict):
        """Append query record to CSV file."""
        try:
            with open(self.performance_log_file, 'a') as f:
                # Escape quotes in SQL
                sql_query = record['sql_query'].replace('"', '""')
                nl_query = record['nl_query'].replace('"', '""')
                
                f.write(
                    f"{record['timestamp']},"
                    f"\"{nl_query}\","
                    f"\"{sql_query}\","
                    f"{record['success']},"
                    f"{record['execution_time_ms']},"
                    f"{record['input_tokens']},"
                    f"{record['output_tokens']},"
                    f"{record['total_tokens']},"
                    f"{record['cost_usd']:.6f},"
                    f"{record['confidence'] or 0},"
                    f"{record['retry_attempt']},"
                    f"\"{record['error'] or ''}\","
                    f"{record['table_count'] or 0},"
                    f"{record['complexity']}\n"
                )
        except Exception as e:
            self.logger.error(f"Failed to write CSV: {e}")
    
    def _append_to_sql_log(self, record: Dict):
        """Append generated SQL to SQL log file."""
        try:
            with open(self.sql_log_file, 'a') as f:
                f.write(f"\n-- Generated at: {record['timestamp']}\n")
                f.write(f"-- User query: {record['nl_query']}\n")
                f.write(f"-- Success: {record['success']}\n")
                f.write(f"-- Confidence: {record['confidence']}\n")
                if not record['success']:
                    f.write(f"-- Error: {record['error']}\n")
                f.write(f"-- Attempt: {record['retry_attempt']}\n")
                f.write(f"{record['sql_query']};\n")
                f.write(f"-- " + "="*80 + "\n")
        except Exception as e:
            self.logger.error(f"Failed to write SQL log: {e}")
    
    def _log_error(self, record: Dict):
        """Append error details to errors log file."""
        try:
            with open(self.errors_log_file, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Timestamp: {record['timestamp']}\n")
                f.write(f"Natural Language Query: {record['nl_query']}\n")
                f.write(f"Generated SQL: {record['sql_query']}\n")
                f.write(f"Error: {record['error']}\n")
                f.write(f"Attempt: {record['retry_attempt']}\n")
                f.write(f"Complexity: {record['complexity']}\n")
                f.write(f"{ '='*80}\n")
        except Exception as e:
            self.logger.error(f"Failed to write error log: {e}")
    
    def _update_summary_json(self):
        """Update summary JSON file with current statistics."""
        try:
            summary = self.get_summary()
            with open(self.summary_log_file, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to write summary: {e}")
    
    def get_summary(self) -> Dict:
        """Get aggregated statistics."""
        if not self.queries:
            return {
                "total_queries": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0,
                "total_tokens": self.total_tokens,
                "total_cost_usd": self.total_cost,
                "avg_latency_ms": 0,
                "avg_confidence": 0,
                "queries_needing_retry": 0,
                "avg_retries": 0,
                "last_updated": datetime.now().isoformat()
            }
        
        successful = sum(1 for q in self.queries if q["success"])
        failed = sum(1 for q in self.queries if not q["success"])
        queries_with_retries = sum(1 for q in self.queries if q["retry_attempt"] > 1)
        
        confidences = [q["confidence"] for q in self.queries if q["confidence"] is not None]
        retries = [q["retry_attempt"] for q in self.queries]
        
        return {
            "total_queries": len(self.queries),
            "successful": successful,
            "failed": failed,
            "success_rate": successful / len(self.queries) if self.queries else 0,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_latency_ms": sum(q["execution_time_ms"] for q in self.queries) / len(self.queries) if self.queries else 0,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "queries_needing_retry": queries_with_retries,
            "avg_retries": sum(retries) / len(retries) if retries else 0,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_success_rate(self) -> float:
        """Get overall success rate."""
        if not self.queries:
            return 0
        successful = sum(1 for q in self.queries if q["success"])
        return successful / len(self.queries)
    
    def get_stats_by_complexity(self) -> Dict:
        """Get statistics aggregated by query complexity."""
        stats = {}
        for query in self.queries:
            complexity = query['complexity']
            if complexity not in stats:
                stats[complexity] = {
                    "queries": 0,
                    "successful": 0,
                    "failed": 0,
                    "success_rate": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "avg_latency_ms": 0,
                    "avg_confidence": 0
                }
            
            stats[complexity]["queries"] += 1
            if query["success"]:
                stats[complexity]["successful"] += 1
            else:
                stats[complexity]["failed"] += 1
            stats[complexity]["total_tokens"] += query["total_tokens"]
            stats[complexity]["total_cost"] += query["cost_usd"]
        
        # Calculate averages
        for complexity in stats:
            queries_of_type = [q for q in self.queries if q["complexity"] == complexity]
            
            # Success rate
            successful = sum(1 for q in queries_of_type if q["success"])
            stats[complexity]["success_rate"] = successful / len(queries_of_type) if queries_of_type else 0
            
            # Average latency
            latencies = [q["execution_time_ms"] for q in queries_of_type]
            stats[complexity]["avg_latency_ms"] = sum(latencies) / len(latencies) if latencies else 0
            
            # Average confidence
            confidences = [q["confidence"] for q in queries_of_type if q["confidence"] is not None]
            stats[complexity]["avg_confidence"] = sum(confidences) / len(confidences) if confidences else 0
        
        return stats
    
    def get_retry_stats(self) -> Dict:
        """Get statistics about query retries."""
        queries_with_retries = [q for q in self.queries if q["retry_attempt"] > 1]
        
        return {
            "total_queries": len(self.queries),
            "queries_with_retries": len(queries_with_retries),
            "retry_rate": len(queries_with_retries) / len(self.queries) if self.queries else 0,
            "avg_retries": sum(q["retry_attempt"] for q in self.queries) / len(self.queries) if self.queries else 0,
            "max_retry_attempt": max([q["retry_attempt"] for q in self.queries]) if self.queries else 0
        }
    
    def get_confidence_stats(self) -> Dict:
        """Get statistics about confidence scores."""
        confidences = [q["confidence"] for q in self.queries if q["confidence"] is not None]
        
        if not confidences:
            return {
                "avg_confidence": 0,
                "min_confidence": 0,
                "max_confidence": 0,
                "low_confidence_queries": 0,
                "low_confidence_rate": 0
            }
        
        low_confidence = sum(1 for c in confidences if c < 0.7)
        
        return {
            "avg_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "low_confidence_queries": low_confidence,
            "low_confidence_rate": low_confidence / len(confidences)
        }
    
    def print_summary(self):
        """Print formatted summary to console and log."""
        summary = self.get_summary()
        retry_stats = self.get_retry_stats()
        confidence_stats = self.get_confidence_stats()
        
        output = f"""
{'='*80}
NL2SQL QUERY METRICS SUMMARY
{'='*80}
Total Queries:          {summary['total_queries']}
Successful:             {summary['successful']}
Failed:                 {summary['failed']}
Success Rate:           {summary['success_rate']*100:.2f}%

TOKENS & COST:
Total Tokens:           {summary['total_tokens']['input'] + summary['total_tokens']['output']:,}
  - Input:              {summary['total_tokens']['input']:,}
  - Output:             {summary['total_tokens']['output']:,}
Total Cost:             ${summary['total_cost_usd']:.6f}
Avg Cost per Query:     ${(summary['total_cost_usd']/summary['total_queries']) if summary['total_queries'] else 0:.6f}

PERFORMANCE:
Avg Latency:            {summary['avg_latency_ms']:.2f}ms
Avg Confidence:         {summary['avg_confidence']:.2f}

RETRIES & CORRECTIONS:
Queries Needing Retry:  {summary['queries_needing_retry']}
Retry Rate:             {retry_stats['retry_rate']*100:.2f}%
Avg Retry Attempts:     {retry_stats['avg_retries']:.2f}
Max Retry Attempt:      {retry_stats['max_retry_attempt']}

CONFIDENCE ANALYSIS:
Low Confidence (<0.7):  {confidence_stats['low_confidence_queries']}
Low Confidence Rate:    {confidence_stats['low_confidence_rate']*100:.2f}%
Min Confidence:         {confidence_stats['min_confidence']:.2f}
Max Confidence:         {confidence_stats['max_confidence']:.2f}

Last Updated:           {summary.get('last_updated', 'N/A')}
{'='*80}
"""
        
        print(output)
        self.logger.info(output)
        
        # Save to file
        summary_text_file = self.log_dir / "summary.txt"
        with open(summary_text_file, 'a') as f:
            f.write(output + '\n')
    
    def load_existing_queries(self) -> int:
        """Load existing queries from JSONL file into memory."""
        if not self.queries_log_file.exists():
            return 0
        
        count = 0
        try:
            with open(self.queries_log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        self.queries.append(record)
                        self.total_cost += record['cost_usd']
                        self.total_tokens['input'] += record['input_tokens']
                        self.total_tokens['output'] += record['output_tokens']
                        count += 1
            
            self.logger.info(f"Loaded {count} existing queries from {self.queries_log_file}")
        except Exception as e:
            self.logger.error(f"Failed to load existing queries: {e}")
        
        return count
    
    def export_to_json(self, filepath: str = None):
        """Export all queries and summary to JSON file."""
        if filepath is None:
            filepath = self.log_dir / f"queries_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    "summary": self.get_summary(),
                    "retry_stats": self.get_retry_stats(),
                    "confidence_stats": self.get_confidence_stats(),
                    "complexity_stats": self.get_stats_by_complexity(),
                    "queries": self.queries
                }, f, indent=2)
            self.logger.info(f"Exported queries to {filepath}")
        except Exception as e:
            self.logger.error(f"Failed to export to JSON: {e}")


# =============================================================================
# INTEGRATION WITH NL2SQL ENGINE
# =============================================================================

class NL2SQLEngine:
    """Natural Language to SQL query generator with tracking."""
    
    def __init__(self, semantic_layer: Dict, tracker: QueryMetricsTracker):
        """
        Initialize NL2SQL engine.
        
        Args:
            semantic_layer: Semantic layer with table/column information
            tracker: QueryMetricsTracker instance for logging
        """
        self.semantic_layer = semantic_layer
        self.tracker = tracker
        self.max_retries = 2
    
    def generate_sql(self, nl_query: str) -> Tuple[str, bool, float]:
        """
        Generate SQL from natural language query.
        
        Args:
            nl_query: Natural language query from user
            
        Returns:
            Tuple of (sql_query, success, confidence_score)
        """
        
        attempt = 1
        sql_query = None
        error = None
        total_tokens = {"input": 0, "output": 0}
        latency_ms = 0
        confidence = 0
        
        while attempt <= self.max_retries:
            try:
                # Build context
                context = self._build_context(nl_query)
                
                # Build prompt
                if attempt == 1:
                    prompt = self._build_initial_prompt(nl_query, context)
                else:
                    prompt = self._build_retry_prompt(nl_query, sql_query, error, context)
                
                # Call Groq
                start_time = time.time()
                
                from groq import Groq  # Assuming Groq client available
                groq_client = Groq()
                
                response = groq_client.chat.completions.create(
                    model="meta-llama/llama-3-70b-instruct",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000
                )
                
                latency_ms = (time.time() - start_time) * 1000
                
                # Parse response
                sql_query = response.choices[0].message.content.strip()
                
                # Extract SQL from response
                sql_query = self._extract_sql(sql_query)
                
                in_tokens = response.usage.prompt_tokens
                out_tokens = response.usage.completion_tokens
                total_tokens["input"] += in_tokens
                total_tokens["output"] += out_tokens
                
                # Calculate confidence based on SQL validity
                confidence = self._calculate_confidence(sql_query)
                
                # Try to validate SQL
                is_valid = self._validate_sql(sql_query)
                
                if is_valid:
                    # Success!
                    self.tracker.log_query(
                        nl_query=nl_query,
                        sql_query=sql_query,
                        success=True,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                        latency_ms=latency_ms,
                        confidence=confidence,
                        retry_attempt=attempt,
                        error=None,
                        table_count=self._count_tables(sql_query),
                        complexity=self._assess_complexity(sql_query)
                    )
                    
                    return sql_query, True, confidence
                else:
                    error = "Invalid SQL generated"
                    attempt += 1
                    continue
            
            except Exception as e:
                error = str(e)
                attempt += 1
                
                if attempt > self.max_retries:
                    # Final failure
                    self.tracker.log_query(
                        nl_query=nl_query,
                        sql_query=sql_query or "",
                        success=False,
                        input_tokens=total_tokens.get("input", 0),
                        output_tokens=total_tokens.get("output", 0),
                        latency_ms=latency_ms,
                        confidence=confidence,
                        retry_attempt=attempt - 1,
                        error=error,
                        complexity="unknown"
                    )
                    raise
        
        return None, False, 0
    
    def _build_context(self, nl_query: str) -> str:
        """Build semantic context from query and semantic layer."""
        # This would use semantic layer to build context
        return "Context: " + str(self.semantic_layer)[:500]
    
    def _build_initial_prompt(self, nl_query: str, context: str) -> str:
        """Build initial SQL generation prompt."""
        return f"""You are an expert SQL query generator for EHS databases.

Context:
{context}

Generate SQL for this natural language query:
{nl_query}

Return ONLY valid SQL, no explanation."""
    
    def _build_retry_prompt(self, nl_query: str, sql_query: str, error: str, context: str) -> str:
        """Build retry prompt with error feedback."""
        return f"""The previous SQL had an error: {error}

Original SQL:
{sql_query}

Please fix the SQL for this query:
{nl_query}

Return ONLY valid SQL."""
    
    def _extract_sql(self, response: str) -> str:
        """Extract SQL from response."""
        # Remove markdown code blocks if present
        if "```sql" in response:
            return response.split("```sql")[1].split("```")[0].strip()
        if "```" in response:
            return response.split("```")[1].split("```")[0].strip()
        return response.strip()
    
    def _calculate_confidence(self, sql_query: str) -> float:
        """Calculate confidence score based on SQL characteristics."""
        score = 0.5  # Base score
        
        # Check for SELECT
        if "SELECT" in sql_query.upper():
            score += 0.2
        
        # Check for JOIN (common pattern)
        if "JOIN" in sql_query.upper():
            score += 0.1
        
        # Check for WHERE
        if "WHERE" in sql_query.upper():
            score += 0.1
        
        # Check for GROUP BY
        if "GROUP BY" in sql_query.upper():
            score += 0.05
        
        return min(score, 1.0)
    
    def _validate_sql(self, sql_query: str) -> bool:
        """Basic SQL validation."""
        if not sql_query:
            return False
        
        sql_upper = sql_query.upper()
        
        # Must have SELECT
        if "SELECT" not in sql_upper:
            return False
        
        # Must have FROM
        if "FROM" not in sql_upper:
            return False
        
        return True
    
    def _count_tables(self, sql_query: str) -> int:
        """Count tables in SQL query."""
        # Simple count of FROM/JOIN keywords
        count = sql_query.upper().count(" FROM ")
        count += sql_query.upper().count(" JOIN ")
        return max(count, 1)
    
    def _assess_complexity(self, sql_query: str) -> str:
        """Assess query complexity."""
        sql_upper = sql_query.upper()
        
        has_join = "JOIN" in sql_upper
        has_subquery = "SELECT" in sql_upper and sql_upper.count("SELECT") > 1
        has_group_by = "GROUP BY" in sql_upper
        has_having = "HAVING" in sql_upper
        has_union = "UNION" in sql_upper
        
        complexity_score = sum([
            has_join,
            has_subquery,
            has_group_by,
            has_having,
            has_union
        ])
        
        if complexity_score >= 4:
            return "complex"
        elif complexity_score >= 2:
            return "medium"
        else:
            return "simple"
