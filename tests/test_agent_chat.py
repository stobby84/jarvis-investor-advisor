import os
import unittest
from unittest.mock import patch

from agent_chat import AgentSettings, create_credential, load_settings, validate_settings


class AgentChatTests(unittest.TestCase):
    def test_validate_settings_accepts_required_values(self) -> None:
        settings = AgentSettings(project_endpoint="https://example.services.ai.azure.com/api/projects/demo", agent_name="demo-agent")
        validate_settings(settings)

    def test_validate_settings_requires_project_endpoint_and_agent_name(self) -> None:
        with self.assertRaises(ValueError):
            validate_settings(AgentSettings(project_endpoint="", agent_name=""))

    def test_load_settings_reads_auth_environment_variables(self) -> None:
        with patch.dict(
            os.environ,
            {
                "AZURE_AI_PROJECT_ENDPOINT": "https://example.services.ai.azure.com/api/projects/demo",
                "AZURE_AI_AGENT_NAME": "demo-agent",
                "AZURE_AI_MODEL": "gpt-4.1-mini",
                "AZURE_AUTH_MODE": "apikey",
                "AZURE_KEY_VAULT_URL": "https://example.vault.azure.net/",
                "AZURE_API_KEY_SECRET_NAME": "demo-secret",
            },
            clear=False,
        ):
            settings = load_settings()

        self.assertEqual(settings.auth_mode, "apikey")
        self.assertEqual(settings.key_vault_url, "https://example.vault.azure.net/")
        self.assertEqual(settings.api_key_secret_name, "demo-secret")

    def test_create_credential_returns_default_credential_for_apikey_mode(self) -> None:
        class FakeSecretClient:
            def __init__(self, vault_url, credential):
                self.vault_url = vault_url
                self.credential = credential

            def get_secret(self, secret_name):
                self.secret_name = secret_name
                return type("Secret", (), {"value": "demo-api-key"})()

        settings = AgentSettings(
            project_endpoint="https://example.services.ai.azure.com/api/projects/demo",
            agent_name="demo-agent",
            auth_mode="apikey",
            key_vault_url="https://example.vault.azure.net/",
            api_key_secret_name="demo-secret",
        )

        with patch("agent_chat.SecretClient", FakeSecretClient), patch("agent_chat.DefaultAzureCredential", return_value="fake-credential"):
            credential = create_credential(settings)

        self.assertEqual(credential, "fake-credential")


if __name__ == "__main__":
    unittest.main()
