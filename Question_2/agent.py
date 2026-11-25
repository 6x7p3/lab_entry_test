from contextlib import suppress
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend
from langchain_openai import ChatOpenAI

from .analysis_tools import STAGE_TOOLS
from .sandbox import AnalysisSandbox


run_dir = Path.cwd()
sandbox = AnalysisSandbox(data_dir=run_dir, workspace=run_dir / "workspace")
with suppress(FileExistsError):
    (sandbox.workspace / "dataset_notes.md").touch(exist_ok=False)

agent = create_deep_agent(
    model=ChatOpenAI(model="gpt-6.1-terra", use_responses_api=True, reasoning={"effort": "medium"}),
    backend=CompositeBackend(default=sandbox, routes={}, artifacts_root="/workspace/.deepagents"),
    skills=["/skills/"],
    memory=["/workspace/dataset_notes.md"],
    tools=[sandbox.bind_tool(tool) for tool in STAGE_TOOLS],
    system_prompt=(Path(__file__).resolve().parent / "prompts" / "system.md").read_text(encoding="utf-8"),
)
