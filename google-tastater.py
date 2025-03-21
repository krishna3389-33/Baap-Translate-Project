# -*- coding: utf-8 -*-
import google.generativeai as genai
from gtts import gTTS
import tempfile
import pygame
import speech_recognition as sr
import os

class GoogleAssistant:
    def __init__(self):
        self.name = "Google Assistant"
        self.gemini_initialized = False
        self.model = None
        self.chat = None
        self.recognizer = sr.Recognizer()
        
    def initialize_gemini(self):
        """Initialize the Gemini API."""
        try:
            # Configure the Gemini API with default key
            api_key = "AIzaSyDNRtw8I2AmlDK_4x8AzV4H8-omPlNTou4"
            genai.configure(api_key=api_key)
            
            # Set up the model configuration
            generation_config = {
                "temperature": 0.9,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048,
            }
            
            # Initialize the model
            self.model = genai.get_model('gemini-pro')
            self.model.generate_content("Hello")  # Warm up the model
            self.gemini_initialized = True
            
            # Initialize the chat
            self.chat = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": ["You are a helpful virtual assistant that can understand and respond in both English and Marathi. Guidelines: 1. Always provide detailed responses 2. For Marathi queries, respond in Marathi 3. For technical terms, provide both Marathi and English explanations 4. Keep responses natural and conversational 5. If the input is in Marathi, always respond in Marathi"]
                    }
                ]
            )
            
            print("Gemini API initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing Gemini API: {e}")
            return False
    
    def generate_response(self, user_input):
        """Generate a response using the Gemini API."""
        try:
            # Ensure Gemini is initialized
            if not self.gemini_initialized or not self.chat:
                self.initialize_gemini()
            
            # Detect if input is in Marathi
            is_marathi_input = any('\u0900' <= char <= '\u097F' for char in user_input) or any(word in user_input.lower() for word in ['व्हॉट', 'इज', 'पायथॉन', 'हो', 'आहे', 'काय'])
            
            # Create the prompt
            if is_marathi_input or "मराठी" in user_input:
                prompt = f"User: {user_input}\nAssistant: Please provide a detailed response in Marathi. Use proper grammar and natural language. For technical terms, include both Marathi and English explanations."
            else:
                prompt = f"User: {user_input}\nAssistant: Please provide a clear and detailed response. Include examples for technical questions."
            
            # Generate response
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return "माफ करा, एक त्रुटी आली. कृपया पुन्हा प्रयत्न करा."
    
    def speak(self, text):
        """Convert text to speech."""
        print("🔊 [Text-to-Speech]: " + text)
        
        try:
            # Create temporary file
            text_hash = hash(text)
            temp_file_path = os.path.join(tempfile.gettempdir(), f"tts_{text_hash}.mp3")
            
            # Generate speech
            if not os.path.exists(temp_file_path):
                is_marathi = any('\u0900' <= char <= '\u097F' for char in text)
                tts = gTTS(text=text, lang='mr' if is_marathi else 'en', slow=False)
                tts.save(temp_file_path)
            
            # Play audio
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.quit()
                
        except Exception as e:
            print(f"Audio playback failed: {str(e)}")

    def listen_for_command(self):
        """Listen for voice input."""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.energy_threshold = 4000
                
                try:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    print("Processing...")
                    text = self.recognizer.recognize_google(audio, language='mr-IN')
                    print(f"You said: {text}")
                    return text
                    
                except sr.WaitTimeoutError:
                    print("No speech detected.")
                    return None
                
        except Exception as e:
            print(f"Error: {e}")
            return None

def main():
    assistant = GoogleAssistant()
    
    # Initialize Gemini API
    print("Initializing Google Assistant...")
    assistant.initialize_gemini()
    
    # Enable text-to-speech
    tts_enabled = input("Enable text-to-speech? (y/n): ").lower().strip() == 'y'
    print("Text-to-speech enabled." if tts_enabled else "Text-to-speech disabled.")
    
    # Enable voice input
    voice_input_enabled = input("Enable voice input? (y/n): ").lower().strip() == 'y'
    print("Voice input enabled. Say 'stop listening' to disable." if voice_input_enabled else "Voice input disabled.")
    
    print(f"{assistant.name}: Hello! How can I help you today?")
    
    try:
        while True:
            if voice_input_enabled:
                user_input = assistant.listen_for_command()
                if user_input is None:
                    continue
                if user_input.lower() == "stop listening":
                    voice_input_enabled = False
                    print("Voice input disabled. Type 'enable voice' to enable it again.")
                    continue
            else:
                user_input = input("You: ")
                if user_input.lower() == "enable voice":
                    voice_input_enabled = True
                    print("Voice input enabled. Say 'stop listening' to disable it.")
                    continue
            
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print(f"{assistant.name}: Goodbye! Have a great day!")
                if tts_enabled:
                    assistant.speak("Thank you for using me! Have a great day!")
                break
                
            response = assistant.generate_response(user_input)
            print(f"{assistant.name}: {response}")
            
            if tts_enabled:
                assistant.speak(response)
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
        if tts_enabled:
            assistant.speak("Thank you for using me! Have a great day!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
