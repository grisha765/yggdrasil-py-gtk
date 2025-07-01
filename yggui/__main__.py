import os, sys, signal, atexit, functools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def write_pid_file(pid_file) -> None:
    def is_process_alive(pid: int) -> bool:
        try:
            os.kill(pid, 0)
        except OSError:
            return False
        return True

    if pid_file.exists():
        try:
            previous_pid = int(pid_file.read_text().strip())
        except ValueError:
            previous_pid = None

        if (
            previous_pid
            and previous_pid != os.getpid()
            and is_process_alive(previous_pid)
        ):
            sys.stderr.write("Another instance is already running.\n")
            sys.exit(1)

    try:
        pid_file.write_text(str(os.getpid()))
    except OSError:
        sys.stderr.write("Failed to create PID file – exiting.\n")
        sys.exit(1)


def cleanup_pid_file(pid_file, *_args) -> None:
    pid_file.unlink(missing_ok=True)


from yggui.core.common import Default

write_pid_file(Default.pid_file)
atexit.register(cleanup_pid_file, Default.pid_file)
signal.signal(signal.SIGTERM, functools.partial(cleanup_pid_file, Default.pid_file))

from yggui.core.window import MyApp

if __name__ == '__main__':
    app = MyApp(application_id="io.github.grisha765.yggdrasil-go-gtk")
    app.run(sys.argv)

