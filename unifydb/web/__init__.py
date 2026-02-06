"""
UnifyDB Web Dashboard.
Optional web interface for database management.

Install:
    pip install unifydb[web]

Usage:
    from unifydb.web import create_app, run_server
    
    # Run standalone
    run_server(host="0.0.0.0", port=5000)
    
    # Or integrate with existing Flask app
    app = create_app()
"""

from typing import Optional


def create_app(config: Optional[dict] = None):
    """Create Flask application."""
    try:
        from .app import create_flask_app
        return create_flask_app(config)
    except ImportError:
        raise ImportError(
            "Web dependencies not installed. "
            "Install with: pip install unifydb[web]"
        )


def run_server(
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
    **kwargs
):
    """Run web dashboard server."""
    app = create_app()
    print(f"🚀 UnifyDB Dashboard running at http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, **kwargs)


__all__ = ["create_app", "run_server"]
