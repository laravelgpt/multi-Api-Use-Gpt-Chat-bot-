import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import customtkinter as ctk
import openai
import requests
import json
import os
from datetime import datetime

# Global variables
API_KEY = ""
CONFIG_FILE = "config.json"
CHAT_HISTORY_DIR = "chat_history"
last_user_input = ""
last_bot_response = ""

# API URLs
API_URLS = {
    "DeepSeek": "https://api.deepseek.com/v1/chat/completions",
    "ChatGPT": "https://api.openai.com/v1/chat/completions",
    "Blackbox AI": "https://api.blackbox.ai/v1/chat/completions",  # Replace with actual Blackbox AI URL
    "v0.dev": "https://api.v0.dev/v1/chat/completions",  # Replace with actual v0.dev API URL
    "Kimi (Moonshot.cn)": "https://api.moonshot.cn/v1/chat/completions",  # Replace with actual Kimi API URL
    "ChatGPT Models": "https://api.openai.com/v1/models"  # ChatGPT model list API
}

# Set theme
ctk.set_appearance_mode("System")  # Modes: "System", "Light", "Dark"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

# Ensure chat history directory exists
if not os.path.exists(CHAT_HISTORY_DIR):
    os.makedirs(CHAT_HISTORY_DIR)

# Function to load API configuration from file
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("api_url", ""), config.get("api_key", "")
    return "", ""

# Function to save API configuration to file
def save_config(api_url, api_key):
    config = {"api_url": api_url, "api_key": api_key}
    with open(CONFIG_FILE, "w") as file:
        json.dump(config, file)

# Function to fetch ChatGPT models
def fetch_chatgpt_models():
    try:
        client = openai.OpenAI(api_key=API_KEY)
        models = client.models.list()
        return [model.id for model in models.data]
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch models: {str(e)}")
        return []

# Function to send message to the selected API
def send_to_api(api_url, message):
    try:
        if api_url == API_URLS["ChatGPT"]:
            client = openai.OpenAI(api_key=API_KEY)
            response = client.chat.completions.create(
                model=model_var.get(),
                messages=[{"role": "user", "content": message}],
                stream=True  # Enable streaming
            )
            return response
        else:
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "default",
                "messages": [{"role": "user", "content": message}]
            }
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"API Error: {str(e)}"

# Function to handle sending messages
def send_message(event=None, message=None):
    global last_user_input, last_bot_response
    user_input = message if message else input_text.get("1.0", tk.END).strip()
    if user_input:
        # Add user input to chat history
        chat_history.config(state=tk.NORMAL)
        chat_history.insert(tk.END, f"You: {user_input}\n", "user")
        chat_history.config(state=tk.DISABLED)

        # Clear input text area
        if not message:
            input_text.delete("1.0", tk.END)

        # Send input to the selected API
        selected_api = api_var.get()
        api_url = API_URLS[selected_api]
        response = send_to_api(api_url, user_input)

        # Handle streaming response (for ChatGPT)
        if selected_api == "ChatGPT":
            chat_history.config(state=tk.NORMAL)
            chat_history.insert(tk.END, f"Bot: ", "bot")
            chat_history.config(state=tk.DISABLED)

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    chunk_content = chunk.choices[0].delta.content
                    full_response += chunk_content
                    chat_history.config(state=tk.NORMAL)
                    chat_history.insert(tk.END, chunk_content, "bot")
                    chat_history.config(state=tk.DISABLED)
                    chat_history.see(tk.END)  # Scroll to the end
                    chat_window.update()  # Update the UI in real-time

            chat_history.config(state=tk.NORMAL)
            chat_history.insert(tk.END, "\n", "bot")
            chat_history.config(state=tk.DISABLED)

            # Store the last bot response
            last_bot_response = full_response
        else:
            # Handle non-streaming response
            chat_history.config(state=tk.NORMAL)
            chat_history.insert(tk.END, f"Bot: {response}\n", "bot")
            chat_history.config(state=tk.DISABLED)

            # Store the last bot response
            last_bot_response = response

        # Store the last user input
        last_user_input = user_input

        # Auto-save chat history
        auto_save_chat_history()

# Function to regenerate the last response
def regenerate_response():
    if last_user_input:
        send_message(message=last_user_input)

# Function to continue the conversation
def continue_conversation():
    if last_bot_response:
        send_message(message=last_bot_response)

