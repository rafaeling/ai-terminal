import google.generativeai as genai
import os
import sys


from dotenv import load_dotenv

class GeminiClient:
    """Manages Gemini client."""

    def __init__(self):
        print("Ussing GeminiClient")
        if not self._configure_gemini():
            sys.exit(1) 
        
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.chat = self.model.start_chat(history=[]) # Start with empty history

    def _configure_gemini(self):
        """Loads API key and configures the Gemini library."""
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            print("Error: GOOGLE_API_KEY environment variable not set.")
            print("Please create a .env file with GOOGLE_API_KEY=YOUR_API_KEY")
            sys.exit(1) # Exit if key is missing

        try:
            genai.configure(api_key=api_key)
            print("Gemini API configured successfully.")
            return True
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            sys.exit(1)
  
    def send_request(self, request):
        print("Received request: " + request)
        response = self.model.generate_content(request)
        print("Return response: " + response.text)
        return response.text
                
