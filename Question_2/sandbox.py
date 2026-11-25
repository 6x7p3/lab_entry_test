import json
import subprocess
import sys
from functools import wraps
from pathlib import Path
from tempfile import TemporaryDirectory

from deepagents.backends.protocol import ExecuteResponse, FileDownloadResponse, FileUploadResponse
from deepagents.backends.sandbox import BaseSandbox


class AnalysisSandbox(BaseSandbox):
    enable_capture_offload = True

    def __init__(self, data_dir: Path, workspace: Path):
        bundle = Path(__file__).resolve().parent
        self.workspace = workspace.resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.scratch = TemporaryDirectory(prefix="scrna-sandbox-")
        self.mounts = [
            "/usr/bin/bwrap", "--unshare-all", "--unshare-user", "--disable-userns", "--die-with-parent",
            "--new-session", "--cap-drop", "ALL",
            "--ro-bind", "/usr/bin", "/usr/bin", "--symlink", "usr/bin", "/bin",
            "--ro-bind", "/usr/lib", "/usr/lib", "--symlink", "usr/lib", "/lib",
            "--ro-bind", "/usr/lib64", "/usr/lib64", "--symlink", "usr/lib64", "/lib64",
            "--ro-bind", "/usr/share", "/usr/share",
            "--ro-bind", "/etc/fonts", "/etc/fonts",
            "--ro-bind", f"{sys.prefix}/bin", f"{sys.prefix}/bin",
            "--ro-bind", f"{sys.prefix}/lib", f"{sys.prefix}/lib",
            "--ro-bind", f"{sys.prefix}/share", f"{sys.prefix}/share",
            "--ro-bind", str(bundle / "skills"), "/skills",
            "--ro-bind", str(bundle / "analysis_tools"), "/opt/scrna/analysis_tools",
            "--proc", "/proc", "--dev", "/dev",
            "--bind", self.scratch.name, "/tmp",
            "--bind", str(self.workspace), "/workspace", "--dir", "/data",
        ]
        for dataset in sorted(data_dir.glob("*.h5ad")):
            self.mounts.extend(["--ro-bind", str(dataset.resolve()), f"/data/{dataset.name}"])
        self.mounts.extend(["--remount-ro", "/", "--chdir", "/workspace", "--"])

    @property
    def id(self) -> str:
        return str(self.workspace)

    def _run(self, args, *, data=b"", timeout=None, stderr=subprocess.PIPE):
        return subprocess.run(
            [*self.mounts, *args], input=data, stdout=subprocess.PIPE, stderr=stderr,
            timeout=timeout, cwd="/",
            env={
                "PATH": f"{sys.prefix}/bin:/usr/bin", "HOME": "/tmp", "LANG": "C.UTF-8",
                "PYTHONPATH": "/opt/scrna", "MPLBACKEND": "Agg", "NUMBA_CACHE_DIR": "/tmp/numba",
            },
        )

    def execute(self, command: str, *, timeout: int | None = None) -> ExecuteResponse:
        try:
            result = self._run(["/bin/sh", "-c", command], timeout=timeout or None, stderr=subprocess.STDOUT)
        except subprocess.TimeoutExpired:
            return ExecuteResponse(output=f"Command exceeded {timeout} seconds.", exit_code=124)
        return ExecuteResponse(output=result.stdout.decode(errors="replace"), exit_code=result.returncode)

    def bind_tool(self, tool):
        @wraps(tool)
        def call(**arguments):
            result = self._run(["python", "-P", "-m", "analysis_tools", tool.__name__], data=json.dumps(arguments).encode())
            if result.returncode:
                raise RuntimeError(result.stderr.decode(errors="replace"))
            return json.loads(result.stdout)

        return call

    def upload_files(self, files: list[tuple[str, bytes]]) -> list[FileUploadResponse]:
        responses = []
        for path, content in files:
            write_command = 'mkdir -p -- "$(dirname -- "$1")" && cat > "$1"'
            result = self._run(["/bin/sh", "-c", write_command, "upload", path], data=content)
            error = result.stderr.decode(errors="replace") if result.returncode else None
            responses.append(FileUploadResponse(path=path, error=error))
        return responses

    def download_files(self, paths: list[str]) -> list[FileDownloadResponse]:
        responses = []
        for path in paths:
            result = self._run(["/usr/bin/cat", "--", path])
            responses.append(FileDownloadResponse(
                path=path, content=result.stdout if result.returncode == 0 else None,
                error=result.stderr.decode(errors="replace") if result.returncode else None,
            ))
        return responses

