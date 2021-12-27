local wezterm = require 'wezterm'
local running_on_windows = wezterm.target_triple == "x86_64-pc-windows-msvc"

local config = {
  color_scheme = "OneHalfDark",
  audible_bell = "Disabled",
  default_cursor_style = "SteadyUnderline",
  default_cwd = "~",
  exit_behavior = "Close",
  swallow_mouse_click_on_pane_focus = true,
  tab_bar_at_bottom = true,
  window_close_confirmation = "NeverPrompt",
  window_decorations = "RESIZE",
  visual_bell = {
    fade_in_duration_ms = 75,
    fade_out_duration_ms = 75,
    target = "CursorColor",
  },
  colors = {
    visual_bell = "#202020",
  },
  font_size = 9.0,
  font = wezterm.font_with_fallback({
    {
      family="FiraCode NF",
      harfbuzz_features={"calt=1", "clig=1", "liga=1"},
    },
    "Cozette",
  })
}

if running_on_windows then
  local wsl_distro = "kali-linux"

  config["default_prog"] = {
    "wsl.exe", "--distribution", wsl_distro, "--cd", "~"
  }
  config["add_wsl_distributions_to_launch_menu"] = false
  config["launch_menu"] = {
    {
      label = "Powershell",
      args = {"powershell.exe"},
      cwd = "~",
    },
    {
      label = "zsh",
      args = {"wsl.exe", "--distribution", wsl_distro},
      cwd = "~",
    }
  }
end

return config
