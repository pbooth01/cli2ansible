"""Command-line interface for cli2ansible utilities."""

import json
import sys
from pathlib import Path

from cli2ansible.adapters.outbound.capture.asciinema_parser import parse_cast_file


def convert_cast_to_json(cast_file: str, output_file: str | None = None) -> None:
    """
    Convert an asciinema .cast file to human-readable JSON format.

    Args:
        cast_file: Path to .cast file
        output_file: Optional output file path (defaults to stdout)

    Raises:
        FileNotFoundError: If cast file doesn't exist
        ValueError: If cast file format is invalid
    """
    # Parse the cast file
    events = parse_cast_file(cast_file)

    # Convert events to JSON-serializable dicts
    events_json = [
        {
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "data": event.data,
            "sequence": event.sequence,
        }
        for event in events
    ]

    # Format as pretty JSON
    json_output = json.dumps(events_json, indent=2, ensure_ascii=False)

    # Write to file or stdout
    if output_file:
        Path(output_file).write_text(json_output + "\n", encoding="utf-8")
        print(f"Converted {len(events)} events to {output_file}", file=sys.stderr)
    else:
        print(json_output)


def main() -> None:
    """CLI entry point for cast-to-json conversion."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert asciinema .cast files to human-readable JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Output to stdout
  python -m cli2ansible.cli convert-cast recording.cast

  # Save to file
  python -m cli2ansible.cli convert-cast recording.cast -o output.json

  # Use with make
  make convert-cast CAST_FILE=recording.cast
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # convert-cast subcommand
    cast_parser = subparsers.add_parser(
        "convert-cast", help="Convert .cast file to JSON"
    )
    cast_parser.add_argument("cast_file", help="Path to .cast file")
    cast_parser.add_argument(
        "-o", "--output", help="Output file (default: stdout)", default=None
    )

    args = parser.parse_args()

    if args.command == "convert-cast":
        try:
            convert_cast_to_json(args.cast_file, args.output)
        except FileNotFoundError:
            print(f"Error: File not found: {args.cast_file}", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"Error: Invalid .cast file: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
