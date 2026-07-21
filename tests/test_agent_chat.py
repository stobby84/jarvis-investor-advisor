import unittest

from agent_chat import AgentSettings, validate_settings


class AgentChatTests(unittest.TestCase):
    def test_validate_settings_accepts_required_values(self) -> None:
        settings = AgentSettings(project_endpoint="https://example.services.ai.azure.com/api/projects/demo", agent_name="demo-agent")
        validate_settings(settings)

    def test_validate_settings_requires_project_endpoint_and_agent_name(self) -> None:
        with self.assertRaises(ValueError):
            validate_settings(AgentSettings(project_endpoint="", agent_name=""))


if __name__ == "__main__":
    unittest.main()
