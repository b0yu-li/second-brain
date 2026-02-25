# src/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# The OpenInference bridge specifically formats LLM data
from openinference.instrumentation.pydantic_ai import OpenInferenceSpanProcessor
from pydantic_ai import Agent


def init_telemetry(project_name: str = "second-brain-blog"):
    """Initializes OpenTelemetry and routes traces to Arize Phoenix."""
    # Phoenix runs locally on port 6006 by default
    endpoint = "http://127.0.0.1:6006/v1/traces"

    # 1. Name your project (this appears in the Phoenix sidebar)
    resource = Resource.create({"openinference.project.name": project_name})

    # 2. Set up the Tracer Provider
    tracer_provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(tracer_provider)

    # 3. Add the Exporter (Sends data to Phoenix)
    tracer_provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(endpoint=endpoint))
    )

    # 4. Add the Pydantic AI Processor (Formats the prompts/responses beautifully)
    tracer_provider.add_span_processor(OpenInferenceSpanProcessor())

    # 5. The Magic Line: Auto-instrument all Pydantic AI agents
    Agent.instrument_all()

    print(f"📡 Telemetry online. Dashboard available at http://localhost:6006")
