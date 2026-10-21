#!/usr/bin/env python3
"""Builds api-reference/openapi.json from the product's OpenAPI file.

The product (services/platform) writes Swagger 2.0 from its annotations;
Mintlify reads OpenAPI 3. This converts it with swagger2openapi (npx) and
then sets what the product's file does not say: the API's title and
description for a customer, the server placeholder, the security schemes,
and example hosts in place of any environment's.

    python3 scripts/openapi.py [path/to/swagger.json]   # write
    python3 scripts/openapi.py --check                   # the file is normalized

The default input is the product's file beside this site when the site is
checked out as the product's submodule (docs/site).
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "api-reference" / "openapi.json"
DEFAULT_IN = ROOT.parent.parent / "services" / "platform" / "docs" / "swagger.json"

INFO = {
    "title": "OpenController API",
    "description": (
        "The OpenController API is what the console runs on, and what your own scripts, pipelines and services "
        "call. It lists the AI agents and the assets they use across your connected clouds, starts discovery "
        "scans, registers agents and records who owns them, evaluates security posture, tries text against "
        "guardrails, and reads the runs your agents send as traces. Every route under /v1 takes a service-account "
        "key as a bearer credential, needs the permission the caller's role holds, and answers errors as RFC 9457 "
        "problem documents."
    ),
}
SERVERS = [{"url": "https://<your-opencontroller-host>", "description": "Your OpenController installation"}]
SECURITY_SCHEMES = {
    "serviceAccountKey": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "cpk_<key id>_<secret>",
        "description": (
            "A service-account key minted in Settings > Service accounts, sent as `Authorization: Bearer cpk_...`. "
            "The same key is also accepted in the `X-API-Key` header; the Authorization header wins when both are "
            "sent. Keys are kept only as SHA-256 hashes; disabling the account or revoking the key stops it at once."
        ),
    },
    "apiKeyHeader": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "The same service-account key, in the `X-API-Key` header, for clients that cannot set an Authorization header.",
    },
}
SECURITY = [{"serviceAccountKey": []}, {"apiKeyHeader": []}]

# Hosts an example may carry from the environment the product was annotated
# in, replaced with example hosts.
HOSTS = [
    (re.compile(r"https://rekori\.[a-z0-9.-]*opencontroller\.sh"), "https://gateway.opencontroller.example.com"),
    (re.compile(r"https://[a-z0-9.-]*opencontroller\.sh"), "https://opencontroller.example.com"),
]


def normalize(doc: dict) -> dict:
    doc["info"] = {**doc.get("info", {}), **INFO}
    doc["servers"] = SERVERS
    doc.setdefault("components", {})["securitySchemes"] = SECURITY_SCHEMES
    doc["security"] = SECURITY
    text = json.dumps(doc, indent=2, ensure_ascii=False)
    for host, example in HOSTS:
        text = host.sub(example, text)
    return json.loads(text)


def dump(doc: dict) -> str:
    return json.dumps(doc, indent=2, ensure_ascii=False) + "\n"


def convert(swagger: Path) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        subprocess.run(["npx", "-y", "swagger2openapi", str(swagger), "-o", tmp.name], check=True, capture_output=True)
        return json.load(open(tmp.name))


def main() -> int:
    if "--check" in sys.argv:
        current = json.load(open(OUT))
        if dump(normalize(current)) != dump(current):
            print("api-reference/openapi.json is not normalized: run python3 scripts/openapi.py", file=sys.stderr)
            return 1
        print("openapi: normalized")
        return 0
    swagger = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_IN
    if not swagger.exists():
        print(f"no OpenAPI file at {swagger}: pass the product's swagger.json", file=sys.stderr)
        return 1
    doc = normalize(convert(swagger))
    OUT.write_text(dump(doc))
    print(f"openapi: {len(doc['paths'])} paths from {swagger}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
