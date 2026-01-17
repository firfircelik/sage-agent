"""
Validation utilities for Sage Agent system.
"""

from typing import Dict, Any, List, Tuple


def validate_prompt(
    prompt: str, min_length: int = 1, max_length: int = 10000
) -> Tuple[bool, str]:
    """Validate prompt."""
    if not prompt:
        return False, "Prompt cannot be empty"

    if len(prompt) < min_length:
        return False, f"Prompt must be at least {min_length} characters"

    if len(prompt) > max_length:
        return False, f"Prompt must be at most {max_length} characters"

    return True, "Valid"


def validate_agent_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate agent configuration."""
    errors = []

    required_fields = ["name", "role", "goal", "backstory"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(config[field], str) or not config[field].strip():
            errors.append(f"Field '{field}' must be a non-empty string")

    if "agent_type" in config:
        valid_types = ["manager", "specialist"]
        if config["agent_type"] not in valid_types:
            errors.append(f"Invalid agent_type. Must be one of: {valid_types}")

    if "tools" in config:
        if not isinstance(config["tools"], list):
            errors.append("Field 'tools' must be a list")

    return len(errors) == 0, errors


def validate_task_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate task configuration."""
    errors = []

    required_fields = ["description", "agent", "expected_output"]
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")

    if "priority" in config:
        if not isinstance(config["priority"], int) or config["priority"] < 1:
            errors.append("Field 'priority' must be a positive integer")

    if "dependencies" in config:
        if not isinstance(config["dependencies"], list):
            errors.append("Field 'dependencies' must be a list")

    return len(errors) == 0, errors


def validate_llm_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate LLM configuration."""
    errors = []

    if "provider" not in config:
        errors.append("Missing required field: provider")
    else:
        valid_providers = ["openai", "anthropic", "local", "groq", "cohere", "mistral"]
        if config["provider"] not in valid_providers:
            errors.append(f"Invalid provider. Must be one of: {valid_providers}")

    if "model" not in config:
        errors.append("Missing required field: model")

    if "temperature" in config:
        temp = config["temperature"]
        if not isinstance(temp, (int, float)) or not (0 <= temp <= 2):
            errors.append("Field 'temperature' must be between 0 and 2")

    if "max_tokens" in config:
        tokens = config["max_tokens"]
        if not isinstance(tokens, int) or tokens < 1:
            errors.append("Field 'max_tokens' must be a positive integer")

    return len(errors) == 0, errors


def validate_rlm_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate RLM configuration."""
    errors = []

    if "enabled" in config:
        if not isinstance(config["enabled"], bool):
            errors.append("Field 'enabled' must be a boolean")

    if "cache_responses" in config:
        if not isinstance(config["cache_responses"], bool):
            errors.append("Field 'cache_responses' must be a boolean")

    if "max_context_length" in config:
        length = config["max_context_length"]
        if not isinstance(length, int) or length < 100:
            errors.append("Field 'max_context_length' must be an integer >= 100")

    if "context_top_k" in config:
        k = config["context_top_k"]
        if not isinstance(k, int) or k < 1:
            errors.append("Field 'context_top_k' must be a positive integer")

    return len(errors) == 0, errors
