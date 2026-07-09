import json
from app.llm import call_llm

REVIEWER_SYSTEM_PROMPT = """You are a Reviewer agent in a multi-agent coding assistant.
You will be given a coding task and a piece of generated Python code.
Check the code for correctness, bugs, edge cases, and whether it actually fulfills the task.

Respond with ONLY a valid JSON object in this exact format, nothing else:
{
  "approved": true or false,
  "issues": ["issue 1", "issue 2"]
}

If the code is correct and complete, set "approved" to true and "issues" to an empty list.
If there are problems, set "approved" to false and list each specific issue clearly."""


async def run_reviewer(task_description: str, code: str) -> dict:
    """
    Takes the original task + generated code, and returns a structured verdict:
    { "approved": bool, "issues": [str, ...] }
    This verdict drives the Reviewer <-> Debugger loop in the LangGraph state graph.
    """
    user_prompt = f"""Original task: {task_description}

Generated code:
{code}

Review this code now."""

    response = await call_llm(
        system_prompt=REVIEWER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.1,
    )

    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        verdict = json.loads(cleaned)
    except json.JSONDecodeError:
        verdict = {"approved": False, "issues": [f"Reviewer returned invalid JSON: {response}"]}

    return verdict