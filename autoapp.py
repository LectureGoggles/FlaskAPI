from app.__init__ import create_app
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace import config_integration
import os

app = create_app()
middleware = FlaskMiddleware(
    app,
    exporter=AzureExporter(connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]),
    sampler=ProbabilitySampler(rate=1.0)
)
config_integration.trace_integrations(['sqlalchemy'])

if __name__ == "__main__":
    import logging
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', threaded=True)
