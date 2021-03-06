local wezterm = require 'wezterm'
local running_on_windows = wezterm.target_triple == "x86_64-pc-windows-msvc"

local config = {
  color_scheme = "Homebrew",
  audible_bell = "Disabled",
  default_cursor_style = "SteadyUnderline",
  default_cwd = "~",
  exit_behavior = "Close",
  swallow_mouse_click_on_pane_focus = true,
  tab_bar_at_bottom = true,
  window_close_confirmation = "NeverPrompt",
  window_decorations = "RESIZE",
  keys = {
    -- This will create a new split and run your default program inside it
    {key="v", mods="CTRL|SHIFT|ALT",
      action=wezterm.action{SplitVertical={domain="CurrentPaneDomain"}}},
    {key="h", mods="CTRL|SHIFT|ALT",
      action=wezterm.action{SplitHorizontal={domain="CurrentPaneDomain"}}},
  },
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
    "Fira Code",
    "Symbols Nerd Font",
  }),
  default_cwd = "~"
}

if running_on_windows then
  config["default_prog"] = { "wsl.exe", "--cd", "~" }
  config["add_wsl_distributions_to_launch_menu"] = false
  config["launch_menu"] = {
    {
      label = "PowerShell",
      args = {"pwsh.exe"},
    },
    {
      label = "zsh",
      args = { "wsl.exe", "--cd", "~" }
    }
  }
end

wezterm.on("update-right-status", function(window, pane)
  -- "Wed Mar 3 08:14"
  local date = wezterm.strftime("%A, %b %-d @ %H:%M:%S ");

  local bat = ""
  for _, b in ipairs(wezterm.battery_info()) do
    if b.state == "Charging" then
        bat = "🔌"
    end
    bat = bat .. "🔋" .. string.format("%.0f%%", b.state_of_charge * 100)
   end

  window:set_right_status(wezterm.format({
    {Text=bat .. "   "..date},
  }));
end)

return config
