from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.graph import build_graph

app = FastAPI(title="Codexa API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before real deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class TaskRequest(BaseModel):
    task_description: str
    max_retries: int = 3


class TaskResponse(BaseModel):
    code: str
    plan: str
    approved: bool
    issues: list[str]
    retry_count: int


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/generate", response_model=TaskResponse)
async def generate_code(request: TaskRequest):
    initial_state = {
        "task_description": request.task_description,
        "plan": "",
        "code": "",
        "approved": False,
        "issues": [],
        "retry_count": 0,
        "max_retries": request.max_retries,
    }

    final_state = await graph.ainvoke(initial_state)

    return TaskResponse(
        code=final_state["code"],
        plan=final_state["plan"],
        approved=final_state["approved"],
        issues=final_state["issues"],
        retry_count=final_state["retry_count"],
    )