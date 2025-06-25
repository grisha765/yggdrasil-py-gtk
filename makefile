PY          ?= python3
MODULE      ?= yggui
OUTDIR      ?= build
LTO         ?= yes

NUITKA_OPTS ?= \
	--standalone \
	--onefile \
	--output-dir=$(OUTDIR) \
	--include-package=$(MODULE) \
	--include-package-data=yggui.ui \
	--enable-plugin=gi \
	--nofollow-import-to=tkinter,unittest,turtle,pdb,doctest \
	--noinclude-default-mode=error \
	--lto=$(LTO) \
	--show-progress

SRCS := $(shell find $(MODULE) -name '*.py') $(shell find . -maxdepth 1 -name '*.py')
RAW_BIN := $(OUTDIR)/$(MODULE).bin
BIN     := $(OUTDIR)/$(MODULE)

.PHONY: all deps run clean install

all: deps $(BIN)

deps:
	@{ \
		missing=0; \
		if ! command -v pkg-config >/dev/null; then \
			echo "ERROR: pkg-config not found. Install it (Debian/Ubuntu: apt install pkg-config, Fedora/RHEL: dnf install pkg-config)."; \
			missing=1; \
		fi; \
		if ! command -v $(PY) >/dev/null; then \
			echo "ERROR: $(PY) not found. Install it (Debian/Ubuntu: apt install python3, Fedora/RHEL: dnf install python3)."; \
			missing=1; \
		fi; \
		if [ "$$missing" -eq 1 ]; then \
			exit 127; \
		fi; \
	}
	@{ \
		missing=0; \
		if ! $(PY) -m nuitka --version >/dev/null 2>&1; then \
			echo "ERROR: Nuitka not installed for $(PY). Install with: $(PY) -m pip install --upgrade nuitka."; \
			missing=1; \
		fi; \
		if ! command -v patchelf >/dev/null; then \
			echo "ERROR: patchelf not found. Install it (Debian/Ubuntu: apt install patchelf, Fedora/RHEL: dnf install patchelf)."; \
			missing=1; \
		fi; \
		if ! command -v $(CC) >/dev/null; then \
			echo "ERROR: C compiler '$(CC)' not found. Install it (Debian/Ubuntu: apt install gcc, Fedora/RHEL: dnf install gcc)."; \
			missing=1; \
		fi; \
		pyver="$$( $(PY) -c 'import sys; print("python%d.%d" % (sys.version_info[0], sys.version_info[1]))' 2>/dev/null )"; \
		if [ -z "$$pyver" ]; then \
			echo "ERROR: Could not detect python version. Install it (Debian/Ubuntu: apt install python3, Fedora/RHEL: dnf install python3)."; \
			missing=1; \
		else \
			pkg_ok=no; \
			for pc in "$${pyver}-embed" "$${pyver}" python3; do \
				if pkg-config --exists "$$pc"; then pkg_ok=yes; break; fi; \
			done; \
			if [ "$$pkg_ok" = no ]; then \
				echo "ERROR: Python development headers not found. Install it (Debian/Ubuntu: apt install python3-dev, Fedora/RHEL: dnf install python3-devel)."; \
				missing=1; \
			fi; \
		fi; \
		if ! pkg-config --exists gobject-introspection-1.0; then \
			echo "ERROR: gobject-introspection not found. Install it (Debian/Ubuntu: apt install libgirepository1.0-dev, Fedora/RHEL: dnf install gobject-introspection-devel)."; \
			missing=1; \
		fi; \
		if ! $(PY) -c "import gi" >/dev/null 2>&1; then \
			echo "ERROR: gi (PyGObject) not found for $(PY). Install it (Debian/Ubuntu: apt install python3-gi, Fedora/RHEL: dnf install python3-gobject)."; \
			missing=1; \
		fi; \
		if [ "$$missing" -eq 1 ]; then \
			exit 127; \
		fi; \
	}

$(RAW_BIN): $(SRCS)
	$(PY) -m nuitka $(NUITKA_OPTS) $(MODULE)

$(BIN): $(RAW_BIN)
	@cp $< $@

install: $(BIN)
	@{ \
		if [ "$$(id -u)" -eq 0 ]; then \
			DEST=/usr/bin; \
		else \
			DEST=$$HOME/.local/bin; \
		fi; \
		echo "Installing to $$DEST/$(MODULE)"; \
		install -Dm755 $(BIN) $$DEST/$(MODULE); \
	}

run: $(BIN)
	@echo "Running $(BIN)…"; ./$(BIN)

clean:
	rm -rf $(OUTDIR) $(MODULE).build $(MODULE).dist \
	       $(MODULE).onefile-build __pycache__

