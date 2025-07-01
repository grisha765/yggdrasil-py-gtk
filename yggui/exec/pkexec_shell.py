import subprocess
import time
from threading import Lock
from yggui.core.common import Runtime, Binary


class PkexecShell:
    _proc: subprocess.Popen[str] | None = None
    _lock: Lock = Lock()

    @classmethod
    def _spawn_shell(cls) -> subprocess.Popen[str]:
        cmd = []
        if Runtime.is_flatpak:
            cmd.extend(["flatpak-spawn", "--host"])

        cmd.extend([Binary.pkexec_path, "--disable-internal-agent", "/bin/sh"])
        return subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    @classmethod
    def _ensure_shell(cls) -> subprocess.Popen[str]:
        with cls._lock:
            if cls._proc is None or cls._proc.poll() is not None:
                cls._proc = cls._spawn_shell()
            return cls._proc

    @classmethod
    def run_capture(cls, command: str, timeout: float = 15.0) -> str:
        proc = cls._ensure_shell()

        stdin = proc.stdin
        stdout = proc.stdout
        assert stdin is not None
        assert stdout is not None

        marker = f"__YGGUI_DONE_{time.time_ns()}__"

        stdin.write(f"{command}; echo {marker}\n")
        stdin.flush()

        output_lines: list[str] = []
        start = time.time()
        for line in iter(stdout.readline, ""):
            if line.strip() == marker:
                break
            output_lines.append(line)
            if time.time() - start > timeout:
                break

        return "".join(output_lines)

    @classmethod
    def run_background(cls, command: str) -> int:
        proc = cls._ensure_shell()

        stdin = proc.stdin
        stdout = proc.stdout
        assert stdin is not None
        assert stdout is not None

        sentinel = "__YGGUI_PID__"

        stdin.write(f"{command} & echo $! {sentinel}\n")
        stdin.flush()

        for line in iter(stdout.readline, ""):
            if sentinel in line:
                return int(line.split()[0])

        raise RuntimeError("Failed to capture background PID")

    @classmethod
    def run(cls, command: str) -> None:
        proc = cls._ensure_shell()

        stdin = proc.stdin
        assert stdin is not None

        stdin.write(f"{command}\n")
        stdin.flush()

    @classmethod
    def stop(cls) -> None:
        with cls._lock:
            if cls._proc and cls._proc.poll() is None:
                try:
                    stdin = cls._proc.stdin
                    assert stdin is not None
                    stdin.write("exit\n")
                    stdin.flush()
                    cls._proc.wait(timeout=3)
                except Exception:
                    cls._proc.kill()
            cls._proc = None


if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")

