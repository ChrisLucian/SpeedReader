"""MainFrame wiring for the configurable speech engine (OneCore / SAPI)."""
from Core.config import save_enabled_voices


def test_voice_registry_falls_back_to_all_voices_when_saved_ids_unknown(frame):
    save_enabled_voices(['id-from-the-other-engine'])

    registry = frame._build_voice_registry()

    assert registry.enabled() == list(frame.voices)
