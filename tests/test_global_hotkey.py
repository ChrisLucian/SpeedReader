"""System-wide hotkey, driven by a scripted fake user32 (no real Win32 calls)."""
from Core.global_hotkey import GlobalHotkey, MOD_ALT, MOD_CONTROL, MOD_NOREPEAT

WM_HOTKEY = 0x0312
WM_TIMER = 0x0113


class FakeUser32:
    def __init__(self, messages=(), registers=True):
        self.messages = list(messages)
        self.registers = registers
        self.calls = []

    def RegisterHotKey(self, *args):
        self.calls.append(("RegisterHotKey", args))
        return 1 if self.registers else 0

    def UnregisterHotKey(self, *args):
        self.calls.append(("UnregisterHotKey", args))
        return 1

    def GetMessageW(self, msg_ref, *args):
        self.calls.append(("GetMessageW", args))
        if not self.messages:
            return 0
        msg_ref._obj.message = self.messages.pop(0)
        return 1

    def PostThreadMessageW(self, *args):
        self.calls.append(("PostThreadMessageW", args))
        return 1

    def called(self, name):
        return [args for call, args in self.calls if call == name]


def test_hotkey_registers_ctrl_alt_b():
    fake = FakeUser32()
    GlobalHotkey(lambda: None, user32=fake).run()
    assert fake.called("RegisterHotKey") == [(None, 1, MOD_CONTROL | MOD_ALT | MOD_NOREPEAT, 0x42)]


def test_hotkey_message_calls_on_press():
    presses = []
    GlobalHotkey(lambda: presses.append(1), user32=FakeUser32([WM_HOTKEY])).run()
    assert presses == [1]


def test_hotkey_ignores_other_messages():
    presses = []
    GlobalHotkey(lambda: presses.append(1), user32=FakeUser32([WM_TIMER])).run()
    assert presses == []


def test_hotkey_failed_registration_skips_pump():
    fake = FakeUser32([WM_HOTKEY], registers=False)
    hotkey = GlobalHotkey(lambda: None, user32=fake)
    hotkey.run()
    assert hotkey.registered is False
    assert fake.called("GetMessageW") == []


def test_hotkey_unregisters_when_loop_ends():
    fake = FakeUser32()
    GlobalHotkey(lambda: None, user32=fake).run()
    assert fake.called("UnregisterHotKey") == [(None, 1)]


def test_hotkey_stop_posts_quit_to_its_thread():
    fake = FakeUser32()
    hotkey = GlobalHotkey(lambda: None, user32=fake)
    hotkey.thread_id = 42
    hotkey.stop()
    assert fake.called("PostThreadMessageW") == [(42, 0x0012, 0, 0)]
