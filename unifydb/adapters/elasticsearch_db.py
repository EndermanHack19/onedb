"""
Elasticsearch Adapter.
"""

from typing import Any, Dict, List, Optional, Union
import time
import json

from ..core.base import BaseAdapter, ConnectionConfig, QueryResult, DatabaseType
from ..exceptions import ConnectionError, QueryError, DriverNotInstalledError


class Elasticsearch(BaseAdapter):
    """
    Elasticsearch adapter.
    
    Install:
        pip install unifydb[elasticsearch]
    """
    
    db_type = DatabaseType.ELASTICSEARCH
    driver_name = "elasticsearch"
    install_command = "pip install unifydb[elasticsearch]"
    
    def __init__(self, config: Optional[ConnectionConfig] = None, **kwargs):
        super().__init__(config, **kwargs)
        if self.config.port is None:
            self.config.port = 9200
        self._client = None
    
    def _import_driver(self):
        try:
            from elasticsearch import Elasticsearch as ES
            return ES
        except ImportError:
            raise DriverNotInstalledError("elasticsearch", self.install_command)
    
    def connect(self) -> None:
        ES = self._import_driver()
        
        try:
            hosts = [f"http://{self.config.host}:{self.config.port}"]
            
            auth = None
            if self.config.user and self.config.password:
                auth = (self.config.user, self.config.password)
            
            self._client = ES(
                hosts=hosts,
                basic_auth=auth,
                request_timeout=self.config.timeout
            )
            
            # Test connection
            self._client.info()
            self._is_connected = True
            
        except Exception as e:
            raise ConnectionError(
                f"Failed to connect to Elasticsearch: {e}",
                host=self.config.host,
                port=self.config.port
            )
    
    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
        self._is_connected = False
    
    def is_connected(self) -> bool:
        try:
            if self._client:
                self._client.ping()
                return True
        except Exception:
            pass
        return False
    
    def execute(
        self,
        query: str,
        params: Optional[Union[tuple, dict]] = None
    ) -> QueryResult:
        """Execute Elasticsearch query (expects JSON query)."""
        start_time = time.time()
        
        try:
            if isinstance(query, str):
                query_dict = json.loads(query)
            else:
                query_dict = query
            
            index = query_dict.pop("_index", self.config.database or "*")
            
            response = self._client.search(index=index, body=query_dict)
            
            result = QueryResult()
            result.data = [hit["_source"] for hit in response["hits"]["hits"]]
            
