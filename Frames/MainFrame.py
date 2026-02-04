import threading
import tkinter.ttk as ttk
from tkinter.constants import END, N, S, E, W, NORMAL, DISABLED, RIGHT, CENTER, SEL, INSERT, HORIZONTAL
from tkinter import Text
import pyttsx3
from pyttsx3 import engine
import re

class MainFrame(ttk.Frame):
    def __init__(self, **kw):
        ttk.Frame.__init__(self, **kw)
        self.engine = None
        self.engine_lock = threading.Lock()
        self.is_speaking = False
        self.stop_requested = False
        self.speech_thread = None
        self.speech_session_id = 0  # Track current speech session to ignore stale callbacks
        self.current_session_id = 0  # Session ID for the currently running speech
        self.spoken_text = ''
        self.highlight_index1 = None
        self.highlight_index2 = None
        self.build_frame_content(kw)

    def build_frame_content(self, kw):

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=1)

        row_index = 0

        self.progress = ttk.Progressbar(self, orient=HORIZONTAL, mode="determinate")
        self.progress.grid(row=row_index, columnspan=4, sticky=(W, E))

        row_index += 1


        self.grid_rowconfigure(row_index, weight=1)
        self.title = ttk.Label(self, font=("Georgia", "80"), justify=RIGHT, text="Speed Reader", anchor=CENTER)
        self.title.grid(row=row_index, column=0, columnspan=4, sticky=(N, W, E), pady=15)
        row_index += 1


        self.spoken_words = ttk.Label(self, font=("Georgia", "20"), justify=RIGHT, anchor=E)
        self.spoken_words.grid(row=row_index, column=0, columnspan=4, sticky=(W, E))
        row_index += 1

        self.current_word_label = ttk.Label(self, font=("Georgia", "120"), anchor=CENTER)
        self.current_word_label.grid(row=row_index, column=0, columnspan=4, sticky=(W, E))
        row_index += 1

        self.next_words = ttk.Label(self, font=("Georgia", "20"), anchor=W)
        self.next_words.grid(row=row_index, column=0, columnspan=4, sticky=(W, E))

        row_index += 1

        self.speed_label = ttk.Label(self, text="Speed: ")
        self.speed_label.grid(row=row_index, column=1, pady=10)
        self.speed_entry = ttk.Entry(self)
        self.speed_entry.insert(0, "500")
        self.speed_entry.grid(row=row_index, column=2, pady=10)
        row_index += 1



        self.grid_rowconfigure(row_index, weight=1)
        self.text_area = Text(self, height=5, width=1, font=("Georgia", "40"))
        self.text_area.insert(END, '')
        self.text_area.tag_config(TAG_CURRENT_WORD, foreground="red")
        self.text_area.grid(row=row_index, column=0, columnspan=4, sticky=(N, S, E, W))
        row_index += 1

        self.speak_button = ttk.Button(self, text="Speak")
        self.speak_button.grid(row=row_index, column=1, pady=10)
        self.speak_button['state'] = NORMAL
        self.speak_button.bind("<Button-1>", self.speak)

        self.stop_button = ttk.Button(self, text="Stop")
        self.stop_button.grid(row=row_index, column=2, pady=10)
        self.stop_button['state'] = DISABLED
        self.stop_button.bind("<Button-1>", self.stop)

        self.text_area.bind("<Control-Key-a>", self.select_all_text)
        self.text_area.bind("<Control-Key-A>", self.select_all_text)

        self.master.bind("<Control-Key-b>", self.paste_and_speak)
        self.master.bind("<Control-Key-B>", self.paste_and_speak)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.cleanup_engine()
        self.master.destroy()
        self.master.quit()

    def cleanup_engine(self):
        """Properly release and cleanup the TTS engine resources."""
        self.stop_requested = True
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception as e:
                print(f"Error during engine cleanup: {e}")
            finally:
                self.engine = None
                self.is_speaking = False
        

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
        
        # Start speaking the new text
        self.speak(event)

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
            self.stop_requested = True
            if self.engine is not None:
                try:
                    self.engine.stop()
                except Exception as e:
                    print(f"Error stopping engine: {e}")
                # Dispose of engine so next speech gets a fresh one
                self.engine = None
            self.is_speaking = False
            self.speak_button['state'] = NORMAL
            self.stop_button['state'] = DISABLED

    def onStart(self, name):
        """Called when an utterance starts."""
        # Ignore callbacks from old speech sessions
        if self.current_session_id != self.speech_session_id:
            return
        self.is_speaking = True
        self.stop_requested = False
        self.speak_button['state'] = DISABLED
        self.stop_button['state'] = NORMAL
        print(f"onStart: {name}")

    def onStartWord(self, name, location, length):
        """Called when a word starts being spoken."""
        # Skip updates if stop was requested or this is an old session
        if self.stop_requested or self.current_session_id != self.speech_session_id:
            return
            
        read_trail = 100
        left_index = location - read_trail
        if left_index < 0:
            left_index = 0

        self.spoken_words['text'] = self.spoken_text[left_index:location]
        self.current_word_label['text'] = self.spoken_text[location:location + length]
        self.next_words['text'] = self.spoken_text[location + length:location + length + read_trail]
        if self.highlight_index1 is not None:
            self.text_area.tag_remove(TAG_CURRENT_WORD, self.highlight_index1, self.highlight_index2)
        self.highlight_index1 = "1.{}".format(location)
        self.highlight_index2 = "1.{}".format(location + length)
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
        # Ignore callbacks from old speech sessions
        if self.current_session_id != self.speech_session_id:
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

    def speak(self, event):
        if self.speak_button['state'].__str__() == NORMAL:
            text = self.text_area.get("1.0", END).replace('\n', ' ')
            text = re.sub(r'http\S+', ' [URL] ', text)
            self.spoken_text = text
            self.text_area.delete("1.0", END)
            self.text_area.insert(END, self.spoken_text)

            speech_speed = int(self.speed_entry.get())
            
            # Increment session ID for this new speech
            self.speech_session_id += 1
            session_id = self.speech_session_id

            self.speech_thread = threading.Thread(target=self.speak_on_thread, args=(speech_speed, self.spoken_text, session_id))
            self.speech_thread.daemon = True
            self.speech_thread.start()

    def speak_on_thread(self, speech_speed, spoken_text, session_id):
        """Run speech synthesis on a separate thread.
        
        Creates a new engine for each speech session to ensure clean state
        and proper resource management.
        
        Args:
            speech_speed: Words per minute
            spoken_text: Text to speak
            session_id: Session ID to track this speech session
        """
        # Store session ID so callbacks know which session they belong to
        self.current_session_id = session_id
        
        # Always create a fresh engine for each speech session
        # This avoids issues with pyttsx3 engine state after interruption
        try:
            engine = pyttsx3.init()
            self.engine = engine
            engine.connect('started-utterance', self.onStart)
            engine.connect('started-word', self.onStartWord)
            engine.connect('finished-utterance', self.onEnd)
            engine.connect('error', self.onError)
        except Exception as e:
            print(f"Error initializing TTS engine: {e}")
            self.speak_button['state'] = NORMAL
            self.stop_button['state'] = DISABLED
            return

        try:
            self.stop_requested = False
            engine.setProperty('rate', speech_speed)
            engine.say(spoken_text)
            
            # Use runAndWait - this blocks until speech is complete or stopped
            engine.runAndWait()
        except Exception as e:
            print(f"Error during speech: {e}")
        finally:
            # Clean up this engine instance only if it's still the current one
            if self.engine == engine:
                self.engine = None
                self.is_speaking = False


TAG_CURRENT_WORD = "current word"
