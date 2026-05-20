import httpx
import os

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "codellama"  # swap to "gemma3:4b" if codellama not ready

def build_prompt(filename: str, source_code: str, metrics: dict) -> str:
    return f"""You are a Senior Software Architect reviewing Python code for refactoring.

FILE: {filename}
METRICS:
- Lines of Code: {metrics.get('loc')}
- Cyclomatic Complexity: {metrics.get('cyclomatic_complexity')}
- Halstead Effort: {metrics.get('halstead_effort')}
- Maintainability Index: {metrics.get('maintainability_index')}
- Risk Score: {metrics.get('risk_score')} / 100
- Risk Tier: {metrics.get('risk_tier')}

SOURCE CODE:
```python
{source_code[:3000]}
```

Provide a refactoring plan with these exact sections:
1. ISSUES: List the top 3 problems in this code
2. REFACTORED CODE: The improved version of the code
3. CHANGES: Numbered list of what you changed and why
4. ESTIMATED IMPROVEMENT: Expected reduction in complexity

Keep your response concise and practical."""


def get_source_code(filepath: str) -> str | None:
    """Read source code from the stored filepath."""
    try:
        if not filepath or not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


async def call_ollama(prompt: str) -> str:
    """Call Ollama REST API and return the response text."""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(OLLAMA_URL, json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            })
            response.raise_for_status()
            return response.json().get("response", "").strip()
    except httpx.ConnectError:
        raise RuntimeError("Ollama is not running. Start it with: ollama serve")
    except httpx.TimeoutException:
        raise RuntimeError("Ollama timed out. Try a smaller file or lighter model.")
    except Exception as e:
        raise RuntimeError(f"Ollama error: {str(e)}")