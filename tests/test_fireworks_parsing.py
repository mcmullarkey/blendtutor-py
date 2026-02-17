"""Tests for Fireworks response parsing helpers. No API calls needed."""

from blendtutor._fireworks import (
    extract_text_fallback,
    extract_tool_call,
    parse_feedback_arguments,
    parse_fireworks_tool_response,
)


# -- extract_text_fallback ---------------------------------------------------


def test_extract_text_fallback_returns_feedback_from_text():
    body = {
        "choices": [{"message": {"content": "The code is correct and works well."}}]
    }
    result = extract_text_fallback(body)
    assert result["is_correct"] is True
    assert result["feedback"] == "The code is correct and works well."


def test_extract_text_fallback_detects_incorrect():
    body = {"choices": [{"message": {"content": "The code is incorrect."}}]}
    result = extract_text_fallback(body)
    assert result["is_correct"] is False


def test_extract_text_fallback_returns_none_for_empty():
    body = {"choices": [{"message": {"content": ""}}]}
    assert extract_text_fallback(body) is None

    body2 = {"choices": [{"message": {"content": None}}]}
    assert extract_text_fallback(body2) is None


# -- extract_tool_call -------------------------------------------------------


def test_extract_tool_call_finds_feedback_call():
    body = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "respond_with_feedback",
                                "arguments": '{"is_correct": true, "feedback_message": "Great!"}',
                            }
                        }
                    ]
                }
            }
        ]
    }
    tc = extract_tool_call(body)
    assert tc["function"]["name"] == "respond_with_feedback"


def test_extract_tool_call_returns_none_for_empty_choices():
    assert extract_tool_call({"choices": []}) is None
    assert extract_tool_call({}) is None


def test_extract_tool_call_returns_none_when_no_tool_calls():
    body = {"choices": [{"message": {"content": "just text"}}]}
    assert extract_tool_call(body) is None


def test_extract_tool_call_returns_none_for_wrong_function():
    body = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "other_tool", "arguments": "{}"}}
                    ]
                }
            }
        ]
    }
    assert extract_tool_call(body) is None


# -- parse_feedback_arguments ------------------------------------------------


def test_parse_feedback_arguments_extracts_correct():
    tc = {
        "function": {
            "arguments": '{"is_correct": true, "feedback_message": "Well done!"}'
        }
    }
    result = parse_feedback_arguments(tc)
    assert result["is_correct"] is True
    assert result["feedback"] == "Well done!"


def test_parse_feedback_arguments_handles_false():
    tc = {
        "function": {
            "arguments": '{"is_correct": false, "feedback_message": "Try again."}'
        }
    }
    result = parse_feedback_arguments(tc)
    assert result["is_correct"] is False
    assert result["feedback"] == "Try again."


def test_parse_feedback_arguments_returns_none_for_invalid_json():
    tc = {"function": {"arguments": "not json {{{"}}
    assert parse_feedback_arguments(tc) is None


def test_parse_feedback_arguments_handles_nested_feedback():
    tc = {
        "function": {
            "arguments": '{"is_correct": true, "feedback_message": {"description": "Nested msg"}}'
        }
    }
    result = parse_feedback_arguments(tc)
    assert result["is_correct"] is True
    assert result["feedback"] == "Nested msg"


# -- parse_fireworks_tool_response -------------------------------------------


def test_parse_fireworks_tool_response_end_to_end():
    body = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {
                            "function": {
                                "name": "respond_with_feedback",
                                "arguments": '{"is_correct": false, "feedback_message": "Missing edge case."}',
                            }
                        }
                    ]
                }
            }
        ]
    }
    result = parse_fireworks_tool_response(body)
    assert result["is_correct"] is False
    assert result["feedback"] == "Missing edge case."


def test_parse_fireworks_tool_response_returns_none_when_no_tool_call():
    body = {"choices": [{"message": {"content": "just text"}}]}
    assert parse_fireworks_tool_response(body) is None
