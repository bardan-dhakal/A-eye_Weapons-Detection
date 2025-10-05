# twilio_api.py
# Twilio Voice API integration for security alert phone calls

import os
import requests
from twilio.rest import Client
from config import *


class TwilioVoiceCall:
    """
    Handles phone calls using Twilio Voice API.
    """
    
    def __init__(self):
        """
        Initialize the Twilio client.
        """
        self.account_sid = TWILIO_ACCOUNT_SID
        self.auth_token = TWILIO_AUTH_TOKEN
        self.twilio_phone = TWILIO_PHONE_NUMBER
        self.target_phone = TARGET_PHONE_NUMBER
        self.enabled = TWILIO_ENABLED
        
        if self.enabled and (self.account_sid == 'YOUR_TWILIO_ACCOUNT_SID' or 
                           self.auth_token == 'YOUR_TWILIO_AUTH_TOKEN'):
            print("⚠️  Twilio credentials not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env file to enable phone calls.")
            self.enabled = False
        
        # Initialize the Twilio client
        if self.enabled:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                print("✅ Twilio client initialized successfully!")
            except Exception as e:
                print(f"❌ Failed to initialize Twilio client: {e}")
                self.enabled = False
    
    def is_enabled(self):
        """
        Check if Twilio API is properly configured and enabled.
        """
        return self.enabled and self.account_sid != 'YOUR_TWILIO_ACCOUNT_SID'
    
    def upload_audio_to_twilio(self, audio_file_path):
        """
        Upload audio file to a web-accessible URL for Twilio to play.
        For now, we'll use a simple approach, but in production you'd want to:
        1. Host the file on your web server, or
        2. Use Twilio's Media API, or
        3. Use a cloud storage service like AWS S3
        
        Args:
            audio_file_path: Path to the MP3 audio file
            
        Returns:
            Web-accessible URL for the audio file
        """
        if not os.path.exists(audio_file_path):
            print(f"❌ Audio file not found: {audio_file_path}")
            return None
        
        # For now, we'll create a simple web server approach
        # In production, you'd upload this to a web server or cloud storage
        print(f"⚠️  Audio file available locally: {os.path.basename(audio_file_path)}")
        print(f"   Note: For production, upload this to a web-accessible URL")
        
        # Return None for now - we'll use text-to-speech instead
        return None
    
    def create_twiml_response(self, audio_url=None, security_message=None):
        """
        Create TwiML response for the call.
        
        Args:
            audio_url: Optional URL to audio file to play
            security_message: Custom security message to speak
            
        Returns:
            TwiML XML string
        """
        twiml = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Security Alert. This is an automated security system calling to report a weapon detection event.</Say>
    <Pause length="2"/>'''
        
        if security_message:
            # Escape XML special characters
            security_message = security_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
            twiml += f'''
    <Say voice="alice">Security Analysis: {security_message}</Say>
    <Pause length="2"/>'''
        elif audio_url:
            twiml += f'''
    <Say voice="alice">Playing detailed security analysis.</Say>
    <Play>{audio_url}</Play>
    <Pause length="1"/>'''
        else:
            twiml += '''
    <Say voice="alice">Weapon detection event detected. Please review security footage immediately.</Say>
    <Pause length="2"/>'''
        
        twiml += '''
    <Say voice="alice">Please review the security footage immediately. This call will now end.</Say>
    <Pause length="1"/>
    <Say voice="alice">Goodbye.</Say>
