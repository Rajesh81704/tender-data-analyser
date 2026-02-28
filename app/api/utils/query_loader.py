import os
from pathlib import Path

class QueryLoader:
    def __init__(self, properties_file="app/api/dao/queries.properties"):
        self.queries = {}
        self._load_queries(properties_file)
    
    def _load_queries(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Properties file not found: {file_path}")
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.queries[key.strip()] = value.strip()
    
    def get_query(self, query_name):
        return self.queries.get(query_name, None)

# Singleton instance
query_loader = QueryLoader()
