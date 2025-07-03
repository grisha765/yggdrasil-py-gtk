# Developer deployment

These steps clone **yggdrasil-py-gtk**, compile the required binaries and run the UI locally. Tested on Fedora 42; adjust package names for your distro.

## 1. Clone the repository

```bash
git clone https://github.com/grisha765/yggdrasil-py-gtk.git
cd yggdrasil-py-gtk
````

## 2. Install system packages

- Fedora / RHEL
    ```bash
    sudo dnf install gtk4 libadwaita python3-gobject
    ```

- Arch
    ```bash
    sudo pacman -S gtk4 libadwaita python-gobject
    ```

- Debian
    ```bash
    sudo apt install libgtk-4-dev gir1.2-gtk-4.0 gir1.2-adwaita-1 python3-gi
    ```

## 3. Create a Python environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip uv
uv sync
```

## 4. Build Yggdrasil & Yggstack

- Yggdrasil
    ```bash
    git clone https://github.com/yggdrasil-network/yggdrasil-go.git
    cd yggdrasil-go
    ./build          # produces yggdrasil and yggdrasilctl
    mv yggdrasil yggdrasilctl ~/.local/bin/
    cd ..
    ```

- Yggstack (optional SOCKS proxy)
    ```bash
    git clone https://github.com/yggdrasil-network/yggstack.git
    cd yggstack
    ./build
    mv yggstack ~/.local/bin/
    cd ..
    ```

Ensure `~/.local/bin` is on your `$PATH` so the UI can locate the executables.

## 5. Run the UI

```bash
source .venv/bin/activate
python -m yggui
```

Press **Switch Toggle** to launch Yggdrasil, switch to **Settings** to tweak peers or enable the SOCKS proxy.

### Troubleshooting

| Symptom                   | Fix                                                           |
| ------------------------- | ------------------------------------------------------------- |
| **Yggdrasil not found**   | Make sure `yggdrasil` and `yggdrasilctl` are on your `$PATH`. |
| **Polkit not found**      | Install `polkit` (`pkexec`).                                  |
| Need verbose logs         | Run with `G_MESSAGES_DEBUG=all`.                              |
