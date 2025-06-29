# yggdrasil-go-gtk
Graphical interface for yggdrasil on gtk4 + libadwaita

### Binary releases

- Download the latest self‑contained executable from the [GitHub releases page](https://github.com/grisha765/yggdrasil-go-gtk/releases).
- Download the stable releases from flatpak:
    ```bash
    flatpak remote-add --user yggdrasil-go-gtk https://grisha765.github.io/yggdrasil-go-gtk/grisha765.flatpakrepo
    ```
    ```bash
    flatpak install --user yggdrasil-go-gtk io.github.grisha765.yggdrasil-go-gtk
    ```

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
        mv ./yggdrasil $HOME/.local/bin/ && \
        mv ./yggdrasilctl $HOME/.local/bin/
        ```
4. **Run the GUI**
    ```bash
    uv run yggui
    ```

### Build with Makefile

The project ships with a `Makefile` that produces an optimized, single‑file binary using [Nuitka](https://nuitka.net). The example below shows the required steps on **Fedora**; adapt the commands for other distributions as needed.

1. **Install system dependencies**
   ```bash
   sudo dnf install \
       python3 python3-devel \
       gcc pkg-config patchelf \
       gobject-introspection-devel \
       python3-gobject
   ```
   - Nuitka is still evolving; the newest version is usually available via *pip*:
       ```bash
       python3 -m pip install --user --upgrade nuitka
       ```

2. **Build the binary**
   ```bash
   make
   ```
   - The resulting executable will be placed in `build/yggui`.

3. **(Optional) Install system‑wide**
   ```bash
   make install
   ```

4. **Run the GUI**
   ```bash
   ./build/yggui
   ```

## Features

- Start or stop your local Yggdrasil node with a single switch.
- Live display of the node’s IPv6 address and subnet once connected.
- Edit or reset the `PrivateKey` used by Yggdrasil without leaving the app.
- Add or remove peers on the fly; changes are immediately saved to `config.json`.
- Auto‑generates a minimal config on first launch and keeps `AdminListen` in sync.
- Self‑contained binary produced via Nuitka for easy distribution.
- Modern GTK 4 + libadwaita interface that integrates with GNOME.
