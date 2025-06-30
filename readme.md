# yggdrasil-go-gtk
A modern GTK 4 + libadwaita desktop interface for running, configuring and monitoring a local Yggdrasil overlay‑network node (and optional Yggstack SOCKS proxy) on Linux. Yggdrasil‑go‑gtk wraps the official yggdrasil and yggdrasilctl binaries with an ergonomic UI that follows GNOME design guidelines. It can operate both on bare‑metal and inside a Flatpak sandbox, automatically copying host binaries into a private runtime directory when needed.

### Finished flatpak assemblies

- Download the stable releases from flatpak:
    ```bash
    flatpak remote-add --user yggdrasil-go-gtk https://grisha765.github.io/yggdrasil-go-gtk/grisha765.flatpakrepo
    ```
    ```bash
    flatpak install --user yggdrasil-go-gtk io.github.grisha765.yggdrasil-go-gtk
    ```

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Create Virtual Env**: Create a Python Virtual Environment `venv` to download the required dependencies and libraries.
3. **Download Dependencies**: Download the required dependencies into the Virtual Environment `venv` using `uv`.
    ```bash
    git clone https://github.com/grisha765/yggdrasil-go-gtk.git
    cd yggdrasil-go-gtk
    python -m venv .venv
    .venv/bin/python -m pip install uv
    .venv/bin/python -m uv sync
    ```

4. **Download Dependencies in distro**:
    ```bash
    sudo dnf install -y gtk4 libadwaita python3-gobject
    ```

5. **Build yggdrasil**: Download the source code, build, put the binary in the root of the project.
    - Clone repo:
        ```bash
        git clone https://github.com/yggdrasil-network/yggdrasil-go.git
        ```
    - Build project:
        ```bash
        cd yggdrasil-go \
        && ./build
        ```
    - Put the binary:
        ```bash
        mv ./yggdrasil $HOME/.local/bin/ && \
        mv ./yggdrasilctl $HOME/.local/bin/
        ```

6. **Run the GUI**:
    ```bash
    .venv/bin/python -m yggui
    ```

### Install with Python library

1. **Install with pip**:
    ```bash
    pip install git+https://github.com/grisha765/yggdrasil-go-gtk.git@main#egg=yggdrasil-go-gtk
    ```

2. **Run the GUI**:
    ```bash
    python3 -m yggui
    ```

## Features

- **One‑click start/stop** – toggles the daemon with polkit (pkexec) or by launching Yggstack when the SOCKS proxy is enabled.
- **Live status panel** – polls the admin socket and shows the current IPv6 address and /64 subnet.
- **Peer management** – add/remove peers with validation for TCP/TLS/QUIC, optional SNI, and instant persistence to config.json.
- **SOCKS5 proxy & DNS forwarder** – expose Yggdrasil traffic through Yggstack with user‑defined listen address and nameserver.
- **Private‑key tooling** – view, edit or regenerate the node’s PrivateKey in‑place.
- **Clipboard helpers** – copy address/subnet rows with a single click.
- **Flatpak aware** – transparently moves required binaries into the sandbox and invokes host shell commands via flatpak‑spawn.
- **Failsafe exit** – gracefully stops child processes on SIGINT or application shutdown.
