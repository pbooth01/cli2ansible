"""OpenAI-based terminal session cleaner."""

import json
from typing import Any
from uuid import UUID

import httpx
from cli2ansible.domain.models import CleanedCommand, CleaningReport, Command
from cli2ansible.domain.ports import LLMPort


class OpenAICleaner(LLMPort):
    """Use OpenAI GPT to clean terminal sessions."""

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"

    def clean_commands(
        self, commands: list[Command], session_id: UUID
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """Analyze and clean terminal commands using OpenAI."""
        if not commands:
            return [], CleaningReport(
                session_id=session_id,
                original_command_count=0,
                cleaned_command_count=0,
                duplicates_removed=0,
                error_corrections_removed=0,
                cleaning_rationale="No commands to clean",
            )

        prompt = self._build_prompt(commands)
        response = self._call_api(prompt)
        return self._parse_response(response, commands, session_id)

    def _build_prompt(self, commands: list[Command]) -> str:
        """Build the prompt for OpenAI."""
        cmd_list = "\n".join(
            [
                f"{i+1}. {cmd.raw} (timestamp: {cmd.timestamp})"
                for i, cmd in enumerate(commands)
            ]
        )

        return f"""Analyze the following terminal session commands and identify which ones are essential.

Commands:
{cmd_list}

Your task:
1. Identify duplicate commands (same command run multiple times)
2. Identify error corrections (user made a typo and then fixed it)
3. Keep only the essential commands needed to reproduce the desired outcome

Return a JSON response with this structure:
{{
  "essential_commands": [
    {{
      "command": "the actual command",
      "reason": "why this command is essential",
      "is_duplicate": false,
      "is_error_correction": false,
      "first_occurrence_index": 0
    }}
  ],
  "removed_commands": [
    {{
      "command": "the removed command",
      "reason": "why it was removed (duplicate/error correction)",
      "is_duplicate": true,
      "is_error_correction": false,
      "original_index": 5
    }}
  ],
  "rationale": "overall explanation of cleaning decisions"
}}

Focus on:
- Commands that accomplish the goal (keep)
- Obvious typos followed by corrections (remove the typo)
- Repeated identical commands (keep only first occurrence)
- Failed commands followed by successful ones (remove failures)"""

    def _call_api(self, prompt: str) -> dict[str, Any]:
        """Call the OpenAI API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a terminal session analyzer. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                result: dict[str, Any] = response.json()
                return result
        except httpx.HTTPStatusError as e:
            # Don't expose response content in error
            raise RuntimeError(
                f"OpenAI API request failed with status {e.response.status_code}"
            ) from e
        except httpx.TimeoutException as e:
            raise RuntimeError("OpenAI API request timed out") from e
        except Exception as e:
            raise RuntimeError("Failed to call OpenAI API") from e

    def _parse_response(
        self,
        response: dict[str, Any],
        original_commands: list[Command],
        session_id: UUID,
    ) -> tuple[list[CleanedCommand], CleaningReport]:
        """Parse OpenAI's response into cleaned commands and report."""
        choices = response.get("choices", [])
        if not choices:
            raise ValueError("Empty response from API")

        message = choices[0].get("message", {})
        content = message.get("content", "")

        if not content:
            raise ValueError("Empty content in API response")

        data = json.loads(content)

        cleaned_commands: list[CleanedCommand] = []
        duplicates_removed = 0
        error_corrections_removed = 0

        # Process essential commands
        for cmd_data in data.get("essential_commands", []):
            idx = cmd_data.get("first_occurrence_index", 0)
            original_cmd = (
                original_commands[idx] if idx < len(original_commands) else None
            )

            if original_cmd:
                cleaned_commands.append(
                    CleanedCommand(
                        session_id=session_id,
                        command=cmd_data["command"],
                        reason=cmd_data["reason"],
                        first_occurrence=original_cmd.timestamp,
                        occurrence_count=1,
                        is_duplicate=cmd_data.get("is_duplicate", False),
                        is_error_correction=cmd_data.get("is_error_correction", False),
                    )
                )

        # Count removed items
        for removed in data.get("removed_commands", []):
            if removed.get("is_duplicate"):
                duplicates_removed += 1
            if removed.get("is_error_correction"):
                error_corrections_removed += 1

        report = CleaningReport(
            session_id=session_id,
            original_command_count=len(original_commands),
            cleaned_command_count=len(cleaned_commands),
            duplicates_removed=duplicates_removed,
            error_corrections_removed=error_corrections_removed,
            cleaning_rationale=data.get("rationale", ""),
        )

        return cleaned_commands, report
