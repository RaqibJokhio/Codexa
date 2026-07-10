import { useState } from "react";
import axios from "axios";
import { ListTree, Code2, ShieldCheck, Wrench, CheckCircle2, XCircle, Loader2 } from "lucide-react";
import "./index.css";

const API_URL = "http://127.0.0.1:8000";

const STAGES = [
  { key: "planner", label: "Planner", desc: "Breaking the task into steps", icon: ListTree },
  { key: "code_generator", label: "Code Generator", desc: "Writing the implementation", icon: Code2 },
  { key: "reviewer", label: "Reviewer", desc: "Checking correctness", icon: ShieldCheck },
  { key: "debugger", label: "Debugger", desc: "Fixing flagged issues", icon: Wrench },
];

function App() {
  const [task, setTask] = useState("");
  const [loading, setLoading] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!task.trim() || loading) return;

    setLoading(true);
    setResult(null);
    setError(null);

    // Simulate the visible pipeline progression while the real request runs.
    // The backend runs all agents in one call, so this gives visual feedback
    // of roughly where the process is, without needing streaming from the API.
    setActiveStage("planner");
    const stageTimer = setInterval(() => {
      setActiveStage((prev) => {
        const idx = STAGES.findIndex((s) => s.key === prev);
        if (idx < STAGES.length - 1) return STAGES[idx + 1].key;
        return prev;
      });
    }, 4000);

    try {
      const response = await axios.post(`${API_URL}/generate`, {
        task_description: task,
        max_retries: 3,
      });
      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Could not reach Codexa's backend. Make sure the server is running."
      );
    } finally {
      clearInterval(stageTimer);
      setActiveStage(null);
      setLoading(false);
    }
  };

  const getStageStatus = (stageKey) => {
    if (loading && activeStage === stageKey) return "active";
    if (!result) return "idle";
    if (stageKey === "reviewer" && !result.approved) return "issue";
    if (stageKey === "debugger" && result.retry_count === 0) return "idle";
    return "done";
  };

  return (
    <div className="app">
      <div className="header">
        <h1>Codexa</h1>
        <p>Planner → Code Generator → Reviewer → Debugger, looping until the code is solid.</p>
      </div>

      <form className="task-form" onSubmit={handleSubmit}>
        <textarea
          placeholder="Describe the coding task, e.g. 'Write a function that checks if a string is a palindrome.'"
          value={task}
          onChange={(e) => setTask(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !task.trim()}>
          {loading ? "Running agents..." : "Generate code"}
        </button>
      </form>

      <div className="pipeline">
        {STAGES.map((stage, idx) => {
          const status = getStageStatus(stage.key);
          const Icon = stage.icon;
          return (
            <div className="stage" key={stage.key}>
              {idx < STAGES.length - 1 && <div className="stage-connector" />}
              <div className={`stage-icon ${status}`}>
                {status === "active" && <Loader2 size={18} className="spin" />}
                {status === "done" && <CheckCircle2 size={18} color="#3ECF8E" />}
                {status === "issue" && <XCircle size={18} color="#E5484D" />}
                {status === "idle" && <Icon size={18} color="#8A8D93" />}
              </div>
              <div className="stage-info">
                <h3>{stage.label}</h3>
                <p>{stage.desc}</p>
              </div>
              {stage.key === "debugger" && result && result.retry_count > 0 && (
                <span className="retry-badge">retried {result.retry_count}x</span>
              )}
            </div>
          );
        })}
      </div>

      {error && <div className="error-box">{error}</div>}

      {result && (
        <>
          <div className="status-row">
            <span className={`status-badge ${result.approved ? "approved" : "not-approved"}`}>
              {result.approved ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
              {result.approved ? "Approved" : "Not fully resolved"}
            </span>
          </div>

          <div className="panel">
            <h2>Plan</h2>
            <ul className="plan-list">
              {result.plan
                .split("\n")
                .filter((line) => line.trim())
                .map((line, i) => (
                  <li key={i}>{line.replace(/^\d+\.\s*/, "")}</li>
                ))}
            </ul>
          </div>

          <div className="panel">
            <h2>Final Code</h2>
            <pre className="code-block">
              {result.code.replace(/^```python\n?/, "").replace(/```$/, "")}
            </pre>
          </div>

          {result.issues.length > 0 && (
            <div className="panel">
              <h2>Remaining Issues</h2>
              <ul className="issues-list">
                {result.issues.map((issue, i) => (
                  <li key={i}>{issue}</li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default App;