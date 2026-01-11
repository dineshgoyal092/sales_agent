"""
Data Manager for Retail Insights Assistant
Handles loading, cleaning, and querying sales datasets using DuckDB for efficiency
"""

import pandas as pd
import duckdb
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages sales data loading, preprocessing, and querying"""
    
    def __init__(self, data_dir: str = "Sales Dataset"):
        self.data_dir = Path(data_dir)
        self.conn = duckdb.connect(database=':memory:', read_only=False)
        self.tables: Dict[str, pd.DataFrame] = {}
        self.metadata: Dict[str, Dict] = {}
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """Load all CSV files from the data directory"""
        csv_files = list(self.data_dir.glob("*.csv"))
        
        for csv_file in csv_files:
            try:
                table_name = self._sanitize_table_name(csv_file.stem)
                logger.info(f"Loading {csv_file.name}...")
                
                # Load CSV with low_memory=False to avoid dtype warnings
                df = pd.read_csv(csv_file, low_memory=False)
                
                # Clean column names
                df.columns = [self._sanitize_column_name(col) for col in df.columns]
                
                # Convert nullable integer columns to standard types to avoid Arrow issues
                for col in df.columns:
                    dtype_name = df[col].dtype.name
                    # Handle all nullable integer types (Int8, Int16, Int32, Int64)
                    if dtype_name.startswith('Int'):
                        df[col] = df[col].fillna(0).astype('int64')
                    # Handle object columns that might be mixed types
                    elif dtype_name == 'object':
                        # Try to convert to numeric if possible, otherwise keep as string
                        try:
                            # First check if all non-null values are numeric
                            sample = df[col].dropna().head(100)
                            if len(sample) > 0 and sample.astype(str).str.match(r'^-?\d+\.?\d*$').all():
                                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                        except:
                            pass  # Keep as object/string
                
                # Store in memory
                self.tables[table_name] = df
                
                # Register with DuckDB
                self.conn.register(table_name, df)
                
                # Store metadata
                self.metadata[table_name] = {
                    "original_name": csv_file.name,
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict()
                }
                
                logger.info(f"✓ Loaded {table_name}: {len(df)} rows, {len(df.columns)} columns")
                
            except Exception as e:
                logger.error(f"Error loading {csv_file.name}: {str(e)}")
                
        return self.tables
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Execute a SQL query using DuckDB"""
        try:
            result = self.conn.execute(query).fetchdf()
            return result
        except Exception as e:
            logger.error(f"Query execution error: {str(e)}")
            raise
    
    def get_table_info(self, table_name: Optional[str] = None) -> Dict:
        """Get information about tables"""
        if table_name:
            return self.metadata.get(table_name, {})
        return self.metadata
    
    def get_sample_data(self, table_name: str, n: int = 5) -> pd.DataFrame:
        """Get sample rows from a table"""
        if table_name in self.tables:
            return self.tables[table_name].head(n)
        return pd.DataFrame()
    
    def get_summary_statistics(self, table_name: str) -> Dict:
        """Get summary statistics for a table"""
        if table_name not in self.tables:
            return {}
        
        df = self.tables[table_name]
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_summary": df.describe().to_dict() if not df.select_dtypes(include='number').empty else {},
            "missing_values": df.isnull().sum().to_dict(),
            "column_types": df.dtypes.astype(str).to_dict()
        }
        return summary
    
    def get_all_tables(self) -> List[str]:
        """Get list of all loaded tables"""
        return list(self.tables.keys())
    
    def search_columns(self, keyword: str) -> Dict[str, List[str]]:
        """Search for columns containing a keyword across all tables"""
        results = {}
        for table_name, df in self.tables.items():
            matching_cols = [col for col in df.columns if keyword.lower() in col.lower()]
            if matching_cols:
                results[table_name] = matching_cols
        return results
    
    @staticmethod
    def _sanitize_table_name(name: str) -> str:
        """Convert filename to valid SQL table name"""
        # Replace spaces and special chars with underscores
        name = name.replace(" ", "_").replace("-", "_").replace("&", "and")
        # Remove other special characters
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        # Ensure it starts with a letter
        if name[0].isdigit():
            name = f"table_{name}"
        return name.lower()
    
    @staticmethod
    def _sanitize_column_name(name: str) -> str:
        """Convert column name to valid SQL column name"""
        name = str(name).strip()
        name = name.replace(" ", "_").replace("-", "_")
        name = ''.join(c for c in name if c.isalnum() or c == '_')
        return name.lower()
    
    def get_schema_description(self) -> str:
        """Generate a comprehensive schema description for LLM context"""
        description = "# Available Tables and Schema\n\n"
        description += "**IMPORTANT**: Only use the exact table names listed below. Do NOT create or assume other table names.\n\n"
        description += f"**Total tables available: {len(self.metadata)}**\n\n"
        
        for table_name, meta in self.metadata.items():
            description += f"## Table: `{table_name}`\n"
            description += f"- Original file: {meta['original_name']}\n"
            description += f"- Rows: {meta['rows']:,}\n"
            description += f"- Columns ({len(meta['columns'])}): {', '.join([f'`{col}`' for col in meta['columns']])}\n\n"
            
            # Get column types and detect date columns
            df = self.tables[table_name]
            description += "Column types:\n"
            date_columns = []
            for col in meta['columns']:
                dtype = str(df[col].dtype)
                description += f"  - `{col}`: {dtype}"
                
                # Check if it looks like a date column
                if 'date' in col.lower() or 'time' in col.lower():
                    # Get a sample value to show format
                    sample_val = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    if sample_val:
                        description += f" (example: \"{sample_val}\")"
                        date_columns.append(col)
                description += "\n"
            
            if date_columns:
                description += f"\n**Date columns detected**: {', '.join([f'`{col}`' for col in date_columns])}\n"
                description += "Note: Use STRPTIME() to parse date strings. Common format appears to be MM-DD-YY ('%m-%d-%y')\n"
            description += "\n"
            
            # Sample data
            sample = self.get_sample_data(table_name, 2)
            if not sample.empty:
                description += "Sample data (first 2 rows):\n```\n"
                description += sample.to_string(index=False, max_colwidth=50)
                description += "\n```\n\n"
        
        description += "\n---\n"
        description += "**REMINDER**: Use ONLY the table names listed above (e.g., `amazon_sale_report`, `sale_report`, etc.). "
        description += "Do NOT use names like `all_sales` or `sales_data` unless they are explicitly listed.\n"
        
        return description
    
    def generate_insights(self) -> Dict:
        """Generate automated insights from all datasets"""
        insights = {}
        
        for table_name, df in self.tables.items():
            table_insights = []
            
            # Look for date columns
            date_cols = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower()]
            
            # Look for amount/revenue columns
            amount_cols = [col for col in df.columns if any(term in col.lower() 
                          for term in ['amount', 'amt', 'revenue', 'sales', 'gross', 'rate', 'mrp', 'price'])]
            
            # Look for quantity columns
            qty_cols = [col for col in df.columns if any(term in col.lower() 
                       for term in ['qty', 'quantity', 'pcs', 'stock', 'count'])]
            
            # Calculate basic metrics
            if amount_cols:
                for col in amount_cols:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        total = df[col].sum()
                        avg = df[col].mean()
                        table_insights.append(f"Total {col}: {total:,.2f}, Average: {avg:,.2f}")
            
            if qty_cols:
                for col in qty_cols:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        total = df[col].sum()
                        table_insights.append(f"Total {col}: {total:,.0f}")
            
            insights[table_name] = table_insights
        
        return insights


if __name__ == "__main__":
    # Test the data manager
    # When running from src folder, data is in parent/Sales Dataset
    data_dir = Path(__file__).parent.parent / "Sales Dataset"
    dm = DataManager(str(data_dir))
    dm.load_all_datasets()
    
    print("\n=== Loaded Tables ===")
    for table in dm.get_all_tables():
        print(f"- {table}")
    
    print("\n=== Schema Description ===")
    print(dm.get_schema_description())
    
    print("\n=== Auto-generated Insights ===")
    insights = dm.generate_insights()
    for table, insights_list in insights.items():
        print(f"\n{table}:")
        for insight in insights_list:
            print(f"  - {insight}")
