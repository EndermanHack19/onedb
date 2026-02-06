"""
REST API for UnifyDB Web Dashboard.
"""

from flask import Flask, jsonify, request


def register_api(app: Flask):
    """Register API routes."""
    
    @app.route("/api/connections")
    def api_connections():
        """Get all connections."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        return jsonify({
            name: db.get_info()
            for name, db in connections.items()
        })
    
    @app.route("/api/connections/<name>/tables")
    def api_tables(name: str):
        """Get tables for connection."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if name not in connections:
            return jsonify({"error": "Connection not found"}), 404
        
        db = connections[name]
        return jsonify({"tables": db.get_tables()})
    
    @app.route("/api/connections/<name>/tables/<table>/columns")
    def api_columns(name: str, table: str):
        """Get columns for table."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if name not in connections:
            return jsonify({"error": "Connection not found"}), 404
        
        db = connections[name]
        return jsonify({"columns": db.get_columns(table)})
    
    @app.route("/api/connections/<name>/tables/<table>/data")
    def api_table_data(name: str, table: str):
        """Get table data with pagination."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if name not in connections:
            return jsonify({"error": "Connection not found"}), 404
        
        db = connections[name]
        
        # Pagination
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 50, type=int)
        
        result = db.find(
            table,
            limit=per_page,
            offset=(page - 1) * per_page
        )
        
        return jsonify({
            "data": result.data,
            "columns": result.columns,
            "page": page,
            "per_page": per_page
        })
    
    @app.route("/api/connections/<name>/query", methods=["POST"])
    def api_execute_query(name: str):
        """Execute SQL query."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if name not in connections:
            return jsonify({"error": "Connection not found"}), 404
        
        db = connections[name]
        data = request.get_json()
        query = data.get("query", "")
        
        try:
            result = db.execute(query)
            return jsonify({
                "success": True,
                "data": result.data,
                "columns": result.columns,
                "affected_rows": result.affected_rows,
                "execution_time": result.execution_time
            })
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
