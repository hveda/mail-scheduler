# -*- coding: utf-8 -*-
"""
Flask CLI script.
Set environment variable FLASK_APP=serve.py.
"""
from flask import jsonify, redirect, url_for

from app import config, create_app

app = create_app(config.DevelopmentConfig)


@app.route("/")
def index():
    """Redirect root URL to auth login page."""
    # Use url_for to generate the correct URL
    return redirect(url_for("auth.login"))


@app.route("/api-docs")
def api_docs():
    """Redirect to the API documentation."""
    return redirect("/api/doc")


@app.route("/debug")
def debug_info():
    """Show debug information about the application."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(
            {
                "endpoint": rule.endpoint,
                "methods": [
                    method
                    for method in rule.methods
                    if method != "OPTIONS" and method != "HEAD"
                ],
                "path": str(rule),
            }
        )

    return jsonify(
        {
            "routes": sorted(routes, key=lambda x: x["endpoint"]),
            "blueprints": list(app.blueprints.keys()),
            "config": {
                k: str(v) for k, v in app.config.items() if k not in ["SECRET_KEY"]
            },
        }
    )


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return jsonify(error=str(e), message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify(error=str(e), message="Internal server error"), 500
