#!/usr/bin/env python3
"""Test script for Hermes M2M endpoint.

Usage:
    python test_hermes_m2m.py                          # uses defaults from .env
    HERMES_API_KEY=real_key python test_hermes_m2m.py  # override key
    python test_hermes_m2m.py --url https://api.example.com  # override URL

Validates that the external Hermes AI agent can authenticate and read
the financial context snapshot via the static API key.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("httpx not installed. Run: pip install httpx")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Test Hermes M2M endpoint")
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Backend base URL (default: http://localhost:8000)")
    parser.add_argument("--key", default=None,
                        help="Hermes API key (default: reads HERMES_API_KEY env or .env)")
    args = parser.parse_args()

    # Resolve API key: CLI arg → env var → .env file fallback
    api_key = args.key or os.environ.get("HERMES_API_KEY")
    if not api_key:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("HERMES_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break

    if not api_key:
        print("ERROR: No HERMES_API_KEY found. Set via --key, HERMES_API_KEY env, or .env file.")
        sys.exit(1)

    url = f"{args.url.rstrip('/')}/api/v1/hermes/financial-context"
    headers = {"X-API-Key": api_key}

    print(f"Requesting: {url}")
    print(f"Headers:    X-API-Key: {api_key[:6]}...{api_key[-4:] if len(api_key) > 10 else ''}")

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, headers=headers)
    except httpx.ConnectError as e:
        print(f"ERROR: Connection failed — is the backend running?\n  {e}")
        sys.exit(1)
    except httpx.TimeoutException:
        print("ERROR: Request timed out after 15s.")
        sys.exit(1)

    print(f"\nStatus: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  total_transactions: {data['total_transactions']}")
        print(f"  total_income:       {data['total_income']}")
        print(f"  total_expenses:     {data['total_expenses']}")
        print(f"  recent samples:     {len(data['recent'])}")
        print("\n✓ Hermes M2M endpoint accessible and returning data.")
        sys.exit(0)
    elif resp.status_code == 403:
        print("✗ Access denied — check HERMES_API_KEY matches backend settings.")
        sys.exit(1)
    else:
        print(f"✗ Unexpected response: {resp.text[:500]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
