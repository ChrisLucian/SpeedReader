"""Pause/resume system media while SpeedReader speaks (Windows only)."""
import asyncio
import platform

# Windows media key support
if platform.system() == 'Windows':
    import ctypes
    VK_MEDIA_PLAY_PAUSE = 0xB3
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    
    # Try to import Windows Media Session API for detecting playback state
    try:
        from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager
        from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionPlaybackStatus
        MEDIA_SESSION_AVAILABLE = True
    except ImportError:
        # Fallback for environments where the API is not available (e.g., CI/testing)
        MEDIA_SESSION_AVAILABLE = False
        print("Windows Media Session API not available - media detection disabled.")


class MediaControlMixin:
    """Mixed into MainFrame; expects a ``media_was_paused`` attribute."""

    def pause_system_media(self):
        """Pause any currently playing system media (Windows only).
        
        Uses Windows Media Session API to check if media is actually playing
        before sending the pause command. This prevents toggling music that
        was already paused.
        """
        if platform.system() != 'Windows':
            return
            
        # Check if media is actually playing before pausing
        if not self._is_media_playing():
            # If media isn't playing, preserve existing media_was_paused flag
            # (we may have already paused it in a previous session that was interrupted)
            print("No media playing - skipping pause")
            return
            
        try:
            # Send media play/pause key press to pause
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
            ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            self.media_was_paused = True
            print("Paused system media playback")
        except Exception as e:
            print(f"Error pausing media: {e}")
            self.media_was_paused = False
    
    def _is_media_playing(self):
        """Check if system media is currently playing (Windows only).
        
        Uses Windows Media Session API to query the current playback state.
        Returns True if media is playing, False otherwise.
        """
        if platform.system() != 'Windows':
            return False
            
        if not MEDIA_SESSION_AVAILABLE:
            # If API not available, assume nothing is playing to be safe
            return False
            
        try:
            # Run async check synchronously
            return asyncio.run(self._check_media_playing_async())
        except Exception as e:
            print(f"Error checking media state: {e}")
            return False
    
    async def _check_media_playing_async(self):
        """Async helper to check media playback state."""
        try:
            # Get the media session manager
            manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
            session = manager.get_current_session()
            
            if session is None:
                return False
                
            # Get playback info
            playback_info = session.get_playback_info()
            status = playback_info.playback_status
            
            # Check if currently playing
            return status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
        except Exception as e:
            print(f"Error in async media check: {e}")
            return False
    
    def resume_system_media(self):
        """Resume system media playback if we previously paused it (Windows only).
        
        Only resumes if media_was_paused flag is set.
        """
        if platform.system() == 'Windows' and self.media_was_paused:
            try:
                # Send media play/pause key press to resume
                ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
                ctypes.windll.user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
                self.media_was_paused = False
                print("Resumed system media playback")
            except Exception as e:
                print(f"Error resuming media: {e}")
