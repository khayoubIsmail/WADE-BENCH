import asyncio
import http.server
import os
import platform
import shutil
import socketserver
import threading
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


NODE_DIRS = [
    r"C:\Program Files\nodejs",
    r"C:\Program Files (x86)\nodejs",
]


def _find_npx() -> str:
    """Find npx executable, injecting Node.js path if needed on Windows."""
    if shutil.which("npx"):
        return "npx"

    if platform.system() == "Windows":
        for node_dir in NODE_DIRS:
            npx_cmd = Path(node_dir) / "npx.cmd"
            if npx_cmd.exists():
                os.environ["PATH"] = node_dir + os.pathsep + os.environ.get("PATH", "")
                return str(npx_cmd)

    return "npx"  # fallback


def _content_to_text(content: Any) -> str:
    """Convert MCP tool response content into readable text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            text = getattr(item, "text", None)
            if text:
                parts.append(text)
            else:
                parts.append(str(item))
        return "\n".join(parts)
    text = getattr(content, "text", None)
    if text:
        return text
    return str(content)


def _start_local_server(directory: Path) -> tuple:
    """Start a simple HTTP server serving `directory` on a free port."""

    class SilentHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(directory), **kwargs)

        def log_message(self, format, *args):
            pass  # suppress access logs

    httpd = socketserver.TCPServer(("127.0.0.1", 0), SilentHandler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd, port


async def collect_playwright_mcp_evidence_async(
    page_safe_path: str | Path,
    task_id: str,
    server_command: str = "npx",
    server_args: list[str] | None = None,
) -> dict:
    """
    Collect browser evidence using Playwright MCP.

    Serves the frozen HTML snapshot via a local HTTP server to bypass
    Playwright MCP's file:// protocol restriction. The page is still
    served from local disk — no live website access.
    """
    page_safe_path = Path(page_safe_path).resolve()

    if not page_safe_path.exists():
        raise FileNotFoundError(f"page.safe.html not found: {page_safe_path}")

    file_url = page_safe_path.as_uri()

    if server_args is None:
        server_args = ["@playwright/mcp@latest", "--headless"]

    trace = []

    # Serve the snapshot directory via local HTTP to bypass file:// restriction
    serve_dir = page_safe_path.parent
    httpd, port = _start_local_server(serve_dir)
    http_url = f"http://127.0.0.1:{port}/{page_safe_path.name}"

    trace.append({
        "step": "local_http_server",
        "serve_dir": str(serve_dir),
        "http_url": http_url,
        "file_url": file_url,
    })

    try:
        resolved_command = _find_npx()

        server_params = StdioServerParameters(
            command=resolved_command,
            args=server_args,
            env={**os.environ},
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools_result = await session.list_tools()
                tool_names = [tool.name for tool in tools_result.tools]

                trace.append({
                    "step": "list_tools",
                    "tool_names": tool_names,
                })

                def has_tool(name: str) -> bool:
                    return name in tool_names

                async def call_tool(name: str, args: dict) -> str:
                    result = await session.call_tool(name, args)
                    text = _content_to_text(result.content)
                    trace.append({
                        "step": "call_tool",
                        "tool": name,
                        "args": args,
                        "output_preview": text[:2000],
                    })
                    return text

                # 1. Navigate to local HTTP snapshot (bypasses file:// restriction)
                if has_tool("browser_navigate"):
                    navigate_text = await call_tool("browser_navigate", {"url": http_url})
                else:
                    raise RuntimeError(f"browser_navigate not found. Available: {tool_names}")

                # 2. Get browser/accessibility snapshot
                snapshot_text = ""
                if has_tool("browser_snapshot"):
                    snapshot_text = await call_tool("browser_snapshot", {})
                elif has_tool("browser_accessibility_snapshot"):
                    snapshot_text = await call_tool("browser_accessibility_snapshot", {})

                # 3. Optional screenshot through MCP
                screenshot_text = ""
                if has_tool("browser_take_screenshot"):
                    try:
                        screenshot_text = await call_tool("browser_take_screenshot", {})
                    except Exception as e:
                        trace.append({"step": "screenshot_error", "error": str(e)})

                return {
                    "file_url": file_url,
                    "http_url": http_url,
                    "available_mcp_tools": tool_names,
                    "navigation_result": navigate_text,
                    "mcp_browser_snapshot": snapshot_text,
                    "mcp_screenshot_result": screenshot_text,
                    "tool_trace": trace,
                }

    finally:
        try:
            httpd.shutdown()
        except Exception:
            pass


async def _collect_with_timeout(
    page_safe_path: str | Path,
    task_id: str,
    server_command: str,
    server_args: list[str] | None,
    timeout: float = 120.0,
) -> dict:
    return await asyncio.wait_for(
        collect_playwright_mcp_evidence_async(
            page_safe_path=page_safe_path,
            task_id=task_id,
            server_command=server_command,
            server_args=server_args,
        ),
        timeout=timeout,
    )


def collect_playwright_mcp_evidence(
    page_safe_path: str | Path,
    task_id: str,
    server_command: str = "npx",
    server_args: list[str] | None = None,
    timeout: float = 120.0,
) -> dict:
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                _collect_with_timeout(page_safe_path, task_id, server_command, server_args, timeout)
            )
        finally:
            loop.close()
    except (asyncio.TimeoutError, TimeoutError) as e:
        raise RuntimeError(f"Playwright MCP timed out after {timeout}s for {task_id}") from e
