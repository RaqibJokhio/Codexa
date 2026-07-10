from app.llm import call_llm

DEBUGGER_SYSTEM_PROMPT = """You are a Debugger agent in a multi-agent coding assistant.
You will be given a coding task, a piece of Python code, and a list of specific issues found by a Reviewer agent.
Fix the code so that every listed issue is resolved, without breaking anything that already works.
Output ONLY the corrected code inside a single Python code block — no explanation before or after it."""


async def run_debugger(task_description: str, code: str, issues: list[str]) -> str:
    """
    Takes the original task, the current (broken) code, and the Reviewer's issue list.
    Returns fixed code as a string. This goes back to the Reviewer to check again,
    forming the Reviewer <-> Debugger loop.
    """
    issues_text = "\n".join(f"- {issue}" for issue in issues)

    user_prompt = f"""Original task: {task_description}

Current code:
{code}

Issues found by Reviewer:
{issues_text}

Fix the code now."""

    fixed_code = await call_llm(
        system_prompt=DEBUGGER_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
    )
    return fixed_code