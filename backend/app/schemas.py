from typing import TypedDict, List


class CodexaState(TypedDict):
    """
    Shared state that flows through the LangGraph graph.
    Every node (agent) reads from this and writes back to it.
    """
    task_description: str
    plan: str
    code: str
    approved: bool
    issues: List[str]
    retry_count: int
    max_retries: int