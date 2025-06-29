# yggdrasil-go-gtk
Graphical interface for yggdrasil on gtk4 + libadwaita

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

- Start or stop your local Yggdrasil node with a single switch.
- Live display of the node’s IPv6 address and subnet once connected.
- Add or remove peers on the fly; changes are immediately saved to `config.json`.
- Auto‑generates a minimal config on first launch and keeps `AdminListen` in sync.
- Modern GTK 4 + libadwaita interface that integrates with GNOME.
