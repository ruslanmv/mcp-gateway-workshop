import click
from ..utils.gateway_client import GatewayClient

@click.group()
def cli():
    "MCP Workshop CLI"
    pass

@cli.command("tools")
def list_tools():
    gw = GatewayClient()
    tools = gw.list_tools()
    for t in tools:
        name = t.get("name") or t.get("toolName") or "unknown"
        print("-", name)

@cli.command("call")
@click.argument("tool")
@click.argument("json_payload")
def call(tool: str, json_payload: str):
    import json
    gw = GatewayClient()
    res = gw.invoke(tool, json.loads(json_payload))
    print(res)

if __name__ == "__main__":
    cli()
