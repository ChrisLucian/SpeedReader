"""F11 focus mode for MainFrame: hide everything but the reading display."""


class FocusModeMixin:
    """Mixed into MainFrame; uses ``text_area`` and ``settings_frame``."""

    def toggle_focus(self, event=None):
        for widget in (self.text_area, self.settings_frame):
            widget.grid_remove()
