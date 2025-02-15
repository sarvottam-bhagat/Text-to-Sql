from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str
    
class QueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    error: Optional[str] = None

class DatasetInfo(BaseModel):
    table_name: str
    column_descriptions: Dict[str, str]
    sample_data: List[Dict[str, Any]] 