"""MainFrame wiring for the configurable speech engine (OneCore / SAPI)."""
import Frames.MainFrame as MainFrame
from Core.config import save_enabled_voices, update_config_section
from Core.speech_engine import SpeechEngine


def test_voice_registry_falls_back_to_all_voices_when_saved_ids_unknown(frame):
    save_enabled_voices(['id-from-the-other-engine'])

    registry = frame._build_voice_registry()

    assert registry.enabled() == list(frame.voices)


def test_main_frame_builds_engine_from_configured_choice(monkeypatch, new_controller):
    update_config_section('speech', {'engine': 'sapi'})
    names = []

    def recording_factory(name, *callbacks):
        names.append(name)
        return SpeechEngine(*callbacks)

    monkeypatch.setattr(MainFrame, 'create_speech_engine', recording_factory, raising=False)

    controller = new_controller()
    controller.destroy()

    assert names == ['sapi']
