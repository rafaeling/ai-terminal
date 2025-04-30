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
        role = "**Role:** You are an expert command-line assistant. Your goal is to provide accurate and concise terminal commands according to the user's request and specified format."
        self.chat = self.model.start_chat(history=[role]) # Start with empty history

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
    
    def decorate_request(self, request):
        command = (
            "**Task:** I need a terminal commands avoiding recipes to achieve the following:\n" +
            request + "\n" +
            "**Environment:**\n" +
            "*   Operating System: Linux (Ubuntu 22.04)\n" +
            "*   Shell: bash\n" +
            "\n" +
            "**Output Format Requirements:**\n" +
            "Please provide the response *strictly* in the following Markdown format. Do not include any introductions, explanations, apologies, greetings, or sign-offs outside of this defined structure.\n" +
            "\n" +
            "--- START RESPONSE ---\n" +

            "**Command:**\n" +
            "```bash\n" +
            "command \n" +
            "```\n"
        )
        return command
    
    def decorate_error_request(self, command, error):
        command = (
            "**Task:** I received an error when running a terminal command and need you to return a new *comman* suggestion fixing the command:\n" +
            command + "\n" +
            "**Error:**\n" +
            error + "\n"
            "**Output Format Requirements:**\n" +
            "Please provide the response *strictly* in the following Markdown format. Do not include any introductions, explanations, apologies, greetings, or sign-offs outside of this defined structure.\n" +
            "\n" +
            "--- START RESPONSE ---\n" +

            "**Command:**\n" +
            "```bash\n" +
            "command \n" +
            "```\n"
        )
        return command

    def send_request(self, request):
        print("Received request: " + self.decorate_request(request))
        response = self.model.generate_content(self.decorate_request(request))
        print("Return response: " + response.text)
        return response.text

    def send_error_request(self, command, error):
        print("Received error request: " + self.decorate_error_request(command, error))
        response = self.model.generate_content(self.decorate_error_request(command, error))
        print("Return error response: " + response.text)
        return response.text                
