import logging
import socket
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# The OpenInference bridge specifically formats LLM data
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from pydantic_ai import Agent

# Suppress noisy telemetry export errors
logging.getLogger("opentelemetry.sdk.trace.export").setLevel(logging.CRITICAL)


def _is_phoenix_running(host="127.0.0.1", port=6006, timeout=0.5):
    """Check if Phoenix is running by attempting a socket connection."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def init_telemetry(project_name: str = "second-brain-blog"):
    """Initializes OpenTelemetry and routes traces to Arize Phoenix."""
    # Check if Phoenix is running before setting up telemetry
    if not _is_phoenix_running():
        print(f"⚠️  Telemetry disabled (Phoenix not running). Start with: uvx arize-phoenix serve")
        return
    
    try:
        # Phoenix runs locally on port 6006 by default
        endpoint = "http://127.0.0.1:6006/v1/traces"

        # 1. Name your project (this appears in the Phoenix sidebar)
        resource = Resource.create({"openinference.project.name": project_name})

        # 2. Set up the Tracer Provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # 3. Add the OpenInference Processor FIRST so it enriches spans
        #    (sets span kinds, LLM attributes, status codes, etc.)
        #    BEFORE they are handed off to the exporter.
        tracer_provider.add_span_processor(OpenInferenceSpanProcessor())

        # 4. Add the Exporter SECOND (sends already-enriched spans to Phoenix)
        # Use BatchSpanProcessor instead of SimpleSpanProcessor for better error handling
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
        )

        # 5. The Magic Line: Auto-instrument all Pydantic AI agents
        Agent.instrument_all()

        print(f"📡 Telemetry online. Dashboard available at http://localhost:6006")
    except Exception as e:
        print(f"⚠️  Telemetry setup failed: {e}")
