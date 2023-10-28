from flask import Flask, render_template, request
# monitoring and observability
from flask_opentracing import FlaskTracing
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from jaeger_client import Config
from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics
# This library allows tracing HTTP requests made by the requests library.
from opentelemetry.instrumentation.requests import RequestsInstrumentor


def init_tracer(service):

    config = Config(
        config={
            "sampler": {"type": "const", "param": 1},
            "logging": True,
            "reporter_batch_size": 1,
        },
        service_name=service,
        validate=True,
        metrics_factory=PrometheusMetricsFactory(service_name_label=service),
    )

    # this call also sets opentracing.tracer
    return config.initialize_tracer()


app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
metrics = GunicornInternalPrometheusMetrics(app, group_by='endpoint')

tracer = init_tracer("frontend")
flask_tracer = FlaskTracing(tracer, True, app)


@app.route("/")
def homepage():
    with tracer.start_span("homepage") as span:
        span.set_tag("response", "render_template")
        return render_template("main.html")


if __name__ == "__main__":
    app.run()
