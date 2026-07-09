from app.llm import call_llm

PLANNER_SYSTEM_PROMPT = """You are a Planner agent in a multi-agent coding assistant.
Your job is to break down a coding task into a clear, numbered list of concrete implementation steps.
Do not write any code yourself — only plan.
Keep steps specific and actionable (e.g. "Read the CSV file using pandas", not "Handle the file").
Output ONLY the numbered list of steps, nothing else — no preamble, no explanation."""


async def run_planner(task_description: str) -> str:
    """
    Takes the user's raw coding request and returns a numbered step-by-step plan.
    This plan is passed to the Code Generator agent next.
    """
    plan = await call_llm(
        system_prompt=PLANNER_SYSTEM_PROMPT,
        user_prompt=task_description,
        temperature=0.3,
    )
    return plan