PY          ?= python3
MODULE      ?= yggui
OUTDIR      ?= build
LTO         ?= yes

NUITKA_OPTS ?= \
	--standalone \
	--onefile \
	--output-dir=$(OUTDIR) \
	--include-package=$(MODULE) \
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
	@command -v $(PY) >/dev/null || { \
		echo "ERROR: '$(PY)' not found in $(PATH)."; exit 127; }
	@$(PY) -m nuitka --version >/dev/null 2>&1 || { \
		echo "ERROR: Nuitka is not installed for '$(PY)'. Run: $(PY) -m pip install --upgrade nuitka"; \
		exit 127; }
	@command -v patchelf >/dev/null || { \
		echo "ERROR: 'patchelf' is required for Nuitka --standalone on Linux." \
		     "Install it via your package manager (e.g. apt install patchelf)."; \
		exit 127; }
	@command -v $(CC) >/dev/null || { \
		echo "ERROR: no suitable C compiler found (tried '$(CC)')." \
		     "Install GCC or Clang, or call make with CC=<compiler>."; \
		exit 127; }
	@command -v pkg-config >/dev/null || { \
		echo "ERROR: 'pkg-config' is required to detect Python headers."; exit 127; }
	@{ \
		pyver="$$( $(PY) -c 'import sys; print("python%d.%d" % (sys.version_info[0], sys.version_info[1]))' )"; \
		pkg_ok=no; \
		for pc in "$${pyver}-embed" "$${pyver}" python3; do \
			if pkg-config --exists "$$pc"; then pkg_ok=yes; break; fi; \
		done; \
		if [ "$$pkg_ok" = no ]; then \
			echo "ERROR: Python development headers (Python.h) not found."; \
			echo "       Install package python3-dev (Debian/Ubuntu) or python3-devel (Fedora/RHEL)."; \
			exit 127; \
		fi; \
	}
	@pkg-config --exists gobject-introspection-1.0 || { \
		echo "ERROR: gobject-introspection is missing. Install it via your package manager."; \
		exit 127; }
	@$(PY) -c "import gi" >/dev/null 2>&1 || { \
		echo "ERROR: Python module 'gi' (PyGObject) not found for '$(PY)'."; \
		echo "       Install package python3-gi (Debian/Ubuntu) or python3-gobject (Fedora/RHEL) and rebuild."; \
		exit 127; }

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

