---
title: Laptop function keys
description: Volume, display brightness, and keyboard backlight keys that only appear on laptop hardware.
---

This dotfiles repo is applied to more than one machine, so the ThinkPad's Fn-row
media keys (volume, display brightness, keyboard backlight) can't just be bound
unconditionally in i3's config — a desktop has no backlight to adjust. Instead,
both the keybindings and the packages/permissions behind them detect the hardware
themselves, so the exact same source files are a correct no-op on a machine that
isn't a laptop.

## Two gates, one property

**chezmoi side** — `private_dot_config/i3/config.tmpl` wraps the media-key bindsyms
in a template conditional that shells out to `hostnamectl`:

```
{{ if eq (output "hostnamectl" "chassis" | trim) "laptop" -}}
bindsym XF86AudioRaiseVolume exec --no-startup-id wpctl set-volume -l 1.0 @DEFAULT_AUDIO_SINK@ 5%+
bindsym XF86AudioLowerVolume exec --no-startup-id wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-
bindsym XF86AudioMute        exec --no-startup-id wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle

bindsym XF86MonBrightnessUp   exec --no-startup-id brightnessctl set 5%+
bindsym XF86MonBrightnessDown exec --no-startup-id brightnessctl set 5%-

bindsym XF86KbdBrightnessUp   exec --no-startup-id brightnessctl --device='tpacpi::kbd_backlight' set 1+
bindsym XF86KbdBrightnessDown exec --no-startup-id brightnessctl --device='tpacpi::kbd_backlight' set 1-
{{ end -}}
```

`output` runs a command at template-render time and inlines its stdout — no manual
per-machine data file to maintain, it just asks the machine what it is.

**Ansible side** — `dot_bootstrap/setup.yml` gates the matching system-level work on
Ansible's own hardware fact, `ansible_form_factor`, checked against a small list of
laptop-ish DMI chassis types (`Laptop`, `Notebook`, `Portable`, `Sub Notebook`):

```yaml
vars:
  laptop_form_factors:
    - Laptop
    - Notebook
    - Portable
    - Sub Notebook
```

Every laptop-only task carries `when: ansible_form_factor in laptop_form_factors`.

## What the Ansible side actually sets up

1. **Installs `brightnessctl` and `pipewire-audio`** — `brightnessctl` drives both
   the display backlight (`/sys/class/backlight`) and the keyboard backlight
   (`/sys/class/leds/*kbd_backlight`); `pipewire-audio` guarantees `wpctl`
   (WirePlumber's CLI) is present for volume control.
2. **Adds the user to the `video` group.**
3. **Installs a udev rule.** Ubuntu's `brightnessctl` package ships no udev rule of
   its own, so both backlight sysfs nodes stay `root:root 0644` — unwritable by a
   normal user. A rule at `/etc/udev/rules.d/90-backlight.rules` hands them to the
   `video` group instead:

   ```
   SUBSYSTEM=="backlight", ACTION=="add", RUN+="/bin/chgrp video $sys$devpath/brightness", RUN+="/bin/chmod g+w $sys$devpath/brightness"
   SUBSYSTEM=="leds", KERNEL=="*kbd_backlight", ACTION=="add", RUN+="/bin/chgrp video $sys$devpath/brightness", RUN+="/bin/chmod g+w $sys$devpath/brightness"
   ```

4. **Reloads and re-triggers udev** (only when the rule file actually changed) so it
   takes effect immediately, without a reboot.

:::caution
The `video` group membership doesn't apply to an already-open login session — log
out and back in (or at least restart i3) after the playbook runs, before testing
the brightness keys. Volume keys work immediately since they don't touch group
membership.
:::

## Why not just a hostname list

A `case $HOSTNAME in ...` style list would work until the next laptop shows up, at
which point every conditional in the repo needs a new entry. Asking the hardware
directly (`hostnamectl chassis`, `ansible_form_factor`) means a brand-new laptop
gets these features automatically the first time this repo is applied to it — the
same way `chezmoi init --apply` already works for everything else.
