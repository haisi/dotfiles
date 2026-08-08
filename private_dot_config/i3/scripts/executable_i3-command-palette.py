#!/usr/bin/env python3
"""i3 command palette: fuzzy-search i3 keybindings via rofi and run them.

Parses ~/.config/i3/config (or $I3_CONFIG), extracts bindsym/bindcode lines
(including ones nested in mode "..." { } blocks), and offers them to rofi as
a searchable list. The selected binding's command is executed via i3-msg.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

MODE_OPEN_RE = re.compile(r'^mode\s+"([^"]+)"\s*\{')
BIND_RE = re.compile(r"^(bindsym|bindcode)\s+(.*)$")
LABEL_RE = re.compile(r"^#\s*@label:\s*(.*)$")
KEYWORDS_RE = re.compile(r"^#\s*@keywords:\s*(.*)$")
BIND_SPLIT_RE = re.compile(r"^((?:--\S+\s+)*)(\S+)\s+(.*)$")
SET_RE = re.compile(r"^set\s+(\$[A-Za-z0-9_]+)\s+(.*)$")
VAR_TOKEN_RE = re.compile(r"\$[A-Za-z0-9_]+")

DEFAULT_MODE_EXIT_COMMAND = 'mode "default"'


class Entry:
    __slots__ = ("label", "key_display", "command", "exec_command", "keywords", "mode")

    def __init__(self, label, key_display, command, exec_command, keywords, mode):
        self.label = label
        self.key_display = key_display
        self.command = command
        self.exec_command = exec_command
        self.keywords = keywords
        self.mode = mode


def collect_variables(lines):
    """i3 expands `set $name value` variables while it parses the config
    file itself. A command sent over IPC via i3-msg never goes through that
    parser, so a raw command like 'move container to workspace number $ws1'
    would be sent to i3 with the literal, unexpanded token '$ws1'. Resolve
    them ourselves before dispatching."""
    variables = {}
    for raw_line in lines:
        m = SET_RE.match(raw_line.strip())
        if m:
            variables[m.group(1)] = m.group(2).strip()
    return variables


def substitute_vars(text, variables):
    return VAR_TOKEN_RE.sub(lambda m: variables.get(m.group(0), m.group(0)), text)


def die(message):
    sys.stderr.write(f"i3-command-palette: {message}\n")
    try:
        subprocess.run(
            ["notify-send", "-u", "critical", "i3 command palette", message],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass
    sys.exit(1)


def parse_config(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    variables = collect_variables(lines)

    entries = []
    mode_stack = []  # str for mode blocks, None for other blocks
    pending_label = None
    pending_keywords = None

    def current_mode():
        for m in reversed(mode_stack):
            if m is not None:
                return m
        return None

    for raw_line in lines:
        line = raw_line.strip()

        if line == "":
            pending_label = None
            pending_keywords = None
            continue

        m = LABEL_RE.match(line)
        if m:
            pending_label = m.group(1).strip()
            continue

        m = KEYWORDS_RE.match(line)
        if m:
            pending_keywords = m.group(1).strip()
            continue

        m = MODE_OPEN_RE.match(line)
        if m:
            mode_stack.append(m.group(1))
            pending_label = None
            pending_keywords = None
            continue

        if line == "}":
            if mode_stack:
                mode_stack.pop()
            pending_label = None
            pending_keywords = None
            continue

        if line.endswith("{"):
            mode_stack.append(None)
            pending_label = None
            pending_keywords = None
            continue

        m = BIND_RE.match(line)
        if not m:
            # Any other config directive (or a plain comment) discards a
            # pending annotation so it doesn't leak onto a later bindsym.
            pending_label = None
            pending_keywords = None
            continue

        label_annotation = pending_label
        keywords_annotation = pending_keywords
        pending_label = None
        pending_keywords = None

        split = BIND_SPLIT_RE.match(m.group(2))
        if not split:
            continue

        flags, key, command = split.groups()
        key_display = (flags + key).strip()
        command = command.strip()
        mode = current_mode()

        if command == DEFAULT_MODE_EXIT_COMMAND and not label_annotation:
            continue

        label = label_annotation if label_annotation else command
        if mode:
            label = f"[{mode}] {label}"

        keywords = " ".join(
            part for part in (keywords_annotation, command, key, mode) if part
        )

        exec_command = substitute_vars(command, variables)

        entries.append(Entry(label, key_display, command, exec_command, keywords, mode))

    return entries


def build_rofi_input(entries):
    width = max((len(e.label) for e in entries), default=0)
    visibles = [f"{e.label:<{width}}   {e.key_display}" for e in entries]
    lines = [f"{v}\0meta\x1f{e.keywords}" for v, e in zip(visibles, entries)]
    lookup = {v: e.exec_command for v, e in zip(visibles, entries)}
    return "\n".join(lines) + "\n", lookup


def run_rofi(rofi_input):
    try:
        result = subprocess.run(
            ["rofi", "-dmenu", "-i", "-p", "i3 action", "-no-custom"],
            input=rofi_input,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        die("rofi is not installed or not on PATH")

    selection = result.stdout.rstrip("\n")
    if result.returncode != 0 or not selection:
        sys.exit(0)
    return selection


def main():
    config_path = Path(
        os.environ.get("I3_CONFIG", "~/.config/i3/config")
    ).expanduser()

    if not config_path.is_file():
        die(f"config file not found: {config_path}")

    entries = parse_config(config_path)
    if not entries:
        die(f"no bindsym/bindcode entries found in {config_path}")

    rofi_input, lookup = build_rofi_input(entries)
    selection = run_rofi(rofi_input)

    command = lookup.get(selection)
    if command is None:
        sys.exit(0)

    subprocess.run(["i3-msg", command], check=False)


if __name__ == "__main__":
    main()
