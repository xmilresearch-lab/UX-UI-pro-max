#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max HTTP API Server

Exposes the search and design-system functionality over HTTP.
Uses only Python stdlib — no external dependencies.

Usage:
    python server.py [--port 7331] [--host 127.0.0.1]

Endpoints:
    GET /health
    GET /search?q=<query>[&domain=<domain>][&stack=<stack>][&n=3][&format=json|text]
    GET /design-system?q=<query>[&project=<name>][&format=ascii|markdown]
"""

import json
import sys
import io
import argparse
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

# Ensure scripts directory is on path so core/design_system imports work
sys.path.insert(0, str(__file__[:__file__.rfind("/")]))

from core import CSV_CONFIG, AVAILABLE_STACKS, MAX_RESULTS, search, search_stack
from design_system import generate_design_system

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 7331


def _json(data: dict | list, status: int = 200) -> tuple[int, str]:
    return status, json.dumps(data, ensure_ascii=False, indent=2)


def _error(message: str, status: int = 400) -> tuple[int, str]:
    return _json({"error": message}, status)


def handle_health() -> tuple[int, str]:
    return _json({"status": "ok", "service": "ui-ux-pro-max"})


def handle_search(params: dict) -> tuple[int, str]:
    q = (params.get("q") or params.get("query") or [""])[0].strip()
    if not q:
        return _error("Missing required param: q (search query)")

    domain = (params.get("domain") or params.get("d") or [None])[0]
    stack = (params.get("stack") or params.get("s") or [None])[0]
    fmt = (params.get("format") or params.get("f") or ["json"])[0].lower()
    try:
        n = int((params.get("n") or [str(MAX_RESULTS)])[0])
    except ValueError:
        n = MAX_RESULTS

    if domain and domain not in CSV_CONFIG:
        return _error(f"Unknown domain '{domain}'. Valid: {', '.join(CSV_CONFIG.keys())}")
    if stack and stack not in AVAILABLE_STACKS:
        return _error(f"Unknown stack '{stack}'. Valid: {', '.join(AVAILABLE_STACKS)}")

    if stack:
        result = search_stack(q, stack, n)
    else:
        result = search(q, domain, n)

    if fmt == "text":
        # Minimal text rendering for human-readable output
        lines = []
        for i, row in enumerate(result.get("results", []), 1):
            lines.append(f"--- Result {i} ---")
            for k, v in row.items():
                lines.append(f"{k}: {str(v)[:300]}")
        return 200, "\n".join(lines)

    return _json(result)


def handle_design_system(params: dict) -> tuple[int, str]:
    q = (params.get("q") or params.get("query") or [""])[0].strip()
    if not q:
        return _error("Missing required param: q (search query)")

    project = (params.get("project") or params.get("p") or [None])[0]
    fmt = (params.get("format") or params.get("f") or ["ascii"])[0].lower()
    if fmt not in ("ascii", "markdown"):
        fmt = "ascii"

    result = generate_design_system(q, project, fmt)
    return _json({"query": q, "project": project, "output": result})


class SkillHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        sys.stderr.write(f"[ui-ux-pro-max] {self.address_string()} - {format % args}\n")

    def send_response_with_body(self, status: int, body: str, content_type: str = "application/json"):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        path = parsed.path.rstrip("/") or "/"

        try:
            if path == "/health":
                status, body = handle_health()
                content_type = "application/json"
            elif path == "/search":
                status, body = handle_search(params)
                content_type = "application/json" if not body.startswith("---") else "text/plain"
            elif path == "/design-system":
                status, body = handle_design_system(params)
                content_type = "application/json"
            else:
                status, body = _error(f"Unknown endpoint: {path}. Available: /health, /search, /design-system", 404)
                content_type = "application/json"
        except Exception as exc:
            status, body = _error(f"Internal error: {exc}", 500)
            content_type = "application/json"

        self.send_response_with_body(status, body, content_type)


def run(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
    server = HTTPServer((host, port), SkillHandler)
    print(f"UI/UX Pro Max API listening on http://{host}:{port}", flush=True)
    print(f"  GET /health", flush=True)
    print(f"  GET /search?q=<query>[&domain=<domain>][&stack=<stack>][&n=3]", flush=True)
    print(f"  GET /design-system?q=<query>[&project=<name>][&format=ascii|markdown]", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.", flush=True)
        server.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UI/UX Pro Max HTTP API Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help=f"Bind host (default: {DEFAULT_HOST})")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Bind port (default: {DEFAULT_PORT})")
    args = parser.parse_args()
    run(args.host, args.port)
