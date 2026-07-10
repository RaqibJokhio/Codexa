from langgraph.graph import StateGraph, END
from app.schemas import CodexaState
from app.agents.planner import run_planner
from app.agents.code_generator import run_code_generator
from app.agents.reviewer import run_reviewer
from app.agents.debugger import run_debugger


async def planner_node(state: CodexaState) -> dict:
    plan = await run_planner(state["task_description"])
    return {"plan": plan}


async def code_generator_node(state: CodexaState) -> dict:
    code = await run_code_generator(state["task_description"], state["plan"])
    return {"code": code}


async def reviewer_node(state: CodexaState) -> dict:
    verdict = await run_reviewer(state["task_description"], state["code"])
    return {"approved": verdict["approved"], "issues": verdict["issues"]}


async def debugger_node(state: CodexaState) -> dict:
    fixed_code = await run_debugger(state["task_description"], state["code"], state["issues"])
    return {"code": fixed_code, "retry_count": state["retry_count"] + 1}


def should_continue(state: CodexaState) -> str:
    """
    This is the decision point after every Reviewer check:
    - If approved -> we're done (END)
    - If not approved but retries remain -> loop to Debugger
    - If not approved and retries exhausted -> stop anyway (END), to avoid an infinite loop
    """
    if state["approved"]:
        return "end"
    if state["retry_count"] >= state["max_retries"]:
        return "end"
    return "debug"


def build_graph():
    graph = StateGraph(CodexaState)

    graph.add_node("planner", planner_node)
    graph.add_node("code_generator", code_generator_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("debugger", debugger_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "code_generator")
    graph.add_edge("code_generator", "reviewer")
    graph.add_conditional_edges(
        "reviewer",
        should_continue,
        {"debug": "debugger", "end": END},
    )
    graph.add_edge("debugger", "reviewer")

    return graph.compile()