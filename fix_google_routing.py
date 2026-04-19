with open("execution/hermes-agent/hermes_cli/auth.py", "r") as f:
    auth_data = f.read()
auth_data = auth_data.replace(
    'inference_base_url="https://generativelanguage.googleapis.com/v1beta/openai"',
    'inference_base_url=""'
)
with open("execution/hermes-agent/hermes_cli/auth.py", "w") as f:
    f.write(auth_data)

with open("execution/hermes-agent/cli.py", "r") as f:
    cli_data = f.read()
cli_data = cli_data.replace(
    'if not isinstance(base_url, str) or not base_url:',
    'if not isinstance(base_url, str):'
)
with open("execution/hermes-agent/cli.py", "w") as f:
    f.write(cli_data)