# Function to handle Enter key press
def on_enter_key(event):
    send_message()

# Function to auto-save chat history
def auto_save_chat_history():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(CHAT_HISTORY_DIR, f"chat_{timestamp}.txt")
        with open(file_path, "w") as file:
            file.write(chat_history.get("1.0", tk.END))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to auto-save chat history: {str(e)}")

# Function to load chat history
def load_chat_history(file_path):
    try:
        with open(file_path, "r") as file:
            chat_history.config(state=tk.NORMAL)
            chat_history.delete("1.0", tk.END)
            chat_history.insert(tk.END, file.read())
            chat_history.config(state=tk.DISABLED)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load chat history: {str(e)}")

# Function to start a new chat
def new_chat():
    chat_history.config(state=tk.NORMAL)
    chat_history.delete("1.0", tk.END)
    chat_history.config(state=tk.DISABLED)

# Function to update history log
def update_history_log():
    history_log.delete("1.0", tk.END)
    for file_name in os.listdir(CHAT_HISTORY_DIR):
        if file_name.endswith(".txt"):
            history_log.insert(tk.END, f"{file_name}\n")

# Function to copy chat history to clipboard
def copy_chat_history():
    chat_history.config(state=tk.NORMAL)
    chat_history_text = chat_history.get("1.0", tk.END)
    chat_history.config(state=tk.DISABLED)
    chat_window.clipboard_clear()
    chat_window.clipboard_append(chat_history_text)
    messagebox.showinfo("Success", "Chat history copied to clipboard!")

# Function to replay chat history
def replay_chat_history():
    chat_history_text = chat_history.get("1.0", tk.END)
    chat_history.config(state=tk.NORMAL)
    chat_history.delete("1.0", tk.END)
    chat_history.insert(tk.END, chat_history_text)
    chat_history.config(state=tk.DISABLED)

# Function to handle file upload
def upload_file(file_type):
    file_paths = filedialog.askopenfilenames(
        title=f"Select {file_type} files",
        filetypes=[(f"{file_type.upper()} files", file_type)]
    )
    if file_paths:
        for file_path in file_paths:
            messagebox.showinfo("File Uploaded", f"{file_type.capitalize()} file uploaded: {file_path}")

