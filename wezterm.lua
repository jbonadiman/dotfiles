local wezterm = require 'wezterm'

local wsl_distro = "kali-linux"

return {
	color_scheme = "OneHalfDark",
	audible_bell = "Disabled",
	default_cursor_style = "SteadyUnderline",
	default_cwd = "~",
	default_prog = {"wsl.exe", "--distribution", wsl_distro, "--cd", "~"},
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
	font_size = 13.0,
	font = wezterm.font({
		"Cozette",
	}),

	add_wsl_distributions_to_launch_menu = false,
	launch_menu = {
		{
			label = "Powershell",
			args = {"powershell.exe"},
			cwd = "~",
		},
		{
			label = "zsh",
			args = {"wsl.exe", "--distribution", wsl_distro},
			cwd = "~",
		},
	}
}
