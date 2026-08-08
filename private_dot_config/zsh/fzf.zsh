# =========================================================
# fzf
# =========================================================

if command -v fd >/dev/null 2>&1; then
  export FZF_DEFAULT_COMMAND='fd --type f --hidden --strip-cwd-prefix'  # strip-cwd-prefix removes the leading ./ from result9;6u
elif command -v fdfind >/dev/null 2>&1; then
  export FZF_DEFAULT_COMMAND='fdfind --type f --hidden --strip-cwd-prefix'
fi

# Ctrl-T uses fd
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# UI
export FZF_DEFAULT_OPTS='
  --height=60%
  --layout=reverse
  --border=rounded
  --prompt="  "
  --pointer="  "
  --preview-window=right:65%:wrap:border-left
'

if command -v bat >/dev/null 2>&1; then
  _fzf_bat_cmd='bat'
elif command -v batcat >/dev/null 2>&1; then
  _fzf_bat_cmd='batcat'
else
  _fzf_bat_cmd='cat'
fi

# Render images inline (Kitty/iTerm/sixel graphics protocol) when chafa is
# available; ghostty and most modern terminals support this. Falls back to
# bat/cat for everything else.
if command -v chafa >/dev/null 2>&1; then
  # Kitty graphics protocol: delete all previously placed images first.
  # Ghostty (like real kitty) treats placed images as a layer separate from
  # the text grid, so a normal screen clear does NOT remove them -- without
  # this, the last preview image lingers on screen after moving to the next
  # file. chafa's own --clear only sends a plain ESC[2J, which doesn't touch
  # that layer, hence the explicit delete-all-placements escape here.
  export _fzf_kitty_img_clear=$'\e_Ga=d,d=A\e\\'
  _fzf_image_case='*.png|*.jpg|*.jpeg|*.gif|*.bmp|*.webp|*.tiff|*.tif|*.ico|*.avif|*.qoi|*.svg)
    printf "%s" "$_fzf_kitty_img_clear"; chafa --animate=off --size="${FZF_PREVIEW_COLUMNS}x${FZF_PREVIEW_LINES}" {} ;;
  '
else
  _fzf_image_case=""
fi

export _FZF_PREVIEW_CMD="case {} in
  ${_fzf_image_case}*)
    $_fzf_bat_cmd --color=always --style=plain,numbers --line-range=:500 {} ;;
esac"
export FZF_CTRL_T_OPTS="--preview '$_FZF_PREVIEW_CMD'"

# Ctrl+F: file picker excluding hidden files
_fzf_file_no_hidden() {
  local cmd result
  cmd="${FZF_DEFAULT_COMMAND/--hidden /}"
  result=$(eval "${cmd:-find . -type f}" | fzf --preview "$_FZF_PREVIEW_CMD") \
    && LBUFFER+="$result"  # LBUFFER is the text left of the cursor
  zle reset-prompt
}
zle -N _fzf_file_no_hidden
