# yggdrasil-go-gtk
Graphical interface for yggdrasil on gtk4 + libadwaita

### Initial Setup

1. **Clone the repository**: Clone this repository using `git clone`.
2. **Download Dependencies**: Download the required dependencies into the Virtual Environment `venv` using `uv`.
    ```bash
    git clone https://github.com/grisha765/yggdrasil-go-gtk.git
    cd yggdrasil-go-gtk
    python -m venv .venv
    .venv/bin/python -m pip install uv
    .venv/bin/python -m uv sync
    ```
3. **Build yggdrasil**: Download the source code, build, put the binary in the root of the project.
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
        mv ./yggdrasil $HOME/.local/bin/
        ```

### Deploy

- Run the gui:
    ```bash
    uv run yggui
    ```
