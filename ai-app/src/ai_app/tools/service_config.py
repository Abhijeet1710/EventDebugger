from langchain.tools import tool

from ai_app.config.services import SERVICE_CONFIGS


@tool
def get_service_config(service_name: str) -> dict:
    """
    Get the onboarding configuration for a service.

    Returns the service's Splunk configuration,
    event identifier configuration, and processing stages.
    """
    config = SERVICE_CONFIGS.get(service_name)

    if not config:
        return {
            "error": f"Service '{service_name}' is not onboarded."
        }

    return config