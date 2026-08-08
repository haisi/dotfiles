#!/usr/bin/env python3
"""Fuzzy-searchable command palette for herdr, backed by fzf.

Resolves the effective [keys.*] binding set (herdr's built-in defaults,
overlaid with the user's ~/.config/herdr/config.toml overrides and
[[keys.command]] entries), offers it to fzf, and executes the selection
either via a direct `herdr` CLI call, a small positional lookup (for
next/previous/switch tab or workspace), or (for [[keys.command]] entries)
by re-running the entry's own command.

`herdr pane send-keys` is deliberately NOT used to simulate built-in
actions: it writes literal bytes into a specific pane's PTY (input for
whatever program is running there), not herdr's own global keybinding
dispatch. Prefix-mode/global actions (help, settings, sidebar, copy mode,
detach, goto, ...) are handled entirely client-side, before any bytes
reach a pane, so there is no socket-API path to trigger them from
outside. Verified empirically: sending "ctrl+b b" to a pane running `cat`
just echoed "^Bb" back, it never toggled the sidebar. Actions with no
real server-side equivalent (REFERENCE_ONLY_ACTIONS) stay in the palette
as a searchable keybinding reference — dimmed, and selecting one just
prints the key to press yourself — rather than pretending to invoke them
(or worse, silently typing into whatever pane happens to be focused).

Supports the same "# @label: ..." / "# @keywords: ..." annotation comments
(placed directly above a [keys] line or a [[keys.command]] block) as the
i3 command palette.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

HERDR_BIN = os.environ.get("HERDR_BIN_PATH") or "herdr"
CONFIG_PATH = Path(os.environ.get("HERDR_CONFIG_PATH", "~/.config/herdr/config.toml")).expanduser()

LABEL_RE = re.compile(r"^#\s*@label:\s*(.*)$")
KEYWORDS_RE = re.compile(r"^#\s*@keywords:\s*(.*)$")
DEFAULT_ACTION_RE = re.compile(r'^#\s*([a-z_]+)\s*=\s*"([^"]*)"\s*(#.*)?$')
REAL_SECTION_RE = re.compile(r"^\[([\w.]+)\]$")
REAL_ARRAY_SECTION_RE = re.compile(r"^\[\[([\w.]+)\]\]$")
COMMENTED_SECTION_RE = re.compile(r"^#\s*\[\[?([\w.]+)\]?\]$")
SCALAR_ASSIGN_RE = re.compile(r"^([a-z_]+)\s*=")
RANGE_RE = re.compile(r"^(.*?)(\d+)\.\.(\d+)$")

# Actions that aren't invokable "actions" at all (prefix itself), or whose
# binding only means something while a *different* input mode already has
# focus (navigate-mode's plain h/j/k/l, the --remote-only paste key). These
# aren't real standalone keybindings, so listing them (with a binding that
# only works in the wrong context) would be actively misleading. True
# palette exclusions, not just "can't invoke".
EXCLUDED_ACTIONS = {
    "prefix",
    "navigate_workspace_up",
    "navigate_workspace_down",
    "navigate_pane_left",
    "navigate_pane_down",
    "navigate_pane_up",
    "navigate_pane_right",
    "remote_image_paste",
}

# Actions that ARE real, globally-triggerable keybindings, but are pure
# client-side UI state (popups, input modes, sidebar, client<->server
# connection) with no server-side representation reachable from outside
# the herdr client. Confirmed via a live test: sending "ctrl+b b" (the
# toggle_sidebar sequence) to a pane running `cat` just echoed "^Bb" back
# into that pane — it never reached herdr's own keybinding dispatch, which
# lives entirely client-side. These stay IN the palette (so it still works
# as a searchable keybinding reference, same as before the send-keys
# fallback existed) but selecting one just reports the key to press
# yourself, instead of pretending to run it.
REFERENCE_ONLY_ACTIONS = {
    "help",
    "settings",
    "detach",
    "goto",
    "workspace_picker",
    "edit_scrollback",
    "toggle_sidebar",
    "copy_mode",
    "resize_mode",
    "cycle_pane_next",
    "cycle_pane_previous",
    "last_pane",
    "open_notification_target",
    "open_worktree",
    "remove_worktree",
    "focus_agent",
    "previous_agent",
    "next_agent",
}

RENAME_ACTIONS = {
    "rename_tab": ("tab", "HERDR_ACTIVE_TAB_ID"),
    "rename_workspace": ("workspace", "HERDR_ACTIVE_WORKSPACE_ID"),
    "rename_pane": ("pane", "HERDR_ACTIVE_PANE_ID"),
}


def die(msg):
    sys.stderr.write(f"\x1b[31mherdr-command-palette: {msg}\x1b[0m\n")
    try:
        input("Press Enter to close...")
    except EOFError:
        pass
    sys.exit(1)


def prettify(name, suffix=None):
    label = name.replace("_", " ").capitalize()
    return f"{label} {suffix}" if suffix is not None else label


def expand_binding(binding):
    m = RANGE_RE.match(binding)
    if not m:
        return [(None, binding)]
    template, start, end = m.group(1), int(m.group(2)), int(m.group(3))
    return [(n, f"{template}{n}") for n in range(start, end + 1)]


def parse_default_bindings(text):
    """herdr --default-config prints every [keys.*] default as a commented
    `# name = "value"` line. Everything else in the file (prose comments,
    the [[keys.command]] example, the legacy [keys.indexed] example) is
    also commented, so we track real vs. commented section headers to know
    when we've left [keys] proper."""
    bindings = {}
    section = None
    skip_subblock = False
    for raw in text.splitlines():
        line = raw.strip()
        m = REAL_SECTION_RE.match(line) or REAL_ARRAY_SECTION_RE.match(line)
        if m:
            section = m.group(1)
            skip_subblock = False
            continue
        if COMMENTED_SECTION_RE.match(line):
            skip_subblock = True
            continue
        if section != "keys" or skip_subblock:
            continue
        m = DEFAULT_ACTION_RE.match(line)
        if m:
            bindings[m.group(1)] = m.group(2)
    return bindings


