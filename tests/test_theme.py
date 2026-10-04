import json

from Core.theme import load_ui_theme, palette, save_ui_theme, text_style, toggled


def test_theme_defaults_to_dark_when_no_file(tmp_path):
    assert load_ui_theme(str(tmp_path / "missing.json")) == "dark"


def test_loads_light_theme(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"ui": {"theme": "light"}}))
    assert load_ui_theme(str(path)) == "light"


def test_unknown_theme_falls_back_to_dark(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"ui": {"theme": "neon"}}))
    assert load_ui_theme(str(path)) == "dark"


def test_dark_text_style_is_light_on_dark():
    style = text_style("dark")
    assert style["background"] != style["foreground"]
    assert style["background"].lower() < "#5"  # dark background
    assert style["insertbackground"] == style["foreground"]


def test_light_text_style_and_distinct_highlight():
    light, dark = text_style("light"), text_style("dark")
    assert light["background"] != dark["background"]
    colors = palette("light")
    assert colors["highlight"] not in (colors["foreground"], colors["background"])


def test_palette_matches_text_style_and_has_ui_colours():
    for theme in ("dark", "light"):
        colors = palette(theme)
        assert colors["background"] == text_style(theme)["background"]
        assert {"placeholder", "link", "highlight"} <= colors.keys()
        assert colors["placeholder"] != colors["background"]


def test_toggled_flips_between_dark_and_light():
    assert toggled("dark") == "light"
    assert toggled("light") == "dark"


def test_save_ui_theme_round_trips_and_preserves_mcp(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"mcp": {"enabled": True}}))
    save_ui_theme("light", path=str(path))
    assert load_ui_theme(str(path)) == "light"
    assert json.loads(path.read_text())["mcp"] == {"enabled": True}


def test_text_style_has_visible_border():
    for theme in ("dark", "light"):
        style = text_style(theme)
        assert style["highlightthickness"] == 1
        assert style["highlightbackground"] != style["background"]