</Response>'''
        
        return twiml
    
    def make_security_call(self, audio_file_path, event_info):
        """
        Make a phone call and play the security announcement.
        
        Args:
            audio_file_path: Path to the MP3 audio file with security announcement
            event_info: Event metadata for call context
            
        Returns:
            Call SID if successful, None if failed
        """
        if not self.is_enabled():
            print("⚠️  Twilio not enabled - cannot make phone call")
            return None
        
        try:
            print(f"📞 Making security alert call to {self.target_phone}...")
            
            # Try to get a web-accessible URL for the audio
            audio_url = self.upload_audio_to_twilio(audio_file_path)
            
            # For now, let's use a custom security message instead of audio file
            # Extract key information from event_info for the call
            weapons = event_info.get('weapons', [])
            duration = event_info.get('duration', 0)
            screenshot_count = event_info.get('screenshot_count', 0)
            
            security_message = f"""
            Detected weapons: {', '.join(weapons) if weapons else 'Unknown weapons'}.
            Event duration: {duration:.1f} seconds.
            Number of detection frames: {screenshot_count}.
            Please review security footage immediately.
            """
            
            # Create TwiML response with custom message
            twiml_response = self.create_twiml_response(audio_url=None, security_message=security_message)
            
            # Make the call
            call = self.client.calls.create(
                twiml=twiml_response,
                to=self.target_phone,
                from_=self.twilio_phone
            )
            
            print(f"✅ Security call initiated successfully!")
            print(f"   Call SID: {call.sid}")
            print(f"   To: {self.target_phone}")
            print(f"   From: {self.twilio_phone}")
            print(f"   Status: {call.status}")
            print(f"   Audio: Using custom security message (ElevenLabs audio saved locally)")
            
            return call.sid
            
        except Exception as e:
            print(f"❌ Error making security call: {e}")
            return None
    
    def make_call_with_elevenlabs_audio(self, audio_file_path, event_info):
        """
        Alternative method that tries to play the actual ElevenLabs audio.
        This requires the audio file to be hosted on a web-accessible URL.
        
        Args:
            audio_file_path: Path to the ElevenLabs MP3 audio file
            event_info: Event metadata
            
        Returns:
            Call SID if successful, None if failed
        """
        if not self.is_enabled():
            print("⚠️  Twilio not enabled - cannot make phone call")
            return None
        
        try:
            print(f"📞 Making call with ElevenLabs audio to {self.target_phone}...")
            
            # For this to work, you need to:
            # 1. Host the audio file on a web server
            # 2. Or upload it to cloud storage (AWS S3, Google Cloud, etc.)
            # 3. Or use Twilio's Media API
            
            # Example: If you had the audio hosted at a URL:
            # audio_url = "https://your-server.com/audio/security_announcement.mp3"
            
            print("⚠️  To play ElevenLabs audio in calls, you need to:")
            print("   1. Host the audio file on a web server")
            print("   2. Or use cloud storage (AWS S3, Google Cloud, etc.)")
            print("   3. Or implement Twilio's Media API")
            print("   For now, using text-to-speech with security details...")
            
            # Fall back to the regular method
            return self.make_security_call(audio_file_path, event_info)
            
        except Exception as e:
            print(f"❌ Error making call with ElevenLabs audio: {e}")
            return None
    
    def send_security_sms(self, event_info, audio_file_path=None):
        """
        Send SMS alert as backup if call fails.
        
        Args:
            event_info: Event metadata
            audio_file_path: Optional path to audio file
            
        Returns:
            Message SID if successful, None if failed
        """
        if not self.is_enabled():
            print("⚠️  Twilio not enabled - cannot send SMS")
            return None
        
        try:
            weapons = event_info.get('weapons', [])
            duration = event_info.get('duration', 0)
            screenshot_count = event_info.get('screenshot_count', 0)
            
            message_body = f"""
🚨 SECURITY ALERT 🚨

Weapon detection event reported:
• Weapons: {', '.join(weapons) if weapons else 'Unknown'}
• Duration: {duration:.1f} seconds
• Detection frames: {screenshot_count}

Please review security footage immediately.

Timestamp: {event_info.get('timestamp', 'Unknown')}
            """.strip()
            
            print(f"📱 Sending security SMS to {self.target_phone}...")
            
            message = self.client.messages.create(
                body=message_body,
                from_=self.twilio_phone,
                to=self.target_phone
            )
            
            print(f"✅ Security SMS sent successfully!")
            print(f"   Message SID: {message.sid}")
            print(f"   To: {self.target_phone}")
            print(f"   Status: {message.status}")
            
            return message.sid
            
        except Exception as e:
            print(f"❌ Error sending security SMS: {e}")
            return None
    
    def get_call_status(self, call_sid):
        """
        Check the status of a call.
        
        Args:
            call_sid: The SID of the call to check
            
        Returns:
            Call status or None if error
        """
        if not self.is_enabled():
            return None
        
        try:
            call = self.client.calls(call_sid).fetch()
            return call.status
        except Exception as e:
            print(f"❌ Error checking call status: {e}")
            return None
    
    def test_twilio_setup(self):
        """
        Test Twilio configuration by making a test call.
        """
        if not self.is_enabled():
            print("⚠️  Twilio not enabled - cannot test setup")
            return False
        
        try:
            print("🧪 Testing Twilio setup with a test call...")
            
            twiml_response = '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">This is a test call from your security system. Twilio integration is working correctly.</Say>
    <Pause length="1"/>
    <Say voice="alice">Goodbye.</Say>
</Response>'''
            
            call = self.client.calls.create(
                twiml=twiml_response,
                to=self.target_phone,
                from_=self.twilio_phone
            )
            
            print(f"✅ Test call initiated successfully!")
            print(f"   Call SID: {call.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Test call failed: {e}")
            return False
    
    def make_simple_call(self, message="This is a test call from your security system."):
        """
        Make a simple call with just a text message.
        
        Args:
            message: Text message to speak during the call
            
        Returns:
            Call SID if successful, None if failed
        """
        if not self.is_enabled():
            print("⚠️  Twilio not enabled - cannot make call")
            return None
        
        try:
            print(f"📞 Making simple call to {self.target_phone}...")
            
            # Escape XML special characters in the message
            message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
            
            twiml_response = f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">{message}</Say>
    <Pause length="1"/>
    <Say voice="alice">Goodbye.</Say>
</Response>'''
            
            call = self.client.calls.create(
                twiml=twiml_response,
                to=self.target_phone,
                from_=self.twilio_phone
            )
            
            print(f"✅ Simple call initiated successfully!")
            print(f"   Call SID: {call.sid}")
            return call.sid
            
        except Exception as e:
            print(f"❌ Error making simple call: {e}")
            return None