def scan_annotations(text):
    """Text-level scan for @label/@keywords comments, since tomllib
    discards comments. Tracks real section headers so a stray annotated
    line outside [keys] doesn't leak in."""
    key_annotations = {}
    command_annotations = []
    section = None
    pending_label = None
    pending_keywords = None

    def clear():
        nonlocal pending_label, pending_keywords
        pending_label = None
        pending_keywords = None

    for raw in text.splitlines():
        line = raw.strip()
        if line == "":
            clear()
            continue
        m = LABEL_RE.match(line)
        if m:
            pending_label = m.group(1).strip()
            continue
        m = KEYWORDS_RE.match(line)
        if m:
            pending_keywords = m.group(1).strip()
            continue
        m = REAL_SECTION_RE.match(line)
        if m:
            section = m.group(1)
            clear()
            continue
        m = REAL_ARRAY_SECTION_RE.match(line)
        if m and m.group(1) == "keys.command":
            command_annotations.append({"label": pending_label, "keywords": pending_keywords})
            clear()
            continue
        if line.startswith("#"):
            clear()
            continue
        m = SCALAR_ASSIGN_RE.match(line)
        if m and section == "keys" and (pending_label or pending_keywords):
            key_annotations[m.group(1)] = {"label": pending_label, "keywords": pending_keywords}
        clear()
    return key_annotations, command_annotations


def load_user_config():
    if not CONFIG_PATH.is_file():
        return {}, "", {}, []
    text = CONFIG_PATH.read_text(encoding="utf-8")
    with open(CONFIG_PATH, "rb") as f:
        data = tomllib.load(f)
    keys_table = data.get("keys", {})
    scalar_overrides = {
        k: v for k, v in keys_table.items() if isinstance(v, str) and k != "indexed"
    }
    custom_commands = keys_table.get("command", [])
    key_annotations, command_annotations = scan_annotations(text)
    if len(command_annotations) != len(custom_commands):
        # Text scan and tomllib disagree on [[keys.command]] count; don't
        # guess at alignment, just drop annotations rather than mismatch them.
        command_annotations = [{} for _ in custom_commands]
    return scalar_overrides, key_annotations, custom_commands, command_annotations


