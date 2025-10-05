# gemini_api.py
# Gemini Vision API integration for event analysis using Google GenAI library

import os
from google import genai
from google.genai import types
from config import *


class GeminiVisionAPI:
    """
    Handles communication with Google's Gemini Vision API for image analysis.
    """
    
    def __init__(self):
        """
        Initialize the Gemini Vision API client.
        """
        self.model_name = GEMINI_MODEL
        self.enabled = GEMINI_ENABLED
        
        if self.enabled and GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY':
            print("⚠️  Gemini API key not configured. Set GEMINI_API_KEY in .env file to enable AI analysis.")
            self.enabled = False
        
        # Initialize the client (gets API key from GEMINI_API_KEY environment variable)
        if self.enabled:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
                print("✅ Gemini API client initialized successfully!")
            except Exception as e:
                print(f"❌ Failed to initialize Gemini client: {e}")
                self.enabled = False
    
    def is_enabled(self):
        """
        Check if Gemini API is properly configured and enabled.
        """
        return self.enabled
    
    def analyze_event(self, image_paths, event_info):
        """
        Send event screenshots to Gemini Vision API for analysis.
        """
        if not self.is_enabled():
            return None
        
        if not image_paths:
            print("⚠️  No images provided for Gemini analysis")
            return None
        
        try:
            print(f"🤖 Sending {len(image_paths)} images to Gemini for analysis...")
            
            # Prepare content with images and text
            parts = []
            
            # Add images
            for image_path in image_paths:
                if not os.path.exists(image_path):
                    print(f"⚠️  Image not found: {image_path}")
                    continue
                
                # Read image as bytes
                with open(image_path, 'rb') as f:
                    image_bytes = f.read()
                
                # Add image part
                parts.append(types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg"
                ))
            
            if not parts:
                print("❌ No valid images could be processed")
                return None
            
            # Add analysis prompt as text
            analysis_prompt = self._create_analysis_prompt(event_info)
            parts.append({"text": analysis_prompt})
            
            # Generate content using the new API
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=parts
            )
            
            if response and response.text:
                print("✅ Gemini analysis completed!")
                return response.text
            else:
                print("❌ No analysis result in Gemini response")
                return None
                
        except Exception as e:
            print(f"❌ Error sending to Gemini: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_analysis_prompt(self, event_info):
        """
        Create the analysis prompt for Gemini based on event information.
        """
        weapons = event_info.get('weapons', [])
        duration = event_info.get('duration', 0)
        screenshot_count = event_info.get('screenshot_count', 0)
        
        prompt = f"""
You are providing a brief tactical audio briefing for first responders responding to an active threat.

DETECTED EVENT:
- Weapons: {', '.join(weapons) if weapons else 'Unknown'}
- Duration: {duration:.1f} seconds
- Images: {screenshot_count}

Provide a concise verbal briefing in 3-4 short paragraphs that flows naturally when read aloud. Use this structure:

Paragraph 1 - THREAT LEVEL & SUSPECT:
Start with threat level (critical, high, moderate, or low), then briefly describe the suspect's appearance, clothing, and current actions.

Paragraph 2 - WEAPON & LOCATION:
Describe the weapon type and how it's being held, then the location type and environment.

Paragraph 3 - SITUATION & RESPONSE:
Describe what's happening, any visible victims or bystanders, and key tactical considerations for responding officers.

CRITICAL RULES:
- Write in short, clear sentences that flow when spoken
- NO bullet points, NO headers, NO special formatting
- Maximum 150 words total
- Use natural, conversational language
- Focus only on what officers need to hear immediately
- Omit anything you cannot clearly see in the images

Write as if you're speaking directly to officers en route to the scene.
"""
        return prompt