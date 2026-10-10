"""Pause/Resume and read-from-word, driven without real speech."""


def test_word_location_is_shifted_by_speak_offset(frame):
    frame.spoken_text = "Hello World"
    frame.speak_offset = 6
    frame.onStartWord(None, 0, 5)
    assert frame.current_word_label["text"] == "World"
