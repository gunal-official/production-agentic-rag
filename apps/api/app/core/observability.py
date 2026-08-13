from app.core.config import settings


def setup_observability():
    if not settings.phoenix_enabled:
        print("Phoenix observability disabled")
        return None

    from phoenix.otel import register

    tracer_provider = register(
        project_name="enterprise-agentic-rag",
        auto_instrument=True,
        batch=False,
    )

    print("Phoenix observability enabled")

    return tracer_provider