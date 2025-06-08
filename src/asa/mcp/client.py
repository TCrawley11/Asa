from fastmcp import Client
from fastmcp.client.auth import OAuth

oauth = OAuth(mcp_url="gotta fill this hoe in later")

async with Client("gotta fill this hoe in later", auth=oauth) as client:
    await client.ping()
