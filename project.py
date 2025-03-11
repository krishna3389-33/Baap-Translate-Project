from tkinter import *
from tkinter import ttk, messagebox
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import speech_recognition as sr
import threading

delay_time = 0  # Delay before translating after user stops typing
translate_timer = None

DetectorFactory.seed = 0  # Ensures consistent language detection

def recognize_speech():
    recognizer = sr.Recognizer()
    try:
        mic = sr.Microphone()
    except OSError as e:
        messagebox.showerror("Microphone Error", "No microphone detected or it's not accessible.")
        return

    try:
        with mic as source:
            messagebox.showinfo("Voice Input", "Speak now...")
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Improved noise filtering
            audio = recognizer.listen(source, phrase_time_limit=10)  # Slightly longer time limit
        
        text = recognizer.recognize_google(audio).strip()
        if text:
            input_text.insert(END, text + " ")  
        else:
            messagebox.showwarning("Speech Error", "No speech detected. Please try again with a clear voice.")
    
    except sr.UnknownValueError:
        messagebox.showwarning("Speech Error", "Could not understand the audio. Try speaking more clearly, reduce background noise, and ensure a steady pace.")
    except sr.RequestError:
        messagebox.showerror("Speech Error", "Could not connect to Google services. Check your internet connection.")
    except OSError as e:
        messagebox.showerror("Microphone Error", f"Microphone issue: {e}")
    except AttributeError as e:
        messagebox.showerror("Speech Error", "Microphone access failed. Please check your input device settings.")
    except Exception as e:
        messagebox.showerror("Speech Error", f"An unexpected error occurred: {e}")

def detect_language(text):
    try:
        return detect(text)  # Automatically detect language
    except:
        return "auto"  # Default to "auto-detect" if detection fails

def delayed_translation():
    global translate_timer
    if translate_timer:
        translate_timer.cancel()
    translate_timer = threading.Timer(delay_time, translate_text_live)
    translate_timer.start()

def translate_text_live():
    text = input_text.get("1.0", END).strip()
    if not text:
        output_text.config(state=NORMAL)
        output_text.delete("1.0", END)
        output_text.config(state=DISABLED)
        return
    
    src_code = lang_dict.get(src_lang.get(), "auto")  # Auto-detect if selected
    dest_code = lang_dict.get(dest_lang.get(), "en")  # Default to English if not selected
    
    try:
        translated_text = GoogleTranslator(source=src_code, target=dest_code).translate(text)
        output_text.config(state=NORMAL)
        output_text.delete("1.0", END)
        output_text.insert(END, translated_text)
        output_text.config(state=DISABLED)
    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

def on_text_change(event=None):
    delayed_translation()

root = Tk()
root.title("Google Translate Clone")
root.geometry("950x550")
root.configure(bg="#E8F0FE")

# Language dictionary
languages = GoogleTranslator().get_supported_languages()
lang_dict = {"Auto-detect": "auto"}  # Add auto-detect option
lang_dict.update({lang.capitalize(): lang for lang in languages})  # Load all languages

# UI Elements
Label(root, text="Google Translate Clone", font=("Arial", 18, "bold"), bg="#E8F0FE").pack(pady=10)

frame = Frame(root, bg="#E8F0FE")
frame.pack(pady=10)

Label(frame, text="Input Text:", font=("Arial", 12), bg="#E8F0FE").grid(row=0, column=0, sticky=W)
input_text = Text(frame, height=10, width=50, font=("Arial", 12))
input_text.grid(row=1, column=0, padx=10, pady=10)
input_text.bind("<KeyRelease>", on_text_change)  # Trigger delayed translation

Label(frame, text="Translated Text:", font=("Arial", 12), bg="#E8F0FE").grid(row=0, column=1, sticky=W)
output_text = Text(frame, height=10, width=50, font=("Arial", 12), state='disabled')
output_text.grid(row=1, column=1, padx=10, pady=10)

# Input Language Selection (Now includes "Auto-detect")
src_lang = StringVar()
src_lang.set("Auto-detect")  # Default to auto-detect
Label(frame, text="From:", font=("Arial", 12), bg="#E8F0FE").grid(row=2, column=0, pady=5, sticky=W)
src_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=src_lang, font=("Arial", 12))
src_dropdown.grid(row=2, column=0, padx=10)
src_dropdown.bind("<<ComboboxSelected>>", translate_text_live)

# Output Language Selection (No default)
dest_lang = StringVar()
dest_lang.set("English")  # Default set to English
Label(frame, text="To:", font=("Arial", 12), bg="#E8F0FE").grid(row=2, column=1, pady=5, sticky=W)
dest_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=dest_lang, font=("Arial", 12))
dest_dropdown.grid(row=2, column=1, padx=10)
dest_dropdown.bind("<<ComboboxSelected>>", translate_text_live)

# Buttons
button_frame = Frame(root, bg="#E8F0FE")
button_frame.pack(pady=10)

voice_button = Button(button_frame, text="🎤 Speak", font=("Arial", 14), command=recognize_speech, bg="#28A745", fg="white", padx=10, pady=5)
voice_button.grid(row=0, column=0, padx=5)

clear_button = Button(button_frame, text="Clear", font=("Arial", 14), command=lambda: [input_text.delete("1.0", END), output_text.config(state=NORMAL), output_text.delete("1.0", END), output_text.config(state=DISABLED)], bg="#DC3545", fg="white", padx=10, pady=5)
clear_button.grid(row=0, column=1, padx=5)

root.mainloop()