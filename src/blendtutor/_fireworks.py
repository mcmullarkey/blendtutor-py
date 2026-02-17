"""Fireworks API integration with httpx."""

from __future__ import annotations

import json
import os
import re

import httpx

from blendtutor._validators import BlendtutorError

FIREWORKS_BASE_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
DEFAULT_MODEL = "accounts/fireworks/models/qwen3-vl-30b-a3b-instruct"
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 3

SYSTEM_MESSAGE = (
    "You MUST call the respond_with_feedback tool exactly once. "
    "Pass ONLY these two arguments and no others:\n"
    "  - is_correct: true or false\n"
    "  - feedback_message: a short string (2-3 sentences)\n"
    "Do not add extra arguments. Do not output JSON manually. Use the tool."
)


def validate_fireworks_available() -> str:
    """Check FIREWORKS_API_KEY env var and return it.

    Raises:
        BlendtutorError: If the key is not set.
    """
    api_key = os.environ.get("FIREWORKS_API_KEY", "")
    if not api_key:
        raise BlendtutorError(
            "FIREWORKS_API_KEY not found.\n"
            "Please set up your Fireworks API key to use AI-powered feedback:\n"
            "  1. Sign up at https://fireworks.ai\n"
            "  2. Get your API key from https://fireworks.ai/api-keys\n"
            "  3. Add to your environment: export FIREWORKS_API_KEY=your_key_here\n"
            "     (Or add it to a .env file)\n"
            "  4. Restart your session and try submit_code() again."
        )
    return api_key


def define_fireworks_feedback_tool() -> dict:
    """Return the tool definition dict for structured feedback (OpenAI format)."""
    return {
        "type": "function",
        "function": {
            "name": "respond_with_feedback",
            "description": "Provide structured feedback on student code",
            "parameters": {
                "type": "object",
                "required": ["is_correct", "feedback_message"],
                "properties": {
                    "is_correct": {
                        "type": "boolean",
                        "description": (
                            "true if code meets requirements, false otherwise"
                        ),
                    },
                    "feedback_message": {
                        "type": "string",
                        "description": "Brief, encouraging feedback (2-3 sentences)",
                    },
                },
            },
        },
    }


def _build_request_payload(model: str, prompt: str, tools: list[dict]) -> dict:
    """Build the JSON body for a chat completions request."""
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
        "tools": tools,
    }


def _perform_request(payload: dict, api_key: str, model: str) -> dict:
    """POST to Fireworks API with retry loop and error classification."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    last_error: Exception | None = None
    for _attempt in range(MAX_RETRIES):
        try:
            resp = httpx.post(
                FIREWORKS_BASE_URL,
                json=payload,
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code
            if status in (401, 403):
                raise BlendtutorError(
                    "Authentication failed.\n"
                    "Please check your FIREWORKS_API_KEY.\n"
                    "Get your key from: https://fireworks.ai/api-keys"
                ) from e
            if status == 404:
                raise BlendtutorError(
                    f"Model '{model}' not found.\n"
                    "Check available models at: https://fireworks.ai/models"
                ) from e
            if status == 429:
                last_error = e
                continue
            raise BlendtutorError(f"Error calling Fireworks API.\n{e}") from e
        except httpx.TimeoutException as e:
            last_error = e
            continue
        except httpx.RequestError as e:
            last_error = e
            continue

    if last_error is not None:
        if (
            isinstance(last_error, httpx.HTTPStatusError)
            and last_error.response.status_code == 429
        ):
            raise BlendtutorError(
                "Rate limit exceeded. Please wait a moment and try again."
            ) from last_error
        raise BlendtutorError(
            f"Error calling Fireworks API.\n{last_error}"
        ) from last_error

    raise BlendtutorError("Error calling Fireworks API: max retries exceeded.")


def extract_tool_call(body: dict) -> dict | None:
    """Find the first respond_with_feedback tool call in the response."""
    choices = body.get("choices")
    if not choices:
        return None

    message = choices[0].get("message", {})
    tool_calls = message.get("tool_calls")
    if not tool_calls:
        return None

    tool_call = tool_calls[0]
    func = tool_call.get("function", {})
    if func.get("name") != "respond_with_feedback":
        return None

    return tool_call


def parse_feedback_arguments(tool_call: dict) -> dict | None:
    """Parse is_correct and feedback_message from a tool call's JSON arguments."""
    raw_args = tool_call.get("function", {}).get("arguments", "")
    try:
        args = json.loads(raw_args)
    except (json.JSONDecodeError, TypeError):
        return None

    # Extract feedback_message, handling nested dict case
    feedback_message = args.get("feedback_message", "")
    if isinstance(feedback_message, dict):
        feedback_message = feedback_message.get("description", "")
    if not isinstance(feedback_message, str):
        feedback_message = str(feedback_message) if feedback_message else ""

    is_correct = args.get("is_correct", False)
    if isinstance(is_correct, str):
        is_correct = is_correct.lower() == "true"
    is_correct = bool(is_correct)

    return {"is_correct": is_correct, "feedback": feedback_message}


def extract_text_fallback(body: dict) -> dict | None:
    """Extract feedback from text content when no tool call was made."""
    choices = body.get("choices")
    if not choices:
        return None

    content = (choices[0].get("message", {}).get("content") or "").strip()
    if not content:
        return None

    is_correct = bool(
        re.search(r"correct", content, re.IGNORECASE)
        and not re.search(r"incorrect|not correct|does not", content, re.IGNORECASE)
    )
    return {"is_correct": is_correct, "feedback": content}


def parse_fireworks_tool_response(body: dict) -> dict | None:
    """Orchestrate tool call extraction and argument parsing."""
    tool_call = extract_tool_call(body)
    if tool_call is None:
        return None
    return parse_feedback_arguments(tool_call)


def call_fireworks_with_tools(model: str, prompt: str) -> dict:
    """Main entry: validate API key, build request, perform, parse response."""
    api_key = validate_fireworks_available()
    tools = [define_fireworks_feedback_tool()]
    payload = _build_request_payload(model, prompt, tools)
    body = _perform_request(payload, api_key, model)

    result = parse_fireworks_tool_response(body)
    if result is not None:
        return result

    fallback = extract_text_fallback(body)
    if fallback is not None:
        return fallback

    return {
        "is_correct": False,
        "feedback": "Unable to parse LLM response. Please try again.",
    }


def evaluate_with_llm(
    student_code: str,
    exercise_prompt: str,
    model: str | None = None,
) -> dict:
    """Substitute {student_code} into the prompt and call the API."""
    if model is None:
        model = DEFAULT_MODEL
    full_prompt = exercise_prompt.replace("{student_code}", student_code)
    return call_fireworks_with_tools(model, full_prompt)
