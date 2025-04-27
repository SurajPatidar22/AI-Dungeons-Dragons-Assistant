import random
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as tb
import threading
import requests
import io
import google.generativeai as genai
import openai

# Setup Google Gemini API
genai.configure(api_key="AIzaSyC2n9rFzR4MTPqNiP16s3gTldue5EVmsUA")  # Replace with your key

# Setup OpenAI API
openai.api_key = "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"  # Replace with your key

class DnDAssistant:
    def __init__(self):
        self.root = tb.Window(themename="solar")  
        self.root.title("D&D Campaign and Character Creator")
        self.root.geometry("1200x850")
        self.root.configure(padx=20, pady=20)

        ttk.Label(self.root, text="Dungeons & Dragons Creator", font=("Arial", 30, "bold")).pack(pady=20)

        self.notebook = ttk.Notebook(self.root, bootstyle="secondary")
        self.notebook.pack(pady=10, expand=True, fill="both")

        self.campaign_tab = ttk.Frame(self.notebook, padding=20)
        self.character_tab = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.campaign_tab, text="Campaign Generator")
        self.notebook.add(self.character_tab, text="Character Generator")

        self.setup_campaign_tab()
        self.setup_character_tab()

    def setup_campaign_tab(self):
        frame = ttk.Frame(self.campaign_tab)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Campaign World Builder", font=("Arial", 22, "bold")).pack(pady=10)

        option_frame = ttk.Labelframe(frame, text="Campaign Settings", bootstyle="primary")
        option_frame.pack(pady=10, fill="x")

        ttk.Label(option_frame, text="World Setting:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.setting_var = tk.StringVar()
        setting_box = ttk.Combobox(option_frame, textvariable=self.setting_var, font=("Arial", 11))
        setting_box['values'] = ('Fantasy', 'Dark Fantasy', 'High Fantasy', 'Urban Fantasy', 'Sci-Fi')
        setting_box.grid(row=0, column=1, padx=10)
        setting_box.set('Fantasy')

        ttk.Label(option_frame, text="Campaign Theme:", font=("Arial", 12)).grid(row=0, column=2, padx=10)
        self.category_var = tk.StringVar()
        category_box = ttk.Combobox(option_frame, textvariable=self.category_var, font=("Arial", 11))
        category_box['values'] = ('Adventure', 'Horror', 'Mystery', 'Crime', 'Mythical', 'Comedy')
        category_box.grid(row=0, column=3, padx=10)
        category_box.set('Adventure')

        ttk.Label(frame, text="Custom Description (optional):", font=("Arial", 12)).pack(pady=5)
        self.extra_description = tk.Text(frame, height=3, width=100, font=("Arial", 11))
        self.extra_description.pack(pady=5)

        self.generate_campaign_btn = ttk.Button(frame, text="Generate Campaign", bootstyle="success", command=self.start_generate_campaign)
        self.generate_campaign_btn.pack(pady=15)

        self.campaign_progress = ttk.Progressbar(frame, mode="indeterminate", bootstyle="info-striped")
        self.campaign_progress.pack(fill="x", pady=5)

        self.campaign_result = tk.Text(frame, height=20, width=120, font=("Arial", 11))  # Big height for long text
        self.campaign_result.pack(pady=10)

        self.campaign_image_label = ttk.Label(frame)
        self.campaign_image_label.pack(pady=10)

    def setup_character_tab(self):
        frame = ttk.Frame(self.character_tab)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Character Creator", font=("Arial", 22, "bold")).pack(pady=10)

        option_frame = ttk.Labelframe(frame, text="Character Settings", bootstyle="primary")
        option_frame.pack(pady=10, fill="x")

        ttk.Label(option_frame, text="Race:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        self.race_var = tk.StringVar()
        race_box = ttk.Combobox(option_frame, textvariable=self.race_var, font=("Arial", 11))
        race_box['values'] = ('Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn')
        race_box.grid(row=0, column=1, padx=10)
        race_box.set('Human')

        ttk.Label(option_frame, text="Class:", font=("Arial", 12)).grid(row=0, column=2, padx=10)
        self.class_var = tk.StringVar()
        class_box = ttk.Combobox(option_frame, textvariable=self.class_var, font=("Arial", 11))
        class_box['values'] = ('Fighter', 'Wizard', 'Rogue', 'Cleric', 'Ranger')
        class_box.grid(row=0, column=3, padx=10)
        class_box.set('Fighter')

        ttk.Label(option_frame, text="Background:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.background_var = tk.StringVar()
        background_box = ttk.Combobox(option_frame, textvariable=self.background_var, font=("Arial", 11))
        background_box['values'] = ('Forest', 'Castle', 'Desert', 'Mountain', 'City')
        background_box.grid(row=1, column=1, padx=10)
        background_box.set('Forest')

        self.generate_character_btn = ttk.Button(frame, text="Generate Character", bootstyle="success", command=self.start_generate_character)
        self.generate_character_btn.pack(pady=15)

        self.character_progress = ttk.Progressbar(frame, mode="indeterminate", bootstyle="info-striped")
        self.character_progress.pack(fill="x", pady=5)

        self.character_result = tk.Text(frame, height=20, width=120, font=("Arial", 11))  # Big height for long text
        self.character_result.pack(pady=10)

        self.character_image_label = ttk.Label(frame)
        self.character_image_label.pack(pady=10)

    def start_generate_campaign(self):
        threading.Thread(target=self.generate_campaign).start()

    def generate_campaign(self):
        self.generate_campaign_btn.config(state="disabled")
        self.campaign_progress.start()

        setting = self.setting_var.get()
        category = self.category_var.get()
        user_desc = self.extra_description.get("1.0", tk.END).strip()

        prompt = f"Create a Dungeons & Dragons campaign in a {setting} world with a {category} theme."
        if user_desc:
            prompt += f" Include: {user_desc}"
        prompt += " Suggest a fantasy illustration description too."

        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        full_text = response.text
        parts = full_text.split("Scene Description:")
        campaign_text = parts[0].strip()
        scene_description = parts[1].strip() if len(parts) > 1 else "Mysterious mountains covered with mist."

        self.campaign_result.delete(1.0, tk.END)
        self.campaign_result.insert(tk.END, campaign_text)  # FULL text shown

        self.display_image_from_description(scene_description, self.campaign_image_label)

        self.generate_campaign_btn.config(state="normal")
        self.campaign_progress.stop()

    def start_generate_character(self):
        threading.Thread(target=self.generate_character).start()

    def generate_character(self):
        self.generate_character_btn.config(state="disabled")
        self.character_progress.start()

        race = self.race_var.get()
        char_class = self.class_var.get()
        background = self.background_var.get()

        prompt = f"Create a D&D character sheet for a {race} {char_class} from a {background} background. Suggest a fantasy art description too."

        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        response = model.generate_content(prompt)

        full_text = response.text
        parts = full_text.split("Scene Description:")
        character_text = parts[0].strip()
        scene_description = parts[1].strip() if len(parts) > 1 else f"A {char_class} hero standing in a {background}."

        self.character_result.delete(1.0, tk.END)
        self.character_result.insert(tk.END, character_text)  # FULL text shown

        self.display_image_from_description(scene_description, self.character_image_label)

        self.generate_character_btn.config(state="normal")
        self.character_progress.stop()

    def display_image_from_description(self, description, label):
        try:
            response = openai.Image.create(
                prompt=description,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']

            img_data = requests.get(image_url).content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((600, 400))
            photo = ImageTk.PhotoImage(img)

            label.config(image=photo)
            label.image = photo
        except Exception as e:
            print("Image Generation Error:", e)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DnDAssistant()
    app.run()
