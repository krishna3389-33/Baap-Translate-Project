from tkinter import *
from tkinter import ttk, messagebox
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import speech_recognition as sr
import threading

DetectorFactory.seed = 0  # Ensure consistent language detection

root = Tk()
root.title("Typing & Speech Translator")
root.geometry("950x550")
root.configure(bg="#E8F0FE")

# Language dictionary
languages = GoogleTranslator().get_supported_languages()
lang_dict = {"Auto-detect": "auto", **{lang.capitalize(): lang for lang in languages}}

# UI Elements
Label(root, text="Typing & Speech Translator", font=("Arial", 18, "bold"), bg="#E8F0FE").pack(pady=10)

frame = Frame(root, bg="#E8F0FE")
frame.pack(pady=10)

Label(frame, text="Input Text:", font=("Arial", 12), bg="#E8F0FE").grid(row=0, column=0, sticky=W)
input_text = Text(frame, height=10, width=50, font=("Arial", 12))
input_text.grid(row=1, column=0, padx=10, pady=10)

Label(frame, text="Translated Text:", font=("Arial", 12), bg="#E8F0FE").grid(row=0, column=1, sticky=W)
output_text = Text(frame, height=10, width=50, font=("Arial", 12), state='disabled')
output_text.grid(row=1, column=1, padx=10, pady=10)

# Language selection dropdowns
src_lang = StringVar(value="Auto-detect")
dest_lang = StringVar(value="English")

Label(frame, text="From:", font=("Arial", 12), bg="#E8F0FE").grid(row=2, column=0, sticky=W)
src_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=src_lang, font=("Arial", 12))
src_dropdown.grid(row=2, column=0, padx=10)

Label(frame, text="To:", font=("Arial", 12), bg="#E8F0FE").grid(row=2, column=1, sticky=W)
dest_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=dest_lang, font=("Arial", 12))
dest_dropdown.grid(row=2, column=1, padx=10)

# Function to translate text
def translate_text():
    """Translate the input text and display the result."""
    text = input_text.get("1.0", END).strip()
    if not text:
        output_text.config(state=NORMAL)
        output_text.delete("1.0", END)
        output_text.config(state=DISABLED)
        return

    src_code = lang_dict.get(src_lang.get(), "auto")
    dest_code = lang_dict.get(dest_lang.get(), "en")

    try:
        translated_text = GoogleTranslator(source=src_code, target=dest_code).translate(text)
        output_text.config(state=NORMAL)
        output_text.delete("1.0", END)
        output_text.insert(END, translated_text)
        output_text.config(state=DISABLED)
    except Exception as e:
        messagebox.showerror("Translation Error", str(e))

# Debounce logic for faster response time
translate_timer = None
def on_text_change(event=None):
    """Trigger translation only after a short pause in typing."""
    global translate_timer
    if translate_timer:
        translate_timer.cancel()  # Cancel previous timer
    translate_timer = threading.Timer(0.5, translate_text)  # Delay translation slightly
    translate_timer.start()

# Trigger translation when language selection changes
def on_language_change(event=None):
    translate_text()

input_text.bind("<KeyRelease>", on_text_change)
src_dropdown.bind("<<ComboboxSelected>>", on_language_change)
dest_dropdown.bind("<<ComboboxSelected>>", on_language_change)

# Speech recognition function
def recognize_and_translate():
    """Recognize speech and immediately translate."""
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            messagebox.showinfo("Voice Input", "Speak now...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, phrase_time_limit=5)

        recognized_text = recognizer.recognize_google(audio).strip()
        input_text.insert(END, recognized_text + " ")
        translate_text()

    except sr.UnknownValueError:
        messagebox.showwarning("Speech Error", "Could not understand the audio.")
    except sr.RequestError:
        messagebox.showerror("Speech Error", "Check your internet connection.")
    except Exception as e:
        messagebox.showerror("Speech Error", f"An error occurred: {e}")

# Run speech recognition in a separate thread
def start_recognition_thread():
    threading.Thread(target=recognize_and_translate, daemon=True).start()

# Buttons
button_frame = Frame(root, bg="#E8F0FE")
button_frame.pack(pady=10)

Button(button_frame, text="🎤 Speak", font=("Arial", 14), command=start_recognition_thread, bg="#28A745", fg="white", padx=10, pady=5).grid(row=0, column=0, padx=5)

Button(button_frame, text="Clear", font=("Arial", 14), command=lambda: [input_text.delete("1.0", END), output_text.config(state=NORMAL), output_text.delete("1.0", END), output_text.config(state=DISABLED)], bg="#DC3545", fg="white", padx=10, pady=5).grid(row=0, column=1, padx=5)

root.mainloop()
