#!/usr/bin/env python3
"""Statically pin fastmcp_slim/pyproject.toml for a non-uv Debian build.

Upstream split fastmcp into a thin "fastmcp" meta-package plus the real
"fastmcp-slim" package (workspace member fastmcp_slim/), with version and
optional-dependencies resolved dynamically via uv-dynamic-versioning /
hatch hooks. dh_auto_configure (pybuild + hatchling) can't resolve those
hooks, so this script rewrites a working copy with a hardcoded version and
a flattened, static dependency list covering the base + mcp + client +
server extras (the feature set previously shipped as a single
python3-fastmcp package).
"""

import re
import sys

DEPENDENCIES = """dependencies = [
    "authlib>=1.6.11",
    "cyclopts>=4.0.0",
    "exceptiongroup>=1.2.2",
    "griffelib>=2.0.0",
    "httpx2>=2.5.0",
    "joserfc>=1.5.0",
    "jsonref>=1.1.0",
    "jsonschema-path>=0.3.4",
    "mcp>=2.0.0",
    "mcp-types>=2.0.0",
    "openapi-pydantic>=0.5.1",
    "opentelemetry-api>=1.28.0",
    "packaging>=24.0",
    "platformdirs>=4.0.0",
    "py-key-value-aio[filetree,keyring,memory]>=0.4.4,<0.5.0",
    "pydantic[email]>=2.12.0",
    "pydantic-settings>=2.0.0",
    "pyperclip>=1.9.0",
    "python-dotenv>=1.1.0",
    "python-multipart>=0.0.26",
    "pyyaml>=6.0,<7.0",
    "rich>=13.9.4",
    "starlette>=1.0.1",
    "typing-extensions>=4.0.0",
    "uncalled-for>=0.4.0",
    "uvicorn>=0.35",
    "watchfiles>=1.0.0",
    "websockets>=15.0.1",
]
"""


def patch(path: str, version: str) -> None:
    text = open(path, encoding="utf-8").read()

    text = text.replace('name = "fastmcp-slim"', 'name = "fastmcp"')
    text = text.replace(
        'dynamic = ["version", "optional-dependencies"]',
        f'version = "{version}"',
    )
    text = text.replace(
        'requires = ["hatchling", "uv-dynamic-versioning>=0.7.0"]',
        'requires = ["hatchling"]',
    )
    text = re.sub(
        r'\[tool\.hatch\.version\]\nsource = "uv-dynamic-versioning"\n\n', "", text
    )
    text = re.sub(
        r"\[tool\.uv-dynamic-versioning\]\n(?:.+\n)+?\n", "", text
    )
    text = re.sub(
        r"\[tool\.hatch\.metadata\.hooks\.uv-dynamic-versioning\.optional-dependencies\]\n"
        r"(?:.*\n)*?(?=\n|\Z)",
        "",
        text,
    )
    text, count = re.subn(
        r"dependencies = \[\n(?:.*\n)*?\]\n", DEPENDENCIES, text, count=1
    )
    if count != 1:
        raise RuntimeError("could not locate dependencies = [...] block to replace")

    open(path, "w", encoding="utf-8").write(text)


if __name__ == "__main__":
    patch(sys.argv[1], sys.argv[2])