def build_entries():
    try:
        default_text = subprocess.run(
            [HERDR_BIN, "--default-config"], capture_output=True, text=True, check=True
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        die(f"could not run `{HERDR_BIN} --default-config`: {e}")

    default_bindings = parse_default_bindings(default_text)
    scalar_overrides, key_annotations, custom_commands, command_annotations = load_user_config()

    effective = dict(default_bindings)
    effective.update(scalar_overrides)

    entries = []
    for name, raw_binding in effective.items():
        if name in EXCLUDED_ACTIONS or not raw_binding:
            continue
        ann = key_annotations.get(name, {})
        for suffix, binding in expand_binding(raw_binding):
            if not binding:
                continue
            label = ann.get("label") or prettify(name, suffix)
            kw = [name, binding]
            if ann.get("keywords"):
                kw.append(ann["keywords"])
            if name in RENAME_ACTIONS and suffix is None:
                kind = "rename"
            elif name in REFERENCE_ONLY_ACTIONS:
                kind = "reference"
            else:
                kind = "builtin"
            entries.append(
                {
                    "label": label,
                    "key_display": binding,
                    "keywords": " ".join(kw),
                    "kind": kind,
                    "action": name,
                    "binding": binding,
                    "index": suffix,
                }
            )

    for ann, cmd in zip(command_annotations, custom_commands):
        description = cmd.get("description", "")
        command_str = cmd.get("command", "")
        key_display = cmd.get("key", "")
        label = ann.get("label") or description or command_str or "(custom command)"
        kw = [p for p in (command_str, key_display, ann.get("keywords"), description) if p]
        entries.append(
            {
                "label": label,
                "key_display": key_display,
                "keywords": " ".join(kw),
                "kind": "custom",
                "cmd": cmd,
            }
        )

    entries.sort(key=lambda e: e["label"].lower())
    return entries


def build_fzf_input(entries):
    label_width = max((len(e["label"]) for e in entries), default=0)
    key_width = max((len(e["key_display"]) for e in entries), default=0)
    lines = []
    for i, e in enumerate(entries):
        row = f"{e['label']:<{label_width}}  {e['key_display']:>{key_width}}"
        if e["kind"] == "reference":
            # Can't be invoked from outside the client (see
            # REFERENCE_ONLY_ACTIONS) — dim the whole row so it visually
            # reads as "reference, not runnable", not just another action.
            row = f"\x1b[2m{row}  (view only)\x1b[0m"
        display = row
        if e["keywords"]:
            # fzf has no native "hidden but searchable" field (--with-nth
            # restricts matching to exactly what it displays, per `man
            # fzf`), so keywords are shown, just dimmed rather than hidden.
            display += f"  \x1b[2;3;90m{e['keywords']}\x1b[0m"
        lines.append(f"{display}\x1f{i}")
    return "\n".join(lines) + "\n"


def run_fzf(fzf_input):
    if shutil.which("fzf") is None:
        die("fzf is not installed or not on PATH.")
    try:
        result = subprocess.run(
            [
                "fzf",
                "--ansi",
                "--delimiter",
                "\x1f",
                "--with-nth=1",
                "--prompt",
                "herdr> ",
                "--height=100%",
                "--layout=reverse",
            ],
            input=fzf_input,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        die("fzf is not installed or not on PATH.")
    selection = result.stdout.rstrip("\n")
    if result.returncode != 0 or not selection:
        sys.exit(0)
    return selection


CLI_MAPPING = {
    "focus_pane_left": lambda p, t, w: [HERDR_BIN, "pane", "focus", "--direction", "left", "--pane", p],
    "focus_pane_right": lambda p, t, w: [HERDR_BIN, "pane", "focus", "--direction", "right", "--pane", p],
    "focus_pane_up": lambda p, t, w: [HERDR_BIN, "pane", "focus", "--direction", "up", "--pane", p],
    "focus_pane_down": lambda p, t, w: [HERDR_BIN, "pane", "focus", "--direction", "down", "--pane", p],
    "swap_pane_left": lambda p, t, w: [HERDR_BIN, "pane", "swap", "--direction", "left", "--pane", p],
    "swap_pane_right": lambda p, t, w: [HERDR_BIN, "pane", "swap", "--direction", "right", "--pane", p],
    "swap_pane_up": lambda p, t, w: [HERDR_BIN, "pane", "swap", "--direction", "up", "--pane", p],
    "swap_pane_down": lambda p, t, w: [HERDR_BIN, "pane", "swap", "--direction", "down", "--pane", p],
    "split_vertical": lambda p, t, w: [HERDR_BIN, "pane", "split", "--pane", p, "--direction", "right"],
    "split_horizontal": lambda p, t, w: [HERDR_BIN, "pane", "split", "--pane", p, "--direction", "down"],
    "close_pane": lambda p, t, w: [HERDR_BIN, "pane", "close", p],
    "close_tab": lambda p, t, w: [HERDR_BIN, "tab", "close", t],
    "zoom": lambda p, t, w: [HERDR_BIN, "pane", "zoom", "--pane", p, "--toggle"],
    "new_tab": lambda p, t, w: [HERDR_BIN, "tab", "create", "--workspace", w, "--focus"],
    "new_workspace": lambda p, t, w: [HERDR_BIN, "workspace", "create", "--focus"],
    "reload_config": lambda p, t, w: [HERDR_BIN, "server", "reload-config"],
    # NOTE: the UI's confirm_close prompt for close_workspace has no CLI
    # equivalent (it's client-side), so this skips that confirmation.
    # There's no other way to invoke it from outside the client.
    "close_workspace": lambda p, t, w: [HERDR_BIN, "workspace", "close", w],
}


def _api_get(argv):
    result = subprocess.run(argv, capture_output=True, text=True, check=False)
    try:
        return json.loads(result.stdout).get("result", {})
    except (json.JSONDecodeError, AttributeError):
        return {}


def handle_tab_step(direction, env):
    ws = env.get("HERDR_ACTIVE_WORKSPACE_ID", "")
    tabs = _api_get([HERDR_BIN, "tab", "list", "--workspace", ws]).get("tabs", [])
    if not tabs:
        return
    idx = next((i for i, t in enumerate(tabs) if t.get("focused")), 0)
    new_idx = (idx + (1 if direction == "next" else -1)) % len(tabs)
    subprocess.run([HERDR_BIN, "tab", "focus", tabs[new_idx]["tab_id"]], check=False)


def handle_switch_tab(n, env):
    ws = env.get("HERDR_ACTIVE_WORKSPACE_ID", "")
    tabs = _api_get([HERDR_BIN, "tab", "list", "--workspace", ws]).get("tabs", [])
    if 1 <= n <= len(tabs):
        subprocess.run([HERDR_BIN, "tab", "focus", tabs[n - 1]["tab_id"]], check=False)


def handle_switch_workspace(n, env):
    workspaces = _api_get([HERDR_BIN, "workspace", "list"]).get("workspaces", [])
    if 1 <= n <= len(workspaces):
        subprocess.run([HERDR_BIN, "workspace", "focus", workspaces[n - 1]["workspace_id"]], check=False)


def handle_new_worktree(env):
    try:
        branch = input("New worktree branch (blank = default): ").strip()
    except EOFError:
        return
    argv = [HERDR_BIN, "worktree", "create", "--workspace", env.get("HERDR_ACTIVE_WORKSPACE_ID", "")]
    if branch:
        argv += ["--branch", branch]
    subprocess.run(argv, check=False)


def handle_rename(action, env):
    kind, id_var = RENAME_ACTIONS[action]
    try:
        new_label = input(f"New {kind} name: ").strip()
    except EOFError:
        return
    if not new_label:
        return
    subprocess.run([HERDR_BIN, kind, "rename", env[id_var], new_label], check=False)


def run_custom(cmd, env):
    command_str = cmd.get("command", "")
    if not command_str:
        return
    typ = cmd.get("type", "shell")
    if typ == "plugin_action":
        argv = [HERDR_BIN, "plugin", "action", "invoke", command_str]
        if cmd.get("plugin"):
            argv += ["--plugin", cmd["plugin"]]
        subprocess.run(argv, check=False)
        return
    # shell / pane / popup: herdr itself just runs `command` in those
    # contexts. We can't reproduce the popup/pane chrome from outside, so
    # (per the task) just run the same command string, detached.
    subprocess.Popen(["sh", "-c", command_str], start_new_session=True, env=env)


def show_reference(entry):
    print(f"'{entry['label']}' can't be triggered from outside herdr (client-side only UI).")
    print(f"Press it yourself: {entry['binding']}")
    try:
        input("Press Enter to close...")
    except EOFError:
        pass


def dispatch(entry, env):
    if entry["kind"] == "custom":
        run_custom(entry["cmd"], env)
        return
    if entry["kind"] == "reference":
        show_reference(entry)
        return
    action = entry["action"]
    if entry["kind"] == "rename":
        handle_rename(action, env)
        return
    if action == "previous_tab":
        handle_tab_step("previous", env)
        return
    if action == "next_tab":
        handle_tab_step("next", env)
        return
    if action == "switch_tab":
        handle_switch_tab(entry["index"], env)
        return
    if action == "switch_workspace":
        handle_switch_workspace(entry["index"], env)
        return
    if action == "new_worktree":
        handle_new_worktree(env)
        return
    argv_fn = CLI_MAPPING.get(action)
    if argv_fn:
        pane = env.get("HERDR_ACTIVE_PANE_ID", "")
        tab = env.get("HERDR_ACTIVE_TAB_ID", "")
        ws = env.get("HERDR_ACTIVE_WORKSPACE_ID", "")
        subprocess.run(argv_fn(pane, tab, ws), check=False)
    else:
        sys.stderr.write(f"herdr-command-palette: no way to trigger '{action}' from outside herdr.\n")


def main():
    if "--list" in sys.argv:
        entries = build_entries()
        for e in entries:
            print(f"{e['label']:<32} {e['key_display']:<20} {e['keywords']}")
        return

    env = os.environ.copy()
    if not env.get("HERDR_ACTIVE_PANE_ID"):
        die("HERDR_ACTIVE_PANE_ID is not set — run this from a herdr custom command.")

    if shutil.which(HERDR_BIN) is None:
        die(f"`{HERDR_BIN}` is not on PATH.")

    entries = build_entries()
    if not entries:
        die("no keybinding entries found.")

    fzf_input = build_fzf_input(entries)
    selection = run_fzf(fzf_input)

    try:
        idx = int(selection.rsplit("\x1f", 1)[-1])
        entry = entries[idx]
    except (ValueError, IndexError):
        sys.exit(0)

    dispatch(entry, env)


if __name__ == "__main__":
    main()
