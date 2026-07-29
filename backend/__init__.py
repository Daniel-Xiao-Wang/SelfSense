import os

from flask import Flask, render_template
from flask_cors import CORS

from .endpoints.info import get_info
from ml.diagnose import Diagnosor

_diagnostic = None


def get_diagnostic():
    """Reuse one trained Diagnosor instance across requests."""
    global _diagnostic
    if _diagnostic is None:
        _diagnostic = Diagnosor()
    return _diagnostic


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    #app = Flask(__name__, instance_relative_config=True)
    app = Flask(__name__, template_folder="../frontend")
    CORS(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # /info endpoint for displaying the service info
    @app.route("/info")
    def info():
        return get_info()

    # /symptoms endpoint for displaying the symptoms
    @app.route("/symptoms")
    def symptoms():
        diagnostic = get_diagnostic()
        result = diagnostic.getSymptoms()
        return result

    # /generate endpoint for returning the diagnostic
    @app.route("/generate/<path:symptoms>")
    def generate(symptoms):
        diagnostic = get_diagnostic()
        parsed = [s.strip() for s in symptoms.split(",") if s.strip()]
        result = diagnostic.generate(parsed)
        print("RESULT: ", result)
        return result

    # /home for rending the Home page
    # not being used currently
    @app.route("/home")
    def home():
        diagnostic = Diagnosor()
        ss = diagnostic.getSymptoms()
        return render_template("index.html", symptoms=ss)

    # make url_for('index') == url_for('blog.index')
    # in another app, you might define a separate main index here with
    # app.route, while giving the blog blueprint a url_prefix, but for
    # the tutorial the blog will be the main index
    app.add_url_rule("/", endpoint="info")

    return app