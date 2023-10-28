from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
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
            "sampler": {
                "type": 'const',
                "param": 1,
            },
            "logging": True,
            "reporter_batch_size": 1,
        },
        service_name=service,
        validate=True,
        metrics_factory=PrometheusMetricsFactory(service_name_label=service)
    )
    return config.initialize_tracer()


app = Flask(__name__)
# fix CORS issue for local development
CORS(app)
tracer = init_tracer("backend")
flask_tracer = FlaskTracing(tracer, True, app)

FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
metrics = GunicornInternalPrometheusMetrics(app, group_by='endpoint')
metrics.info('backend_service_info', 'Backend Service info', version='1.0.0')

app.config["MONGO_DBNAME"] = "example-mongodb"
app.config[
    "MONGO_URI"
] = "mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb"

mongo = PyMongo(app)


@app.route("/")
def homepage():
    with tracer.start_span('homepage') as span:
        r = "Hello World"
        span.set_tag('response', r)
        return r


@app.route("/api")
def my_api():
    with tracer.start_span('api') as span:
        r = "something"
        span.set_tag('response', r)
        return jsonify(repsonse=r)


@app.route("/star", methods=["POST"])
def add_star():
    with tracer.start_span('add_star') as span:
        star = mongo.db.stars
        name = request.json["name"]
        distance = request.json["distance"]
        star_id = star.insert({"name": name, "distance": distance})
        new_star = star.find_one({"_id": star_id})
        output = {"name": new_star["name"], "distance": new_star["distance"]}
        span.set_tag('success', output)
        return jsonify({"result": output})


if __name__ == "__main__":
    app.run()