# Function to open the chat window
def open_chat_window():
    global API_KEY, chat_window
    API_KEY = api_key_entry.get().strip()

    if not API_KEY:
        messagebox.showerror("Error", "Please enter the API Key.")
        return

    # Save API configuration
    selected_api = api_var.get()
    api_url = API_URLS[selected_api]
    save_config(api_url, API_KEY)

    # Close the API setup window
    api_window.destroy()

    # Open the chat window
    chat_window = ctk.CTk()
    chat_window.title("Multi-API Chatbot")
    chat_window.geometry("1200x800")

    # Configure grid weights for resizing
    chat_window.grid_rowconfigure(0, weight=1)
    chat_window.grid_columnconfigure(1, weight=1)

    # Sidebar for navigation or settings
    sidebar_frame = ctk.CTkFrame(chat_window, width=200, corner_radius=10)
    sidebar_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

    sidebar_label = ctk.CTkLabel(sidebar_frame, text="Menu", font=("Arial", 14, "bold"))
    sidebar_label.pack(pady=10)

    # New Chat button
    new_chat_button = ctk.CTkButton(sidebar_frame, text="New Chat", command=new_chat, fg_color="green")
    new_chat_button.pack(pady=5, fill=tk.X)

    # Copy Chat button
    copy_chat_button = ctk.CTkButton(sidebar_frame, text="Copy Chat", command=copy_chat_history, fg_color="blue")
    copy_chat_button.pack(pady=5, fill=tk.X)

    # Replay Chat button
    #replay_chat_button = ctk.CTkButton(sidebar_frame, text="Replay Chat", command=replay_chat_history, fg_color="orange")
    #replay_chat_button.pack(pady=5, fill=tk.X)

    # Regenerate button
    regenerate_button = ctk.CTkButton(sidebar_frame, text="Regenerate", command=regenerate_response, fg_color="orange")
    regenerate_button.pack(pady=5, fill=tk.X)

    # Continue button
    continue_button = ctk.CTkButton(sidebar_frame, text="Continue", command=continue_conversation, fg_color="green")
    continue_button.pack(pady=5, fill=tk.X)

    # File upload buttons
    upload_label = ctk.CTkLabel(sidebar_frame, text="Upload Files:", font=("Arial", 12))
    upload_label.pack(pady=5)

    upload_document_button = ctk.CTkButton(sidebar_frame, text="Upload Document", command=lambda: upload_file("*.pdf *.doc *.docx *.txt"), fg_color="purple")
    upload_document_button.pack(pady=5, fill=tk.X)

    upload_image_button = ctk.CTkButton(sidebar_frame, text="Upload Image", command=lambda: upload_file("*.png *.jpg *.jpeg *.gif"), fg_color="purple")
    upload_image_button.pack(pady=5, fill=tk.X)

    upload_video_button = ctk.CTkButton(sidebar_frame, text="Upload Video", command=lambda: upload_file("*.mp4 *.avi *.mov"), fg_color="purple")
    upload_video_button.pack(pady=5, fill=tk.X)

    upload_audio_button = ctk.CTkButton(sidebar_frame, text="Upload Audio", command=lambda: upload_file("*.mp3 *.wav *.ogg"), fg_color="purple")
    upload_audio_button.pack(pady=5, fill=tk.X)

    # Model selection dropdown (for ChatGPT)
    if api_var.get() == "ChatGPT":
        model_label = ctk.CTkLabel(sidebar_frame, text="Select Model:", font=("Arial", 12))
        model_label.pack(pady=5)

        global model_var
        model_var = ctk.StringVar(value="gpt-3.5-turbo")
        models = fetch_chatgpt_models()
        model_dropdown = ctk.CTkOptionMenu(sidebar_frame, variable=model_var, values=models)
        model_dropdown.pack(pady=5, fill=tk.X)

    # History Log
    history_label = ctk.CTkLabel(sidebar_frame, text="History Log", font=("Arial", 12))
    history_label.pack(pady=5)

    global history_log
    history_log = scrolledtext.ScrolledText(sidebar_frame, wrap=tk.WORD, width=25, height=10, font=("Arial", 10))
    history_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Update history log
    update_history_log()

    # Load Chat button
    load_chat_button = ctk.CTkButton(sidebar_frame, text="Load Chat", command=lambda: load_chat_history(os.path.join(CHAT_HISTORY_DIR, history_log.get("1.0", tk.END).split("\n")[0])), fg_color="blue")
    load_chat_button.pack(pady=5, fill=tk.X)

    # Main chat area
    main_frame = ctk.CTkFrame(chat_window, corner_radius=10)
    main_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

    # Chat history display
    global chat_history
    chat_history = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, state=tk.DISABLED, width=80, height=30, font=("Arial", 12))
    chat_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # Input area
    input_frame = ctk.CTkFrame(main_frame, corner_radius=10)
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    global input_text
    input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, width=80, height=5, font=("Arial", 12))
    input_text.pack(fill=tk.X, padx=5, pady=5)

    # Bind Enter key to send message
    input_text.bind("<Return>", on_enter_key)

    # Send button
    send_button = ctk.CTkButton(input_frame, text="Send", command=send_message, fg_color="blue")
    send_button.pack(pady=5)

    # Add tags for styling chat history
    chat_history.tag_config("user", foreground="blue")
    chat_history.tag_config("bot", foreground="green")

    # Run the chat window
    chat_window.mainloop()

# Load API configuration
loaded_api_url, loaded_api_key = load_config()

# First window for API URL and API Key input
api_window = ctk.CTk()
api_window.title("API Setup")
api_window.geometry("400x300")

# API selection dropdown
api_label = ctk.CTkLabel(api_window, text="Select API:", font=("Arial", 12))
api_label.pack(pady=5)

api_var = ctk.StringVar(value="DeepSeek")
api_dropdown = ctk.CTkOptionMenu(api_window, variable=api_var, values=list(API_URLS.keys()))
api_dropdown.pack(pady=5)

# API Key input
api_key_label = ctk.CTkLabel(api_window, text="API Key:", font=("Arial", 12))
api_key_label.pack(pady=5)

api_key_entry = ctk.CTkEntry(api_window, width=300, font=("Arial", 12), show="*")
api_key_entry.insert(0, loaded_api_key)  # Pre-fill with saved API Key
api_key_entry.pack(pady=5)

# Save and proceed button
save_button = ctk.CTkButton(api_window, text="Save and Proceed", command=open_chat_window, fg_color="blue")
save_button.pack(pady=20)

# Run the API setup window
api_window.mainloop()
