import threading
import webbrowser
import tkinter.ttk as ttk
from tkinter.constants import END, N, S, E, W, LEFT, RIGHT, CENTER, NORMAL, DISABLED, SEL, INSERT, HORIZONTAL
import tkinter as tk
from tkinter import Text, StringVar
import sv_ttk
import pyttsx3
from pyttsx3 import engine
import re

from Core.speech_engine import SpeechEngine
from Core.speak_service import SpeakService
from Core.ui_dispatch import CallbackQueue
from Core.config import load_mcp_config
from Core.text_processing import preprocess_text, word_window, highlight_indices
from Core.voice_registry import VoiceRegistry
from Core.theme import load_ui_theme, palette, save_ui_theme, text_style, toggled
from Frames import dialogs
from Frames.chrome import apply_title_bar
from Frames.media_control import MediaControlMixin
from Frames.ui_pump import UiPumpMixin

class MainFrame(UiPumpMixin, MediaControlMixin, ttk.Frame):
    def __init__(self, **kw):
        ttk.Frame.__init__(self, **kw)
        self.callbacks = CallbackQueue()
        self.speech = SpeechEngine(
            self._queued(self.onStart), self._queued(self.onStartWord), self._queued(self.onEnd))
        self.speak_service = SpeakService(rate=500, speak_fn=self.speak_external)
        # Create + pump the pyttsx3 COM engine on ONE dedicated daemon thread.
        # It MUST NOT be created on this (tkinter main) thread, or SAPI5's word
        # callbacks fire on the pump thread with no Python thread state and crash
        # the process. prime_async builds it on the loop thread; get_voices then
        # waits for the voices that thread enumerated.
        self.speech.prime_async(500)
        self.voices = self.speech.get_voices()
        self.voice_registry = self._build_voice_registry()
        self.mcp_host = None  # set by the controller when MCP hosting is enabled
        self.spoken_text = ''
        self.highlight_index1 = None
        self.highlight_index2 = None
        self.media_was_paused = False  # Track if we paused media playback
        self.is_speaking = False
        self.stop_requested = False
        self.speech_thread = None
        self.current_session_id = 0
        self.speech_session_id = 0
        # For test compatibility - engine is None initially, then gets set by speech engine
        self.engine = None
        self.theme = load_ui_theme()
        self.build_frame_content(kw)
        self.pump_callbacks()

    def _build_voice_registry(self):
        """Build the agent voice registry from system voices + saved config.

        When the config lists no enabled voices, all system voices are enabled.
        """
        cfg = load_mcp_config()
        if cfg.voices:
            enabled = [(vid, name) for vid, name in self.voices if vid in cfg.voices]
        else:
            enabled = list(self.voices)
        return VoiceRegistry(enabled=enabled)

    def build_frame_content(self, kw):
        # Columns: 0 and 3 stretch, 1/2 hold the centred Speak/Stop buttons.
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)

        row_index = 0

        self.progress = ttk.Progressbar(self, orient=HORIZONTAL, mode="determinate")
        self.progress.grid(row=row_index, columnspan=4, sticky=(W, E))
        row_index += 1

        header = ttk.Frame(self)
        header.grid(row=row_index, column=0, columnspan=4, sticky=(W, E), pady=(16, 8))
        header.grid_columnconfigure(0, weight=1)
        self.title = ttk.Label(header, font=(UI_FONT, "28", "bold"), text="Speed Reader")
        self.title.grid(row=0, column=0, sticky=W)
        self.theme_button = ttk.Button(header, command=self.toggle_theme)
        self.theme_button.grid(row=0, column=1, sticky=E)
        row_index += 1

        # Fixed heights in points ("p") so they scale with DPI like the fonts do.
        self.spoken_words_container = ttk.Frame(self, height="30p")
        self.spoken_words_container.grid(row=row_index, column=0, columnspan=4, sticky=(N, S, W, E))
        self.spoken_words_container.grid_propagate(False)  # lock height so text length never resizes the window
        self.spoken_words_container.grid_rowconfigure(0, weight=1)
        self.spoken_words_container.grid_columnconfigure(0, weight=1)
        self.spoken_words = ttk.Label(self.spoken_words_container, font=("Georgia", "20"), justify=RIGHT, anchor=E)
        self.spoken_words.grid(row=0, column=0, sticky=(N, S, W, E))
        row_index += 1

        self.current_word_container = ttk.Frame(self, height="135p")
        self.current_word_container.grid(row=row_index, column=0, columnspan=4, sticky=(N, S, W, E))
        self.current_word_container.grid_propagate(False)  # lock height so word length never resizes the window
        self.current_word_container.grid_rowconfigure(0, weight=1)
        self.current_word_container.grid_columnconfigure(0, weight=1)
        self.current_word_label = ttk.Label(self.current_word_container, font=("Georgia", "96"), anchor=CENTER)
        self.current_word_label.grid(row=0, column=0, sticky=(N, S, W, E))
        row_index += 1

        self.next_words_container = ttk.Frame(self, height="30p")
        self.next_words_container.grid(row=row_index, column=0, columnspan=4, sticky=(N, S, W, E))
        self.next_words_container.grid_propagate(False)  # lock height so text length never resizes the window
        self.next_words_container.grid_rowconfigure(0, weight=1)
        self.next_words_container.grid_columnconfigure(0, weight=1)
        self.next_words = ttk.Label(self.next_words_container, font=("Georgia", "20"), anchor=W)
        self.next_words.grid(row=0, column=0, sticky=(N, S, W, E))
        row_index += 1

        self.settings_frame = ttk.Frame(self)
        self.settings_frame.grid(row=row_index, column=0, columnspan=4, sticky=(W, E), pady=12)
        self.settings_frame.grid_columnconfigure(5, weight=1)

        ttk.Label(self.settings_frame, text="Speed").grid(row=0, column=0, padx=(0, 8))
        self.speed_var = StringVar(master=self, value="500")
        self.speed_entry = ttk.Spinbox(
            self.settings_frame, from_=100, to=1000, increment=25, width=6, textvariable=self.speed_var, font=ENTRY_FONT)
        self.speed_entry.grid(row=0, column=1, padx=(0, 4))
        ttk.Label(self.settings_frame, text="WPM").grid(row=0, column=2, padx=(0, 24))
        self.speed_var.trace_add("write", self.on_rate_changed)

        ttk.Label(self.settings_frame, text="Voice").grid(row=0, column=3, padx=(0, 8))
        self.voice_var = StringVar(master=self)
        self.voice_combo = ttk.Combobox(
            self.settings_frame, textvariable=self.voice_var, state="readonly",
            width=30, values=[name for _, name in self.voices], font=ENTRY_FONT)
        self.voice_combo.grid(row=0, column=4, sticky=W)
        self.voice_combo.bind("<<ComboboxSelected>>", self.on_voice_changed)
        if self.voices:
            self.voice_var.set(self.voices[0][1])
            self.speech.set_voice(self.voices[0][0])
            # Reserve the user's voice so agents claim the other voices first.
            self.voice_registry.set_user_voice(self.voices[0][0])

        self.voice_settings_button = ttk.Button(
            self.settings_frame, text="Agent Voices…", command=lambda: dialogs.open_voice_settings(self))
        self.voice_settings_button.grid(row=0, column=6, padx=(8, 0))
        self.server_button = ttk.Button(
            self.settings_frame, text="Server…", command=lambda: dialogs.open_server_dialog(self))
        self.server_button.grid(row=0, column=7, padx=(8, 0))
        row_index += 1

        self.grid_rowconfigure(row_index, weight=1)
        self.text_area = Text(self, height=5, width=1, font=("Georgia", "28"), wrap="word",
                              relief="flat", borderwidth=0, padx=12, pady=10)
        self.text_area.grid(row=row_index, column=0, columnspan=4, sticky=(N, S, E, W))
        self.placeholder = tk.Label(
            self.text_area, font=(UI_FONT, "14"), cursor="xterm",
            text="Paste text here, or press Ctrl+B to paste & speak the clipboard.")
        self.placeholder.bind("<Button-1>", lambda e: self.text_area.focus_set())
        self.text_area.bind("<<Modified>>", self._on_text_modified)
        row_index += 1

        self.speak_button = ttk.Button(self, text="Speak", style="Accent.TButton", width=10)
        self.speak_button.grid(row=row_index, column=1, padx=(0, 4), pady=12)
        self.speak_button['state'] = NORMAL
        self.speak_button.bind("<Button-1>", self.speak)

        self.stop_button = ttk.Button(self, text="Stop", width=10)
        self.stop_button.grid(row=row_index, column=2, padx=(4, 0), pady=12)
        self.stop_button['state'] = DISABLED
        self.stop_button.bind("<Button-1>", self.stop)

        self.contribute_link = tk.Label(
            self, text="Contribute on GitHub", cursor="hand2", font=(UI_FONT, "10", "underline"))
        self.contribute_link.grid(row=row_index, column=3, sticky=E)
        self.contribute_link.bind("<Button-1>", lambda e: self.open_contribute())
        self._apply_theme_colors()
        self._update_placeholder()

        self.text_area.bind("<Control-Key-a>", self.select_all_text)
        self.text_area.bind("<Control-Key-A>", self.select_all_text)

        # Bind paste & speak to KeyRelease, not KeyPress: holding Ctrl+B fires
        # KeyPress repeatedly (auto-repeat) on Windows, which spammed dozens of
        # interrupting speech sessions and raced the Stop button into a bad
        # state. KeyRelease fires once per physical release, so each barge-in is
        # a single, clean interrupt.
        self.master.bind("<Control-KeyRelease-b>", self.paste_and_speak)
        self.master.bind("<Control-KeyRelease-B>", self.paste_and_speak)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        # Stop any ongoing speech and clean up resources
        self.force_stop_and_reset()
        self.master.destroy()
        self.master.quit()

    def open_contribute(self):
        webbrowser.open_new_tab(GITHUB_URL)

    def toggle_theme(self):
        """Switch dark <-> light, restyle non-ttk widgets and the title bar, persist."""
        self.theme = toggled(self.theme)
        sv_ttk.set_theme(self.theme, self.master)
        self.master.update()
        self._apply_theme_colors()
        apply_title_bar(self.master, self.theme)
        save_ui_theme(self.theme)

    def _apply_theme_colors(self):
        # tk (non-ttk) widgets aren't themed by sv-ttk, so colour them here.
        colors = palette(self.theme)
        self.text_area.configure(**text_style(self.theme))
        self.text_area.tag_config(TAG_CURRENT_WORD, foreground=colors["highlight"])
        self.placeholder.configure(background=colors["background"], foreground=colors["placeholder"])
        self.contribute_link.configure(background=colors["window"], foreground=colors["link"])
        self.theme_button["text"] = "Light mode" if self.theme == "dark" else "Dark mode"

    def _on_text_modified(self, event=None):
        self.text_area.edit_modified(False)  # re-arm <<Modified>> for the next change
        self._update_placeholder()

    def _update_placeholder(self):
        if self.text_area.get("1.0", "end-1c"):
            self.placeholder.place_forget()
        else:
            self.placeholder.place(x=14, y=12)

    def set_server_port(self, port):
        """Show the active MCP port on the Server button (host is up)."""
        self.server_button["text"] = "Server: {}…".format(port)

    def on_rate_changed(self, *args):
        # Keep the shared service rate in sync so MCP agents speak at the UI rate.
        try:
            self.speak_service.set_rate(int(self.speed_var.get()))
        except ValueError:
            pass

    def on_voice_changed(self, event=None):
        # Apply the picked voice to the shared engine (used by the GUI and MCP).
        selected = self.voice_var.get()
        for voice_id, voice_name in self.voices:
            if voice_name == selected:
                self.speech.set_voice(voice_id)
                # Re-reserve the user's voice so agents keep avoiding it.
                self.voice_registry.set_user_voice(voice_id)
                break

    def paste_and_speak(self, event):
        """Stop current speech, paste clipboard content, and start speaking."""
        # Force stop any current speech and reset state
        self.force_stop_and_reset()
        
        # Clear UI and insert new text
        self.clear_display_labels()
        self.text_area.delete("1.0", END)
        try:
            clipboard_text = self.master.clipboard_get()
            self.text_area.insert(END, clipboard_text)
        except Exception as e:
            print(f"Error getting clipboard: {e}")
            return
        
        # Start speaking the new text, interrupting (flushing) anything already
        # queued or playing so the pasted text plays now instead of waiting for
        # the queue to drain.
        self.speak(event, interrupt=True)

    def force_stop_and_reset(self):
        """Force stop current speech and reset engine for fresh start."""
        self.stop_requested = True
        
        # Increment session ID to invalidate any pending callbacks from old session
        self.speech_session_id += 1
        
        # Stop the current engine if running
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception as e:
                print(f"Error stopping engine: {e}")
            # Dispose of the engine - we'll create a fresh one
            self.engine = None
        
        # Wait briefly for the speech thread to finish
        if self.speech_thread is not None and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=0.5)
        
        # Reset state
        self.is_speaking = False
        self.stop_requested = False
        self.speak_button['state'] = NORMAL
        self.stop_button['state'] = DISABLED

    def clear_display_labels(self):
        """Clear all the display labels and progress."""
        self.spoken_words['text'] = ''
        self.current_word_label['text'] = ''
        self.next_words['text'] = ''
        self.progress["value"] = 0
        
        # Clear highlighting
        if self.highlight_index1 is not None:
            try:
                self.text_area.tag_remove(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)
            except Exception:
                pass
            self.highlight_index1 = None
            self.highlight_index2 = None

    def select_all_text(self, event):
        self.text_area.tag_add(SEL, "1.0", END)

    def stop(self, event):
        """Stop current speech when stop button is clicked."""
        if self.stop_button['state'].__str__() == NORMAL:
            self.speech.stop()
            self.speak_button['state'] = NORMAL
            self.stop_button['state'] = DISABLED

    def _is_stale_utterance(self, name):
        """True if a callback belongs to an interrupted/old user utterance.

        GUI utterances are tagged with their int session id via ``engine.say``,
        so an interrupted utterance's ``finished-utterance`` (which can arrive
        AFTER the new utterance's ``started-utterance`` during a Ctrl+B
        barge-in) doesn't disable the Stop button or resume paused media while
        the new speech is playing. Agent (MCP) speech passes no session id
        (name is ``None``), so it is never treated as stale here.
        """
        return isinstance(name, int) and name != self.current_session_id

    def onStart(self, name):
        """Called when an utterance starts."""
        # Ignore callbacks from old speech sessions
        if self._is_stale_utterance(name):
            return
        if self.current_session_id != self.speech_session_id:
            return
        self.is_speaking = True
        self.stop_requested = False
        self.speak_button['state'] = DISABLED
        self.stop_button['state'] = NORMAL
        
        # Pause any system media playing
        self.pause_system_media()
        print(f"onStart: {name}")

    def onStartWord(self, name, location, length):
        if self._is_stale_utterance(name):
            return
        spoken, current, next_ = word_window(self.spoken_text, location, length)
        self.spoken_words['text'] = spoken
        self.current_word_label['text'] = current
        self.next_words['text'] = next_
        if self.highlight_index1 is not None:
            self.text_area.tag_remove(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)
        self.highlight_index1, self.highlight_index2 = highlight_indices(location, length)
        self.text_area.see(self.highlight_index1)
        self.text_area.tag_add(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)

        self.progress["maximum"] = self.spoken_text.__len__()
        self.progress["value"] = location

    def onEnd(self, name, completed):
        """Called when an utterance finishes.
        
        Args:
            name: The name of the utterance that finished
            completed: True if speech completed normally, False if interrupted
        """
        # Check if this is from an old speech session (a new speech started)
        is_old_session = self._is_stale_utterance(name) or \
            self.current_session_id != self.speech_session_id
        
        if is_old_session:
            print(f"onEnd: {name} - ignored (old session)")
            return
            
        self.is_speaking = False
        self.speak_button['state'] = NORMAL
        self.stop_button['state'] = DISABLED
        
        if completed:
            # Speech completed normally - update progress to 100%
            self.progress["maximum"] = self.spoken_text.__len__()
            self.progress["value"] = self.spoken_text.__len__()
            print(f"onEnd: {name} - completed successfully")
        else:
            # Speech was interrupted/stopped
            print(f"onEnd: {name} - interrupted")
        
        # Clear the current word highlight
        if self.highlight_index1 is not None:
            try:
                self.text_area.tag_remove(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)
            except Exception:
                pass
            self.highlight_index1 = None
            self.highlight_index2 = None
        
        # Resume any system media we paused, but only if this session wasn't
        # interrupted by a new speech session starting
        self.resume_system_media()

    def onError(self, name, exception):
        """Called when an error occurs during speech.
        
        Args:
            name: The name of the utterance that had an error
            exception: The exception that occurred
        """
        # Ignore callbacks from old speech sessions
        if self.current_session_id != self.speech_session_id:
            return
            
        self.is_speaking = False
        self.speak_button['state'] = NORMAL
        self.stop_button['state'] = DISABLED
        print(f"onError: {name} - {exception}")
        
        # Clear highlighting on error
        if self.highlight_index1 is not None:
            try:
                self.text_area.tag_remove(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)
            except Exception:
                pass
            self.highlight_index1 = None
            self.highlight_index2 = None
        
        # Resume any system media we paused
        self.resume_system_media()

    def speak(self, event, interrupt=False):
        if self.speak_button['state'].__str__() == NORMAL:
            self.spoken_text = preprocess_text(self.text_area.get("1.0", END))
            self.text_area.delete("1.0", END)
            self.text_area.insert(END, self.spoken_text)

            speech_speed = int(self.speed_entry.get())
            
            # Increment session ID for this new speech and mark it active so the
            # engine callbacks (onStart/onStartWord/onEnd) recognize it instead
            # of treating it as a stale session and bailing out — that bail-out
            # is what previously left the Stop button disabled while speaking.
            self.speech_session_id += 1
            session_id = self.speech_session_id
            self.current_session_id = session_id

            self.thread = threading.Thread(target=self.speak_on_thread, args=(speech_speed, self.spoken_text, interrupt, session_id))
            self.thread.daemon = True
            self.thread.start()

    def speak_on_thread(self, speech_speed, spoken_text, interrupt=False, name=None):
        self.speech.speak(spoken_text, speech_speed, interrupt=interrupt, name=name)

    def speak_external(self, text, rate, voice=None):
        # Entry point for MCP agent speech (called from the server thread).
        # Update the UI on the tkinter main thread, but run the BLOCKING speak on
        # this server thread (never inside `after`, which would freeze the UI).
        # Blocking serializes per-utterance voices so agents don't bleed voices.
        self.after(0, lambda: self._render_external(text))
        self.speech.speak(text, rate, voice=voice, block=True)

    def _render_external(self, text):
        self.spoken_text = text
        self.text_area.delete("1.0", END)
        self.text_area.insert(END, text)


TAG_CURRENT_WORD = "current word"
GITHUB_URL = "https://github.com/ChrisLucian/SpeedReader"
UI_FONT = "Segoe UI Variable Display"
# sv-ttk named font; set explicitly because the theme is applied before entries exist.
ENTRY_FONT = "SunValleyBodyFont"
