# -*- coding: utf-8 -*-

import datetime
import random
import re
import os
import google.generativeai as genai
from gtts import gTTS
import tempfile
import pygame

class GoogleAssistant:
    def __init__(self):
        self.name = "Google Assistant"
        self.user_name = "User"
        self.reminders = []
        self.gemini_initialized = False
        self.model = None
        self.chat_history = []
        
    def initialize_gemini(self, api_key=None):
        """Initialize the Gemini API with your API key."""
        try:
            # If no API key is provided, check for GOOGLE_API_KEY in environment variables
            if not api_key:
                api_key = os.getenv("")
            
            if not api_key:
                print("Gemini API key not found. Using built-in responses.")
                return False
                
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Use Gemini Pro model
            self.model = genai.GenerativeModel('gemini-pro')
            self.gemini_initialized = True
            
            # Initialize the chat with multilingual capability
            self.chat = self.model.start_chat(
                history=[
                    {
                        "role": "user",
                        "parts": ["You are a helpful virtual assistant called Google Assistant. You can understand and respond in both English and Marathi. When someone asks for a response in Marathi, you should respond in Marathi. Keep responses helpful and concise."]
                    },
                    {
                        "role": "model",
                        "parts": ["मी Google Assistant आहे, तुम्हाला कशी मदत करू शकतो? I am Google Assistant, how can I help you?"]
                    }
                ]
            )
            
            print("Gemini API initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing Gemini API: {e}")
            return False
    
    def generate_response_with_gemini(self, user_input):
        """Generate a response using the Gemini API."""
        try:
            # Check if the user wants response in Marathi
            is_marathi_requested = "in marathi" in user_input.lower()
            
            # If Marathi is requested, modify the query to ask for Marathi response
            if is_marathi_requested:
                user_input = f"Please respond in Marathi to: {user_input.replace('in marathi', '').strip()}"
            
            response = self.chat.send_message(user_input)
            return response.text
            
        except Exception as e:
            print(f"Error generating response with Gemini: {e}")
            return self.generate_fallback_response(user_input)
    
    def generate_fallback_response(self, user_input):
        """Generate a fallback response when Gemini API is not available."""
        user_input = user_input.lower().strip()
        
        # Programming language queries
        if "what is python" in user_input:
            return "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and released in 1991. Python supports multiple programming paradigms, including procedural, object-oriented, and functional programming. It's widely used in web development, data science, artificial intelligence, automation, and more."
        
        # Check for Marathi joke requests
        elif re.search(r'\b(tu mala joke sang|मला एक जोक सांग|विनोद सांग)\b', user_input):
            marathi_jokes = [
                "शिक्षक: तुम्ही उशिरा का आलात? विद्यार्थी: सर, तुम्हीच तर शिकवलं की Time and Tide wait for none.",
                "डॉक्टर: तुम्हाला काय त्रास आहे? पेशंट: डोकं दुखतंय. डॉक्टर: किती दिवसांपासून? पेशंट: शनिवारपासून. डॉक्टर: मग आज सोमवार आहे, इतके दिवस का थांबलात? पेशंट: माझं डोकं, मला ठरवायचं किती दिवस दुखायचं.",
                "एक मराठी माणूस हॉटेलमध्ये: 'वेटर, मटण आणि भात आणा'. वेटर: 'सर, मटण संपलं'. मराठी माणूस: 'मग काय ते आणा आणि भात आणा.'",
                "मुलगा: बाबा, माझं लग्न ठरलं. बाबा: कुठल्या जातीची आहे? मुलगा: प्रजाती तर नाही, पण ती सुद्धा मानव आहे."
            ]
            return random.choice(marathi_jokes)
        
        # Check for greetings
        elif re.search(r'\b(hello|hi|hey|greetings|नमस्कार|नमस्ते)\b', user_input):
            return f"Hello {self.user_name}! How can I help you today?"
        
        # Check for name queries
        elif "your name" in user_input or "तुझं नाव" in user_input:
            return f"My name is {self.name}. I'm a virtual assistant created to help you."
        
        # Check for time queries
        elif re.search(r'\b(time|what time)\b', user_input):
            current_time = datetime.datetime.now().strftime("%H:%M")
            return f"The current time is {current_time}."
        
        # Check for date queries
        elif re.search(r'\b(date|day|today)\b', user_input):
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}."
        
        # Check for search queries
        elif re.search(r'\b(search|look up|find)\b', user_input):
            search_query = user_input.split("search", 1)[-1].strip()
            if search_query:
                return f"I would search for '{search_query}' for you."
            else:
                return "What would you like me to search for?"
        
        # Check for weather queries
        elif re.search(r'\b(weather|temperature|forecast)\b', user_input):
            return "I would normally check the weather for you, but I don't have access to weather data in this implementation."
        
        # Check for reminders
        elif re.search(r'\b(remind|reminder)\b', user_input):
            if "set" in user_input or "add" in user_input:
                reminder = re.search(r'remind me to (.*)', user_input)
                if reminder:
                    task = reminder.group(1)
                    self.reminders.append(task)
                    return f"I'll remind you to {task}."
                else:
                    return "What would you like me to remind you about?"
            elif "list" in user_input or "show" in user_input:
                if self.reminders:
                    reminder_list = "\n".join([f"- {r}" for r in self.reminders])
                    return f"Here are your reminders:\n{reminder_list}"
                else:
                    return "You don't have any reminders set."
        
        # Check for jokes
        elif re.search(r'\b(joke|funny|make me laugh)\b', user_input):
            jokes = [
                "Why don't scientists trust atoms? Because they make up everything!",
                "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them!",
                "Why do programmers prefer dark mode? Because light attracts bugs!",
                "What do you call a fake noodle? An impasta!",
                "Why couldn't the bicycle stand up by itself? It was two tired!"
            ]
            return random.choice(jokes)
        
        # Check for exit commands
        elif re.search(r'\b(exit|bye|goodbye|quit)\b', user_input):
            return "Goodbye! Have a great day!"
        
        # Default response
        else:
            return "I'm not sure how to respond to that. Is there something specific you'd like help with?"
            
    def speak(self, text):
        """Convert text to speech and play it."""
        # Always use visual indicator for Replit
        print("🔊 [Text-to-Speech]: " + text)
        
        # Try to generate actual speech if possible
        try:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file_path = temp_file.name
            temp_file.close()
            
            # Generate the speech file
            tts = gTTS(text=text, lang='en')
            tts.save(temp_file_path)
            
            # Initialize pygame mixer
            pygame.mixer.init()
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Wait for the audio to finish playing
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            # Clean up
            pygame.mixer.quit()
            os.unlink(temp_file_path)
                
        except Exception as e:
            # Just show an error message but continue execution
            print(f"Note: Audio playback failed ({str(e)}). Visual text-to-speech will be used instead.")
    
    def respond(self, user_input):
        """Generate a response to the user input."""
        # Handle reminders separately since they modify internal state
        if re.search(r'\b(remind|reminder)\b', user_input.lower().strip()):
            user_input_lower = user_input.lower().strip()
            if "set" in user_input_lower or "add" in user_input_lower:
                reminder = re.search(r'remind me to (.*)', user_input_lower)
                if reminder:
                    task = reminder.group(1)
                    self.reminders.append(task)
                    return f"I'll remind you to {task}."
            elif "list" in user_input_lower or "show" in user_input_lower:
                if self.reminders:
                    reminder_list = "\n".join([f"- {r}" for r in self.reminders])
                    return f"Here are your reminders:\n{reminder_list}"
                else:
                    return "You don't have any reminders set."
        
        # Use Gemini API if initialized, otherwise use fallback responses
        if self.gemini_initialized and self.model:
            return self.generate_response_with_gemini(user_input)
        else:
            return self.generate_fallback_response(user_input)

