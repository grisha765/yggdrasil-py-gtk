import subprocess, re
from threading import Thread
from pathlib import Path

def print_output(process):
    for line in process.stdout:
        print(line.decode('utf-8').strip())

def start_yggdrasil(ygg_path):
    command = ["pkexec", ygg_path, "-useconffile", Path("yggdrasil.conf").resolve()]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output_thread = Thread(target=print_output, args=(process,))
    output_thread.daemon = True
    output_thread.start()
    return process

def stop_yggdrasil(process):
    subprocess.run(["pkexec", "kill", "-s", "SIGINT", str(process.pid)])
    process.wait()

def extract_ips(output):
    ipv6_regex = r"([0-9a-fA-F:]+(?::[0-9a-fA-F]+)*\b)"
    return re.findall(ipv6_regex, output)

def switch_switched(self, switch, state):
    print(f'ygg_path: {self.ygg_path}')
    if state and self.process is None:
        self.process = start_yggdrasil(self.ygg_path)
        print("Yggdrasil started. Waiting for output...\n")
        self.label.set_label('Disable Yggdrasil')

    elif not state and self.process is not None:
        stop_yggdrasil(self.process)
        print("Yggdrasil stopped.\n")
        self.label.set_label('Enable Yggdrasil')
        self.process = None

    print(f'The switch has been switched {'on' if state else 'off'}')

if __name__ == "__main__":
    raise RuntimeError("This module should be run only via main.py")
