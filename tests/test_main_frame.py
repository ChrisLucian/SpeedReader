"""Unit tests for MainFrame using shared fixtures."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from tkinter.constants import NORMAL, DISABLED, END, SEL
from Frames.MainFrame import TAG_CURRENT_WORD


class TestMainFrameInitialization:
    """Tests for MainFrame initialization and widget setup."""

    def test_speed_entry_default_value_is_500(self, frame):
        """Speed entry should default to 500 WPM."""
        # Act
        speed_value = frame.speed_entry.get()

        # Assert
        assert speed_value == "500"

    def test_speak_button_initial_state_is_normal(self, frame):
        """Speak button should be enabled initially."""
        # Act
        state = str(frame.speak_button['state'])

        # Assert
        assert state == NORMAL

    def test_stop_button_initial_state_is_disabled(self, frame):
        """Stop button should be disabled initially."""
        # Act
        state = str(frame.stop_button['state'])

        # Assert
        assert state == DISABLED

    def test_title_label_text_is_speed_reader(self, frame):
        """Title label should display 'Speed Reader'."""
        # Act
        title_text = frame.title['text']

        # Assert
        assert title_text == "Speed Reader"

    def test_text_area_is_initially_empty(self, frame):
        """Text area should be empty on initialization."""
        # Act
        text_content = frame.text_area.get("1.0", END).strip()

        # Assert
        assert text_content == ""

    def test_engine_is_none_initially(self, frame):
        """TTS engine should not be initialized until first use."""
        # Act
        engine = frame.engine

        # Assert
        assert engine is None

    def test_progress_bar_exists(self, frame):
        """Progress bar should be created."""
        # Assert
        assert frame.progress is not None

    def test_spoken_words_label_is_empty_initially(self, frame):
        """Spoken words label should be empty initially."""
        # Act
        spoken_text = frame.spoken_words['text']

        # Assert
        assert spoken_text == ""

    def test_current_word_label_is_empty_initially(self, frame):
        """Current word label should be empty initially."""
        # Act
        current_word = frame.current_word_label['text']

        # Assert
        assert current_word == ""

    def test_next_words_label_is_empty_initially(self, frame):
        """Next words label should be empty initially."""
        # Act
        next_words = frame.next_words['text']

        # Assert
        assert next_words == ""


class TestMainFrameSelectAllText:
    """Tests for select all text functionality."""

    def test_select_all_text_selects_entire_content(self, app, frame):
        """Ctrl+A should select all text in text area."""
        # Arrange
        test_text = "Hello World"
        frame.text_area.insert(END, test_text)

        # Act
        frame.select_all_text(None)
        app.update()

        # Assert
        try:
            selected = frame.text_area.get(SEL + ".first", SEL + ".last")
            assert test_text in selected
        except Exception:
            pytest.fail("No text was selected")


class TestMainFrameButtonStates:
    """Tests for button state management."""

    def test_on_start_disables_speak_button(self, frame):
        """onStart callback should disable speak button."""
        # Act
        frame.onStart("test")

        # Assert
        assert str(frame.speak_button['state']) == DISABLED

    def test_on_start_enables_stop_button(self, frame):
        """onStart callback should enable stop button."""
        # Act
        frame.onStart("test")

        # Assert
        assert str(frame.stop_button['state']) == NORMAL

    def test_on_end_enables_speak_button(self, frame):
        """onEnd callback should enable speak button."""
        # Arrange
        frame.spoken_text = "test"
        frame.speak_button['state'] = DISABLED

        # Act
        frame.onEnd("test", True)

        # Assert
        assert str(frame.speak_button['state']) == NORMAL

    def test_on_end_disables_stop_button(self, frame):
        """onEnd callback should disable stop button."""
        # Arrange
        frame.spoken_text = "test"
        frame.stop_button['state'] = NORMAL

        # Act
        frame.onEnd("test", True)

        # Assert
        assert str(frame.stop_button['state']) == DISABLED


class TestMainFrameWordHighlighting:
    """Tests for word highlighting during speech."""

    def test_on_start_word_updates_current_word_label(self, frame):
        """onStartWord should update current word label."""
        # Arrange
        frame.spoken_text = "Hello World Test"
        frame.text_area.insert(END, frame.spoken_text)

        # Act
        frame.onStartWord("test", 0, 5)

        # Assert
        assert frame.current_word_label['text'] == "Hello"

    def test_on_start_word_updates_next_words_label(self, frame):
        """onStartWord should update next words label."""
        # Arrange
        frame.spoken_text = "Hello World Test"
        frame.text_area.insert(END, frame.spoken_text)

        # Act
        frame.onStartWord("test", 0, 5)

        # Assert
        assert " World Test" in frame.next_words['text']

    def test_on_start_word_updates_spoken_words_label(self, frame):
        """onStartWord should update spoken words (trailing text)."""
        # Arrange
        frame.spoken_text = "Hello World Test"
        frame.text_area.insert(END, frame.spoken_text)

        # Act
        frame.onStartWord("test", 6, 5)  # "World" starts at 6

        # Assert
        assert "Hello " in frame.spoken_words['text']

    def test_on_start_word_updates_progress_bar(self, frame):
        """onStartWord should update progress bar value."""
        # Arrange
        frame.spoken_text = "Hello World Test"
        frame.text_area.insert(END, frame.spoken_text)

        # Act
        frame.onStartWord("test", 6, 5)

        # Assert
        assert frame.progress["value"] == 6
        assert frame.progress["maximum"] == len(frame.spoken_text)

    def test_on_start_word_sets_highlight_indices(self, frame):
        """onStartWord should set highlight indices for current word."""
        # Arrange
        frame.spoken_text = "Hello World"
        frame.text_area.insert(END, frame.spoken_text)

        # Act
        frame.onStartWord("test", 0, 5)

        # Assert
        assert frame.highlight_index1 == "1.0"
        assert frame.highlight_index2 == "1.5"


class TestMainFrameProgressBar:
    """Tests for progress bar behavior."""

    def test_on_end_sets_progress_to_maximum(self, frame):
        """onEnd should set progress bar to 100%."""
        # Arrange
        frame.spoken_text = "Hello World"

        # Act
        frame.onEnd("test", True)

        # Assert
        assert frame.progress["value"] == len(frame.spoken_text)
        assert frame.progress["maximum"] == len(frame.spoken_text)


class TestMainFrameTextProcessing:
    """Tests for text processing before speech."""

    @patch('Frames.MainFrame.threading.Thread')
    def test_speak_replaces_urls_with_placeholder(self, mock_thread, frame):
        """URLs in text should be replaced with [URL] placeholder."""
        # Arrange
        mock_thread.return_value.daemon = True
        mock_thread.return_value.start = Mock()
        frame.text_area.insert(END, "Check https://example.com for info")

        # Act
        frame.speak(None)

        # Assert
        assert "[URL]" in frame.spoken_text
        assert "https://example.com" not in frame.spoken_text

    @patch('Frames.MainFrame.threading.Thread')
    def test_speak_replaces_newlines_with_spaces(self, mock_thread, frame):
        """Newlines in text should be replaced with spaces."""
        # Arrange
        mock_thread.return_value.daemon = True
        mock_thread.return_value.start = Mock()
        frame.text_area.insert(END, "Hello\nWorld")

        # Act
        frame.speak(None)

        # Assert
        assert "\n" not in frame.spoken_text.rstrip()
        assert "Hello World" in frame.spoken_text

    @patch('Frames.MainFrame.threading.Thread')
    def test_speak_uses_speed_from_entry(self, mock_thread, frame):
        """Speech should use the speed value from the entry field."""
        # Arrange
        mock_thread.return_value.daemon = True
        mock_thread.return_value.start = Mock()
        frame.speed_entry.delete(0, END)
        frame.speed_entry.insert(0, "300")
        frame.text_area.insert(END, "Test text")

        # Act
        frame.speak(None)

        # Assert
        mock_thread.assert_called_once()
        call_args = mock_thread.call_args
        assert call_args[1]['args'][0] == 300  # speech_speed argument

    @patch('Frames.MainFrame.threading.Thread')
    def test_speak_does_nothing_when_button_disabled(self, mock_thread, frame):
        """Speak should not start when speak button is disabled."""
        # Arrange
        frame.speak_button['state'] = DISABLED
        frame.text_area.insert(END, "Test text")

        # Act
        frame.speak(None)

        # Assert
        mock_thread.assert_not_called()


class TestMainFrameStopFunctionality:
    """Tests for stop functionality."""

    def test_stop_does_nothing_when_button_disabled(self, frame):
        """Stop should not act when stop button is disabled."""
        # Arrange
        frame.stop_button['state'] = DISABLED
        frame.engine = Mock()

        # Act
        frame.stop(None)

        # Assert
        frame.engine.stop.assert_not_called()

    def test_stop_calls_engine_stop_when_enabled(self, frame):
        """Stop should call engine.stop() when stop button is enabled."""
        # Arrange
        frame.stop_button['state'] = NORMAL
        frame.engine = Mock()

        # Act
        frame.stop(None)

        # Assert
        frame.engine.stop.assert_called_once()

    def test_stop_enables_speak_button(self, frame):
        """Stop should enable the speak button."""
        # Arrange
        frame.stop_button['state'] = NORMAL
        frame.speak_button['state'] = DISABLED
        frame.engine = Mock()

        # Act
        frame.stop(None)

        # Assert
        assert str(frame.speak_button['state']) == NORMAL

    def test_stop_disables_stop_button(self, frame):
        """Stop should disable the stop button."""
        # Arrange
        frame.stop_button['state'] = NORMAL
        frame.engine = Mock()

        # Act
        frame.stop(None)

        # Assert
        assert str(frame.stop_button['state']) == DISABLED


class TestMainFramePasteAndSpeak:
    """Tests for paste and speak functionality."""

    @patch('Frames.MainFrame.threading.Thread')
    def test_paste_and_speak_clears_text_area(self, mock_thread, app, frame):
        """Paste and speak should clear existing text."""
        # Arrange
        mock_thread.return_value.daemon = True
        mock_thread.return_value.start = Mock()
        frame.text_area.insert(END, "Old text")
        app.clipboard_clear()
        app.clipboard_append("New text")

        # Act
        frame.paste_and_speak(None)

        # Assert
        assert "Old text" not in frame.text_area.get("1.0", END)

    @patch('Frames.MainFrame.threading.Thread')
    def test_paste_and_speak_inserts_clipboard_content(self, mock_thread, app, frame):
        """Paste and speak should insert clipboard content."""
        # Arrange
        mock_thread.return_value.daemon = True
        mock_thread.return_value.start = Mock()
        app.clipboard_clear()
        app.clipboard_append("Clipboard text")

        # Act
        frame.paste_and_speak(None)

        # Assert
        assert "Clipboard text" in frame.text_area.get("1.0", END)


class TestMainFrameTTSEngine:
    """Tests for TTS engine initialization and usage."""

    @patch('Frames.MainFrame.pyttsx3.init')
    def test_speak_on_thread_initializes_engine_on_first_call(self, mock_init, frame):
        """Engine should be initialized on first speak_on_thread call."""
        # Arrange
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        frame.engine = None

        # Act
        frame.speak_on_thread(500, "Test")

        # Assert
        mock_init.assert_called_once()

    @patch('Frames.MainFrame.pyttsx3.init')
    def test_speak_on_thread_sets_speech_rate(self, mock_init, frame):
        """Engine should have rate set to specified speed."""
        # Arrange
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        frame.engine = None

        # Act
        frame.speak_on_thread(350, "Test")

        # Assert
        mock_engine.setProperty.assert_any_call('rate', 350)

    @patch('Frames.MainFrame.pyttsx3.init')
    def test_speak_on_thread_connects_callbacks(self, mock_init, frame):
        """Engine should connect all required callbacks."""
        # Arrange
        mock_engine = MagicMock()
        mock_init.return_value = mock_engine
        frame.engine = None

        # Act
        frame.speak_on_thread(500, "Test")

        # Assert
        connect_calls = [call[0] for call in mock_engine.connect.call_args_list]
        assert ('started-utterance', frame.onStart) in connect_calls
        assert ('started-word', frame.onStartWord) in connect_calls
        assert ('finished-utterance', frame.onEnd) in connect_calls

    @patch('Frames.MainFrame.pyttsx3.init')
    def test_speak_on_thread_reuses_existing_engine(self, mock_init, frame):
        """Subsequent calls should reuse existing engine."""
        # Arrange
        mock_engine = MagicMock()
        frame.engine = mock_engine

        # Act
        frame.speak_on_thread(500, "Test")

        # Assert
        mock_init.assert_not_called()
        mock_engine.say.assert_called_once_with("Test")
