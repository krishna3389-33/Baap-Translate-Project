from tkinter import *
from tkinter import ttk, messagebox
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import speech_recognition as sr
import threading

DetectorFactory.seed = 0  # Ensures consistent language detection

delay_time = 0  # Delay before translating after user stops typing
translate_timer = None

def recognize_speech():
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300  # Adjust sensitivity
    try:
        with sr.Microphone() as source:
            messagebox.showinfo("Voice Input", "Speak now...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, phrase_time_limit=10)
            
            def process_audio():
                try:
                    text = recognizer.recognize_google(audio).strip()
                    input_text.insert(END, text + " ")  
                except sr.UnknownValueError:
                    messagebox.showwarning("Speech Error", "Could not understand the audio.")
                except sr.RequestError:
                    messagebox.showerror("Speech Error", "Could not connect to Google services. Check your internet connection.")
                except Exception as e:
                    messagebox.showerror("Speech Error", f"An unexpected error occurred: {e}")
            
            threading.Thread(target=process_audio, daemon=True).start()
    except Exception as e:
        messagebox.showerror("Speech Error", f"An unexpected error occurred: {e}")

def detect_language(text):
    try:
        return detect(text)
    except:
        return "auto"

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

def on_text_change(event=None):
    delayed_translation()

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    new_bg = "#121212" if dark_mode else "#FFFFFF"
    new_fg = "white" if dark_mode else "black"
    text_bg = "black" if dark_mode else "white"
    text_fg = "white" if dark_mode else "black"
    button_bg = "#333333" if dark_mode else "#F0F0F0"
    button_fg = "white" if dark_mode else "black"
    
    input_text.config(bg=text_bg, fg=text_fg, insertbackground=text_fg)
    output_text.config(bg=text_bg, fg=text_fg, insertbackground=text_fg)
    frame.config(bg=new_bg)
    root.config(bg=new_bg)
    button_frame.config(bg=new_bg)
    theme_button.config(text="Light Mode" if dark_mode else "Dark Mode", bg=button_bg, fg=button_fg)
    voice_button.config(bg="#28A745", fg="white")
    clear_button.config(bg="#DC3545", fg="white")
    title_label.config(bg=new_bg, fg=new_fg)
    
    for widget in frame.winfo_children():
        if isinstance(widget, Label):
            widget.config(bg=new_bg, fg=new_fg)
        elif isinstance(widget, ttk.Combobox):
            widget.configure(style="Dark.TCombobox" if dark_mode else "Light.TCombobox")
    
    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Dark.TCombobox", fieldbackground="black", background="black", foreground="white")
    style.configure("Light.TCombobox", fieldbackground="white", background="white", foreground="black")

dark_mode = False
root = Tk()
root.title("Google Translate Clone")
root.geometry("950x550")
root.configure(bg="#FFFFFF")

# Language dictionary
languages = GoogleTranslator().get_supported_languages()
lang_dict = {"Auto-detect": "auto"}
lang_dict.update({lang.capitalize(): lang for lang in languages})

# UI Elements
title_label = Label(root, text="Google Translate Clone", font=("Arial", 18, "bold"), bg="#FFFFFF", fg="black")
title_label.pack(pady=10)

frame = Frame(root, bg="#FFFFFF")
frame.pack(pady=10)

Label(frame, text="Input Text:", font=("Arial", 12), bg="#FFFFFF", fg="black").grid(row=0, column=0, sticky=W)
input_text = Text(frame, height=10, width=50, font=("Arial", 12), bg="#FFFFFF", fg="black")
input_text.grid(row=1, column=0, padx=10, pady=10)
input_text.bind("<KeyRelease>", on_text_change)

Label(frame, text="Translated Text:", font=("Arial", 12), bg="#FFFFFF", fg="black").grid(row=0, column=1, sticky=W)
output_text = Text(frame, height=10, width=50, font=("Arial", 12), bg="#FFFFFF", fg="black", state='disabled')
output_text.grid(row=1, column=1, padx=10, pady=10)

# Input Language Selection
src_lang = StringVar()
src_lang.set("Auto-detect")
Label(frame, text="From:", font=("Arial", 12), bg="#FFFFFF", fg="black").grid(row=2, column=0, pady=5, sticky=W)
src_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=src_lang, font=("Arial", 12))
src_dropdown.grid(row=2, column=0, padx=10)

# Output Language Selection
dest_lang = StringVar()
dest_lang.set("English")
Label(frame, text="To:", font=("Arial", 12), bg="#FFFFFF", fg="black").grid(row=2, column=1, pady=5, sticky=W)
dest_dropdown = ttk.Combobox(frame, values=list(lang_dict.keys()), textvariable=dest_lang, font=("Arial", 12))
dest_dropdown.grid(row=2, column=1, padx=10)

# Buttons
button_frame = Frame(root, bg="#FFFFFF")
button_frame.pack(pady=10)

voice_button = Button(button_frame, text="🎤 Speak", font=("Arial", 12), command=recognize_speech, bg="#28A745", fg="white", padx=10, pady=5)
voice_button.grid(row=0, column=0, padx=5)

theme_button = Button(button_frame, text="Dark Mode", font=("Arial", 12), command=toggle_theme, bg="#F0F0F0", fg="black", padx=10, pady=5)
theme_button.grid(row=0, column=1, padx=5)

clear_button = Button(button_frame, text="Clear", font=("Arial", 12), command=lambda: [input_text.delete("1.0", END), output_text.config(state=NORMAL), output_text.delete("1.0", END), output_text.config(state=DISABLED)], bg="#DC3545", fg="white", padx=10, pady=5)
clear_button.grid(row=0, column=2, padx=5)

root.mainloop()