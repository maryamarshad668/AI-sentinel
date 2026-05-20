import requests
import os

CODELLAMA_API_URL = os.getenv("CODELLAMA_API_URL", "http://127.0.0.1:11434/v1/chat/completions")
CODELLAMA_MODEL_NAME = os.getenv("CODELLAMA_MODEL_NAME", "tinyllama")
CODELLAMA_FALLBACK_MODELS = [m.strip() for m in os.getenv("CODELLAMA_FALLBACK_MODELS", "").split(",") if m.strip()]
CODELLAMA_MAX_TOKENS = int(os.getenv("CODELLAMA_MAX_TOKENS", "256"))
CODELLAMA_TEMPERATURE = float(os.getenv("CODELLAMA_TEMPERATURE", "0.2"))
CODELLAMA_TIMEOUT = int(os.getenv("CODELLAMA_TIMEOUT", "300"))


def build_prompt(filename: str, source_code: str, metrics: dict) -> str:
    return f"""You are a Senior Software Architect. Refactor this Python code.

FILE: {filename}
Risk Score: {metrics.get('risk_score', 'N/A')}/100
Cyclomatic Complexity: {metrics.get('cyclomatic_complexity', 'N/A')}

CODE:
```python
{source_code[:1200]}
```

Reply with:
1. ISSUES: top 2 problems
2. REFACTORED CODE: improved version
3. CHANGES: what you fixed"""


def get_source_code(filepath: str):
    try:
        if not filepath or not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def build_fallback_refactor_plan(filename: str, source_code: str, metrics: dict, reason: str | None = None) -> str:
    issues = []
    if metrics.get("loc", 0) >= 200:
        issues.append("This file has a large number of lines and likely contains too much behavior in one place.")
    if metrics.get("cyclomatic_complexity", 0) >= 15:
        issues.append("Cyclomatic complexity is high, making the code hard to maintain and test.")
    if metrics.get("maintainability_index") is not None and metrics["maintainability_index"] < 65:
        issues.append("Maintainability index is low, indicating the code is fragile and difficult to understand.")
    if not issues:
        issues.append("The file appears to be okay, but it may still benefit from smaller functions and clearer naming.")

    core_function = None
    for line in source_code.splitlines():
        if line.strip().startswith("def "):
            core_function = line.strip()
            break

    refactored_code = "# Keep functions small and single-purpose. Extract helpers for repeated logic.\n"
    if core_function:
        refactored_code += f"# Example: simplify {core_function.split('(')[0]} by extracting helper functions.\n"
    refactored_code += "# The specific refactor depends on the code paths and business logic in this file."

    changes = [
        "Extract repeated or nested logic into smaller helper functions.",
        "Reduce cyclomatic complexity by flattening conditionals and loops.",
        "Rename variables and functions to improve intent and readability.",
        "Add comments or docstrings for complex sections and remove duplicated code.",
    ]

    payload = [f"- {issue}" for issue in issues]
    changes_text = "\n".join(f"{i+1}. {c}" for i, c in enumerate(changes))
    note = f"\n\nNOTE: Launched fallback refactor plan because CodeLlama was unavailable: {reason}" if reason else ""

    return (
        "ISSUES:\n" + "\n".join(payload) + "\n\n"
        "REFACTORED CODE:\n" + refactored_code + "\n\n"
        "CHANGES:\n" + changes_text + note
    )


def _extract_response_text(data: object) -> str:
    if not isinstance(data, dict):
        return str(data).strip()

    if "response" in data:
        return str(data["response"]).strip()

    if "output" in data:
        output = data["output"]
        if isinstance(output, list):
            output = "".join(str(chunk) for chunk in output)
        return str(output).strip()

    if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
        first = data["choices"][0]
        if isinstance(first, dict):
            if "text" in first:
                return str(first["text"]).strip()
            if "message" in first and isinstance(first["message"], dict):
                return str(first["message"].get("content", "")).strip()
            if "output" in first:
                return str(first["output"]).strip()

    if "results" in data and isinstance(data["results"], list) and data["results"]:
        result = data["results"][0]
        if isinstance(result, dict) and "output" in result:
            return str(result["output"]).strip()

    return str(data).strip()


def _build_codelama_payload(prompt: str, model: str) -> dict:
    api_path = CODELLAMA_API_URL.rstrip("/").lower()
    if api_path.endswith("/chat/completions"):
        return {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": CODELLAMA_MAX_TOKENS,
            "temperature": CODELLAMA_TEMPERATURE,
        }

    return {
        "model": model,
        "prompt": prompt,
        "max_tokens": CODELLAMA_MAX_TOKENS,
        "temperature": CODELLAMA_TEMPERATURE,
    }


def call_codelama(prompt: str) -> str:
    """Call CodeLlama synchronously with a configurable timeout."""
    models_to_try = [CODELLAMA_MODEL_NAME] + [m for m in CODELLAMA_FALLBACK_MODELS if m and m != CODELLAMA_MODEL_NAME]
    last_error = None

    for model in models_to_try:
        payload = _build_codelama_payload(prompt, model)
        try:
            r = requests.post(CODELLAMA_API_URL, json=payload, timeout=(5, CODELLAMA_TIMEOUT))
            r.raise_for_status()
            return _extract_response_text(r.json())
        except requests.exceptions.ReadTimeout as e:
            last_error = f"Model={model} timed out: {e}"
            continue
        except requests.exceptions.ConnectTimeout as e:
            last_error = f"Model={model} connect timeout: {e}"
            continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Model={model} connection error: {e}"
            continue
        except ValueError as e:
            last_error = f"Model={model} returned invalid JSON: {e}"
            continue
        except Exception as e:
            last_error = f"Model={model} error: {e}"
            continue

    raise RuntimeError(
        "CodeLlama API failed for all models. "
        + (last_error or "No response received.")
    )