# elevenlabs_api.py
# ElevenLabs Text-to-Speech API integration for voice announcements

import os
from datetime import datetime
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play
from config import *


class ElevenLabsTTS:
    """
    Handles text-to-speech conversion using ElevenLabs official Python SDK.
    """
    
    def __init__(self):
        """
        Initialize the ElevenLabs TTS client.
        """
        self.api_key = ELEVENLABS_API_KEY
        self.voice_id = ELEVENLABS_VOICE_ID
        self.enabled = ELEVENLABS_ENABLED
        
        if self.enabled and self.api_key == 'YOUR_ELEVENLABS_API_KEY':
            print("⚠️  ElevenLabs API key not configured. Set ELEVENLABS_API_KEY in .env file to enable voice announcements.")
            self.enabled = False
        
        # Initialize the ElevenLabs client
        if self.enabled:
            try:
                self.client = ElevenLabs(api_key=self.api_key)
                print("✅ ElevenLabs client initialized successfully!")
            except Exception as e:
                print(f"❌ Failed to initialize ElevenLabs client: {e}")
                self.enabled = False
    
    def is_enabled(self):
        """
        Check if ElevenLabs API is properly configured and enabled.
        """
        return self.enabled and self.api_key != 'YOUR_ELEVENLABS_API_KEY'
    
    def create_security_announcement(self, description, event_info):
        """
        Create a security announcement from the AI description.
        
        Args:
            description: AI-generated description from Gemini
            event_info: Dictionary containing event metadata
            
        Returns:
            Formatted announcement text
        """
        weapons = event_info.get('weapons', [])
        duration = event_info.get('duration', 0)
        screenshot_count = event_info.get('screenshot_count', 0)
        
        # Create a concise, clear announcement
        announcement = f"""
        Security Alert. Weapon detection event reported.
        
        Detected weapons: {', '.join(weapons) if weapons else 'Unknown weapons'}.
        
        Event duration: {duration:.1f} seconds.
        Number of detection frames: {screenshot_count}.
        
        AI Analysis: {description[:200]}...
        
        Please review the security footage and take appropriate action.
        """
        
        return announcement.strip()
    
    def text_to_speech(self, text, event_id=None, play_audio=False):
        """
        Convert text to speech using ElevenLabs SDK.
        
        Args:
            text: Text to convert to speech
            event_id: Optional event ID for filename
            play_audio: Whether to play the audio immediately
            
        Returns:
            Path to the generated audio file or None if failed
        """
        if not self.is_enabled():
            print("⚠️  ElevenLabs TTS disabled - skipping voice generation")
            return None
        
        try:
            print(f"🔊 Converting text to speech using ElevenLabs...")
            
            # Convert text to speech using the SDK
            audio = self.client.text_to_speech.convert(
                text=text,
                voice_id=self.voice_id,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if event_id:
                filename = f"security_announcement_{event_id}_{timestamp}.mp3"
            else:
                filename = f"security_announcement_{timestamp}.mp3"
            
            # Save audio file - FIXED: Properly handle the audio stream
            audio_path = os.path.join(SCREENSHOT_FOLDER, filename)
            
            # The audio is an iterator, so we need to collect all chunks
            with open(audio_path, 'wb') as f:
                for chunk in audio:
                    f.write(chunk)
            
            print(f"✅ Audio file saved: {filename}")
            
            # Optionally play the audio immediately
            if play_audio:
                print("🔊 Playing audio announcement...")
                # Re-generate audio for playback since we consumed the iterator
                audio_for_play = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id="eleven_multilingual_v2",
                    output_format="mp3_44100_128"
                )
                play(audio_for_play)
            
            return audio_path
            
        except Exception as e:
            print(f"❌ Error converting text to speech: {e}")
            return None
    
    def generate_security_alert(self, description, event_info, event_id=None, play_audio=False):
        """
        Generate a complete security alert with voice announcement.
        
        Args:
            description: AI-generated description from Gemini
            event_info: Event metadata
            event_id: Optional event ID
            play_audio: Whether to play the audio immediately
            
        Returns:
            Path to audio file or None if failed
        """
        if not description:
            print("⚠️  No description provided for voice announcement")
            return None
        
        # Create security announcement
        announcement = self.create_security_announcement(description, event_info)
        
        # Convert to speech
        audio_path = self.text_to_speech(announcement, event_id, play_audio)
        
        return audio_path
    
    def list_available_voices(self):
        """
        List all available voices for the current API key.
        Useful for debugging and voice selection.
        """
        if not self.is_enabled():
            print("⚠️  ElevenLabs not enabled - cannot list voices")
            return []
        
        try:
            voices = self.client.voices.get_all()
            print("🎤 Available voices:")
            for voice in voices.voices:
                print(f"   - {voice.name} (ID: {voice.voice_id})")
            return voices.voices
        except Exception as e:
            print(f"❌ Error listing voices: {e}")
            return []
    
    def test_audio_generation(self, test_text="Hello, this is a test of the ElevenLabs text to speech system."):
        """
        Test method to verify audio generation is working correctly.
        """
        if not self.is_enabled():
            print("⚠️  ElevenLabs not enabled - cannot test audio generation")
            return None
        
        print(f"🧪 Testing audio generation with text: '{test_text}'")
        return self.text_to_speech(test_text, "test", play_audio=False)