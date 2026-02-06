"""
Web dashboard routes.
"""

from flask import Flask, render_template, redirect, url_for, request, flash


def register_routes(app: Flask):
    """Register web routes."""
    
    @app.route("/")
    def index():
        """Dashboard home page."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        return render_template("dashboard.html", connections=connections)
    
    @app.route("/tables/<connection_name>")
    def tables(connection_name: str):
        """View tables for connection."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if connection_name not in connections:
            flash(f"Connection '{connection_name}' not found", "error")
            return redirect(url_for("index"))
        
        db = connections[connection_name]
        tables_list = db.get_tables()
        
        return render_template(
            "tables.html",
            connection_name=connection_name,
            tables=tables_list,
            db_info=db.get_info()
        )
    
    @app.route("/query/<connection_name>", methods=["GET", "POST"])
    def query(connection_name: str):
        """SQL query interface."""
        connections = app.config.get("UNIFYDB_CONNECTIONS", {})
        
        if connection_name not in connections:
            flash(f"Connection '{connection_name}' not found", "error")
            return redirect(url_for("index"))
        
        db = connections[connection_name]
        result = None
        query_text = ""
        error = None
        
        if request.method == "POST":
            query_text = request.form.get("query", "")
            try:
                result = db.execute(query_text)
            except Exception as e:
                error = str(e)
        
        return render_template(
            "query.html",
            connection_name=connection_name,
            query=query_text,
            result=result,
            error=error
        )
