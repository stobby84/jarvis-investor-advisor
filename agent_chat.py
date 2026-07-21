import os
import sys
from dataclasses import dataclass
from typing import Optional

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

try:
    from azure.keyvault.secrets import SecretClient
except ImportError:  # pragma: no cover - optional dependency
    SecretClient = None

load_dotenv()


@dataclass
class AgentSettings:
    project_endpoint: str
    agent_name: str
    model: Optional[str] = None


def load_settings() -> AgentSettings:
    return AgentSettings(
        project_endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT", "").strip(),
        agent_name=os.getenv("AZURE_AI_AGENT_NAME", "").strip(),
        model=os.getenv("AZURE_AI_MODEL", "").strip() or None,
    )


def validate_settings(settings: AgentSettings) -> None:
    missing = []
    if not settings.project_endpoint:
        missing.append("AZURE_AI_PROJECT_ENDPOINT")
    if not settings.agent_name:
        missing.append("AZURE_AI_AGENT_NAME")

    if missing:
        raise ValueError(
            "Missing required environment variables: " + ", ".join(missing)
        )


def create_credential():
    key_vault_url = os.getenv("AZURE_KEY_VAULT_URL", "").strip()
    secret_name = os.getenv("AZURE_API_KEY_SECRET_NAME", "").strip()

    if not key_vault_url or not secret_name:
        raise ValueError(
            "API key mode requires AZURE_KEY_VAULT_URL and AZURE_API_KEY_SECRET_NAME"
        )

    if SecretClient is None:
        raise RuntimeError("azure-keyvault-secrets package is required for API key mode")

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    secret = client.get_secret(secret_name)
    return secret.value


def create_project_client(settings: AgentSettings) -> AIProjectClient:
    credential = create_credential()
    return AIProjectClient(endpoint=settings.project_endpoint, credential=credential)


def create_conversation(settings: AgentSettings):
    project_client = create_project_client(settings)
    openai_client = project_client.get_openai_client(agent_name=settings.agent_name)
    conversation = openai_client.conversations.create()
    return openai_client, conversation


def send_message(openai_client, conversation, message: str) -> str:
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=message,
    )
    return getattr(response, "output_text", "") or ""


def run_cli(settings: AgentSettings) -> None:
    print("Starting Azure Agent chat interface...")
    print("Type 'exit' or 'quit' to leave the conversation.\n")

    openai_client, conversation = create_conversation(settings)

    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            print("\nSession closed.")
            break

        if not user_input:
            continue

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        try:
            assistant_reply = send_message(openai_client, conversation, user_input)
        except Exception as exc:  # pragma: no cover - runtime path
            print(f"Assistant error: {exc}")
            continue

        print(f"Assistant: {assistant_reply or '[No reply returned]'}\n")


if __name__ == "__main__":
    try:
        settings = load_settings()
        validate_settings(settings)
        run_cli(settings)
    except ValueError as exc:
        print(str(exc))
        print("Create a .env file based on .env.example and fill in your Azure settings.")
        sys.exit(1)
    except Exception as exc:  # pragma: no cover - runtime path
        print(f"Unable to start the chat interface: {exc}")
        sys.exit(1)
