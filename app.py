from agent_chat import load_settings, run_cli, validate_settings


def main() -> None:
    settings = load_settings()
    validate_settings(settings)
    run_cli(settings)


if __name__ == "__main__":
    main()
