import json
import logging
import os
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse

from agent_framework import Agent, tool
from agent_framework.anthropic import AnthropicFoundryClient
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic import Field
from azure.ai.agentserver.optimization import load_config, load_skills_from_dir

logger = logging.getLogger(__name__)

# With thinking on, agent-framework-anthropic 1.0.0b260910 sometimes drops Claude's final answer.
CLAUDE_THINKING_OFF = {"claude-sonnet-5-5": {"type": "between_tools"}}


@tool(approval_mode="never_require")
def lookup_travel_policy() -> str:
    """Look up the company travel policy rules and limits."""
    return json.dumps({
        "company": "Contoso Ltd.",
        "approval_thresholds": {
            "auto": 1500, "manager": 3000,
            "director": 7500, "vp": "above 7500"
        },
        "lodging_per_night": {"domestic": 250, "international": 400},
        "airfare": "economy only; business class if flight > 6 hours",
        "advance_booking_days": 14,
    })


@tool(approval_mode="never_require")
def check_department_budget() -> str:
    """Check the remaining travel budget for the employee's department."""
    return json.dumps({
        "department": "Engineering",
        "total_budget": 50000, "remaining": 14800,
    })


@tool(approval_mode="never_require")
def get_flight_alternatives(
    destination: Annotated[str, Field(description="The travel destination city")],
) -> str:
    """Find cheaper flight alternatives for the given destination."""
    return json.dumps({
        "alternatives": [
            {"option": "Flexible dates (±2 days)", "savings": "$200-800"},
            {"option": "Nearby alternate airport", "savings": "$100-400"},
        ],
    })


def create_chat_client(model: str, project_endpoint: str, credential: DefaultAzureCredential):
    if model.startswith("claude"):
        # Claude on Foundry is served by the Anthropic Messages API, not the OpenAI-compatible one.
        return AnthropicFoundryClient(
            model=model,
            resource=urlparse(project_endpoint).hostname.split(".")[0],
            azure_ad_token_provider=get_bearer_token_provider(
                credential, "https://ai.azure.com/.default"
            ),
        )
    return FoundryChatClient(
        project_endpoint=project_endpoint, model=model, credential=credential
    )


def main():
    # Load optimization config from .agent_configs/
    config = load_config()
    if config is None:
        raise RuntimeError(
            "No optimization config found. Ensure .agent_configs/baseline/ exists "
            "next to main.py, or that OPTIMIZATION_LOCAL_DIR points to an existing "
            "directory (relative paths resolve from main.py's folder)."
        )

    # Load skills from local directory if not provided by optimization
    if not config.skills and config.skills_dir:
        config.skills.extend(load_skills_from_dir(Path(config.skills_dir)))

    model = config.model or os.environ.get(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-5.4-mini"
    )
    instructions = config.compose_instructions()

    # Apply optimized tool descriptions
    tools = [lookup_travel_policy, check_department_budget, get_flight_alternatives]
    config.apply_tool_descriptions(tools)

    logger.info(
        "Config source=%s | model=%s | prompt_len=%d | skills=%d",
        config.source, model, len(instructions), len(config.skills),
    )

    client = create_chat_client(
        model, os.environ["FOUNDRY_PROJECT_ENDPOINT"], DefaultAzureCredential()
    )

    if isinstance(client, FoundryChatClient):
        default_options = {"store": False}
    elif model in CLAUDE_THINKING_OFF:
        default_options = {"thinking": CLAUDE_THINKING_OFF[model]}
    else:
        default_options = {}

    agent = Agent(
        client=client,
        instructions=instructions,
        tools=tools,
        # The Anthropic Messages API rejects the OpenAI-only `store` option.
        default_options=default_options,
    )

    server = ResponsesHostServer(agent)
    server.run()


if __name__ == "__main__":
    main()