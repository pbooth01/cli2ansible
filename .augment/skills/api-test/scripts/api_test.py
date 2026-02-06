#!/usr/bin/env python3
"""
API Testing Script

Tests cli2ansible API endpoints for debugging and demonstration.

Usage:
    python3 api_test.py <command> [OPTIONS]
"""

import argparse
import sys
from pathlib import Path

try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Run: poetry install")
    sys.exit(1)


DEFAULT_API_URL = "http://localhost:8000"


def check_health(api_url: str) -> bool:
    """Check API health."""
    print(f"🏥 Checking API health at {api_url}...\n")
    try:
        response = httpx.get(f"{api_url}/api/v1/health", timeout=5)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except httpx.ConnectError:
        print(f"   ❌ Cannot connect to {api_url}")
        print("   Make sure the API is running (docker-dev up or uvicorn)")
        return False


def create_session(api_url: str, name: str) -> str | None:
    """Create a new session."""
    print(f"📝 Creating session: {name}\n")
    try:
        response = httpx.post(
            f"{api_url}/api/v1/sessions", json={"name": name}, timeout=10
        )
        if response.status_code == 201:
            data = response.json()
            session_id = data["id"]
            print(f"   ✅ Session created: {session_id}")
            return session_id
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return None
    except httpx.ConnectError:
        print(f"   ❌ Cannot connect to {api_url}")
        return None


def ingest_cast(api_url: str, session_id: str, cast_file: str) -> bool:
    """Ingest a cast file into a session."""
    print(f"📥 Ingesting cast file: {cast_file}\n")

    if not Path(cast_file).exists():
        print(f"   ❌ File not found: {cast_file}")
        return False

    try:
        with open(cast_file, "rb") as f:
            files = {"file": (Path(cast_file).name, f, "application/octet-stream")}
            response = httpx.post(
                f"{api_url}/api/v1/sessions/{session_id}/cast", files=files, timeout=30
            )

        if response.status_code in (200, 201):
            data = response.json()
            print(f"   ✅ Ingested {data.get('event_count', '?')} events")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def compile_session(api_url: str, session_id: str) -> bool:
    """Compile a session to Ansible playbook."""
    print(f"🔧 Compiling session: {session_id}\n")
    try:
        response = httpx.post(
            f"{api_url}/api/v1/sessions/{session_id}/compile", timeout=60
        )
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Compilation successful!")
            print(f"   📦 Artifact: {data.get('artifact_url', 'N/A')}")
            print(f"   🔗 Download: {data.get('download_url', 'N/A')}")
            return True
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def full_demo(api_url: str, cast_file: str) -> bool:
    """Run full demo workflow."""
    print("🎬 Running full demo workflow\n")
    print("=" * 60 + "\n")

    # Health check
    if not check_health(api_url):
        return False

    print("\n" + "-" * 60 + "\n")

    # Create session
    name = f"Demo Session - {Path(cast_file).stem}"
    session_id = create_session(api_url, name)
    if not session_id:
        return False

    print("\n" + "-" * 60 + "\n")

    # Ingest cast file
    if not ingest_cast(api_url, session_id, cast_file):
        return False

    print("\n" + "-" * 60 + "\n")

    # Compile
    if not compile_session(api_url, session_id):
        return False

    print("\n" + "=" * 60)
    print("✅ Demo complete!")
    return True


def main():
    parser = argparse.ArgumentParser(description="Test cli2ansible API endpoints")
    parser.add_argument(
        "command",
        choices=["health", "create-session", "ingest", "compile", "full-demo"],
    )
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="API base URL")
    parser.add_argument("--session-id", help="Session ID")
    parser.add_argument("--cast-file", help="Path to .cast file")
    parser.add_argument("--name", default="Test Session", help="Session name")

    args = parser.parse_args()

    if args.command == "health":
        sys.exit(0 if check_health(args.api_url) else 1)
    elif args.command == "create-session":
        session_id = create_session(args.api_url, args.name)
        sys.exit(0 if session_id else 1)
    elif args.command == "ingest":
        if not args.session_id or not args.cast_file:
            print("❌ --session-id and --cast-file required")
            sys.exit(1)
        sys.exit(0 if ingest_cast(args.api_url, args.session_id, args.cast_file) else 1)
    elif args.command == "compile":
        if not args.session_id:
            print("❌ --session-id required")
            sys.exit(1)
        sys.exit(0 if compile_session(args.api_url, args.session_id) else 1)
    elif args.command == "full-demo":
        if not args.cast_file:
            args.cast_file = "tests/fixtures/demo.cast"
        sys.exit(0 if full_demo(args.api_url, args.cast_file) else 1)


if __name__ == "__main__":
    main()
