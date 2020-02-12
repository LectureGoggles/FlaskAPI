from app.__init__ import create_app
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace import config_integration

app = create_app()
middleware = FlaskMiddleware(app)
config_integration.trace_integrations(['sqlalchemy'])

if __name__ == "__main__":
    import logging
    logger = logging.getLogger('werkzeug')
    logger.addHandler(AzureLogHandler())
    logger.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', threaded=True)