def main():
    assistant = GoogleAssistant()
    
    # Try to initialize Gemini API
    print("Initializing Google Assistant with Gemini API...")
    api_key = input("Enter your Google AI API key (press Enter to skip): ").strip()
    
    if api_key:
        assistant.initialize_gemini(api_key)
    else:
        print("No API key provided. Using built-in responses instead of Gemini API.")
        print("You can get a Gemini API key from: https://aistudio.google.com/app/apikey")
    
    # Ask if the user wants to enable text-to-speech
    tts_enabled = input("Enable text-to-speech? (y/n, default: n): ").lower().strip() == 'y'
    if tts_enabled:
        print("Text-to-speech enabled.")
    else:
        print("Text-to-speech disabled.")
    
    print(f"{assistant.name}: Hello! How can I help you today?")
    
    try:
        while True:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit", "bye", "goodbye"]:
                print(f"{assistant.name}: Goodbye! Have a great day!")
                break
            
            # Check for text-to-speech toggle command
            if user_input.lower() in ["toggle tts", "toggle speech"]:
                tts_enabled = not tts_enabled
                print(f"Text-to-speech {'enabled' if tts_enabled else 'disabled'}.")
                continue
                
            response = assistant.respond(user_input)
            print(f"{assistant.name}: {response}")
            
            # Speak the response only if enabled
            if tts_enabled:
                assistant.speak(response)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected.")
        print(f"{assistant.name}: Goodbye! Have a great day!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Thank you for using Google Assistant!")

if __name__ == "__main__":
    main()
