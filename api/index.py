# Use a completely simplified app directly defined in vercel_app.py
from api.vercel_app import app

# For Vercel serverless deployment
handler = app


@app.route('/')
def index():
    """Redirect root URL to auth login page."""
    # Use url_for to generate the correct URL
    return redirect(url_for('auth.login'))


@app.route('/api-docs')
def api_docs():
    """Redirect to the API documentation."""
    return redirect('/api/doc')


@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors."""
    return jsonify(error=str(e), message="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify(error=str(e), message="Internal server error"), 500


# This is required for Vercel serverless functions
app.debug = False
app.config['SERVER_NAME'] = None


# For Vercel serverless deployment
handler = app
