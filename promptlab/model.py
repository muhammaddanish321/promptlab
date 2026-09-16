"""Model subprocess invocation."""

import subprocess
import json
import sys


def invoke_model(prompt_file: str, input_text: str, temperature: float = 0.0,
                seed: int = None, max_tokens: int = 256) -> dict:
    """
    Invoke model as subprocess.

    Args:
        prompt_file: Path to prompt file
        input_text: Input text for model
        temperature: Temperature (0.0 = deterministic)
        seed: Random seed (optional)
        max_tokens: Max output tokens

    Returns:
        Response dict with output, tokens_in, tokens_out, finish, latency_ms

    Raises:
        RuntimeError: If model subprocess fails
    """
    try:
        cmd = [
            sys.executable, "stubmodel.py",
            "--prompt", prompt_file,
            "--input", input_text,
            "--temperature", str(temperature),
            "--max-tokens", str(max_tokens)
        ]

        if seed is not None:
            cmd.extend(["--seed", str(seed)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode not in (0, 2, 3):
            raise RuntimeError(f"Model subprocess returned exit code {result.returncode}")

        if result.returncode != 0:
            raise RuntimeError(f"Model error (exit {result.returncode})")

        # Parse response
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError("Model response is not valid JSON")

        return response

    except subprocess.TimeoutExpired:
        raise RuntimeError("Model subprocess timeout (>30s)")
    except FileNotFoundError:
        raise RuntimeError("stubmodel.py not found or not executable")
    except Exception as e:
        raise RuntimeError(f"Model invocation error: {str(e)}")
