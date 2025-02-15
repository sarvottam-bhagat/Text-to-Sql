import pandas as pd
from sqlalchemy import create_engine, text
import os
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine('sqlite:///data.db')
        self.current_table = None

    def load_csv(self, csv_file: str, table_name: str) -> Dict[str, Any]:
        """Load CSV file into SQLite database and return table info"""
        df = pd.read_csv(csv_file)
        self.current_table = table_name
        
        # Clean column names (remove spaces, special characters)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Save to SQLite
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)
        
        # Get column descriptions
        column_descriptions = {col: str(df[col].dtype) for col in df.columns}
        
        # Get sample data
        sample_data = df.head(5).to_dict('records')
        
        return {
            "table_name": table_name,
            "column_descriptions": column_descriptions,
            "sample_data": sample_data
        }

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query and return results"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                return [dict(row._mapping) for row in result]
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")

    def get_table_info(self) -> Dict[str, Any]:
        """Get current table information"""
        if not self.current_table:
            raise Exception("No table is currently loaded")
            
        query = f"SELECT * FROM {self.current_table} LIMIT 5"
        sample_data = self.execute_query(query)
        
        # Get column information
        df = pd.read_sql(f"SELECT * FROM {self.current_table} LIMIT 1", self.engine)
        column_descriptions = {col: str(df[col].dtype) for col in df.columns}
        
        return {
            "table_name": self.current_table,
            "column_descriptions": column_descriptions,
            "sample_data": sample_data
        } 