# multi-Api-Use-Gpt-Chat-bot-
# Multi-API Chatbot

A chatbot application built using Tkinter and CustomTkinter that supports multiple AI APIs including DeepSeek, ChatGPT, Blackbox AI, v0.dev, and Kimi (Moonshot.cn). The application allows users to chat with AI models, save chat history, and upload files for further interaction.

## Features
- Supports multiple AI APIs
- Streamed responses for ChatGPT
- Chat history auto-save and load
- File uploads (documents, images, videos, audio)
- Model selection for ChatGPT
- Copy and replay chat history
- Regenerate last response and continue conversation

## Installation

### Prerequisites
Ensure you have Python installed (>=3.7). Install dependencies using:
```sh
pip install -r requirements.txt
```

### Running the Application
```sh
python main.py
```

## Configuration
The application requires an API Key. You can set it up when launching the application, and it will be stored in `config.json`.

## APIs Supported
- **DeepSeek**
- **ChatGPT (OpenAI)**
- **Blackbox AI**
- **v0.dev**
- **Kimi (Moonshot.cn)**

## Usage
1. Launch the application and enter your API Key.
2. Select the desired AI API from the dropdown.
3. Start chatting by typing in the input box and pressing send.
4. Use additional features like file uploads, chat history management, and model selection for ChatGPT.

## File Uploads
The application supports uploading the following file types:
- **Documents**: PDF, DOC, DOCX, TXT
- **Images**: PNG, JPG, JPEG, GIF
- **Videos**: MP4, AVI, MOV
- **Audio**: MP3, WAV, OGG

## Chat History
Chat history is automatically saved in the `chat_history` directory and can be loaded within the application.

## License
This project is open-source and available under the MIT License.

