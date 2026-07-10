from app.llm import call_llm

CODE_GENERATOR_SYSTEM_PROMPT = """You are a Code Generator agent in a multi-agent coding assistant.
You will be given a numbered implementation plan. Write clean, working Python code that follows the plan exactly.
Include necessary imports. Add brief inline comments only where logic isn't obvious.
Write exactly ONE function that solves the task — do not add alternative implementations, extra helper functions, a main() demo, or test/example code.
Output ONLY the code inside a single Python code block — no explanation before or after it."""


async def run_code_generator(task_description: str, plan: str) -> str:
    """
    Takes the original task + the Planner's step-by-step plan, and generates code.
    Returns raw code as a string (including the markdown code fence, which we'll
    strip out later when we wire the agents together).
    """
    user_prompt = f"""Original task: {task_description}

Implementation plan:
{plan}

Write the code now."""

    code = await call_llm(
        system_prompt=CODE_GENERATOR_SYSTEM_PROMPT,
        user_prompt=user_prompt,
        temperature=0.2,
    )
    return code