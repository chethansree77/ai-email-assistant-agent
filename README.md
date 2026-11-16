# 📧 AI Email Assistant Agent

An intelligent AI-powered email assistant built using Python, Streamlit, Ollama, LangChain, and SQLite. It helps users generate professional emails, suggest replies, categorize emails, and manage saved email drafts using a locally running Large Language Model (LLM).

## 🚀 Project Overview

The AI Email Assistant Agent simplifies everyday email tasks using Generative AI. Users can enter instructions or paste existing emails, and the application processes their requests using the locally hosted Gemma 3 model.

The application allows users to review and edit generated emails before saving them. It also maintains email history using an SQLite database.

## ✨ Features

- **Email Generation:** Generate professional emails from simple user instructions.
- **Email Reply Suggestions:** Create suitable replies to incoming emails.
- **Email Categorization:** Categorize emails into Work, Personal, or Urgent.
- **AI Auto Detection:** Automatically identify the user's intended email task.
- **Editable Drafts:** Edit generated email subjects and bodies.
- **Save Email Drafts:** Store email drafts in an SQLite database.
- **Email History:** View, edit, update, and delete saved drafts.
- **Smart Email Search:** Find saved emails using keywords or natural-language descriptions.
- **Input Validation:** Handle empty and unclear instructions.
- **Error Handling:** Display helpful messages when Ollama is unavailable or an AI response is invalid.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Streamlit | User interface |
| Ollama | Run the local language model |
| Gemma 3 (1B) | Generate and process email content |
| LangChain | Connect Python with Ollama |
| SQLite | Store email drafts |
| JSON | Structure AI responses |

## 📁 Project Structure

```text
ai-email-assistant-agent/
│
├── app.py
├── agent.py
├── email_tools.py
├── prompts.py
├── database.py
├── email_assistant.db
│
├── assets/
│   └── style.css
│
├── requirements.txt
├── README.md
├── .gitignore
│
└── venv/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project folder

```bash
cd ai-email-assistant-agent
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Install and start Ollama

Install Ollama from:

https://ollama.com/

Download the Gemma model:

```bash
ollama pull gemma3:1b
```

Start the Ollama server:

```bash
ollama serve
```

Keep the Ollama server running while using the application.

### 7. Run the application

Open another terminal, activate the virtual environment, and execute:

```bash
streamlit run app.py
```

The application will open in your browser.

## 🔄 Application Workflow

1. User enters an instruction or pastes an incoming email.
2. The agent identifies the requested task.
3. The appropriate email tool is selected.
4. The local Gemma model processes the prompt through LangChain.
5. The AI response is validated and displayed.
6. The user reviews and edits the generated content.
7. The final draft is saved in SQLite.
8. Users can access and manage saved drafts through email history.

## 🧪 Testing

The application was tested against the main internship requirements.

| Test | Description | Result |
|---|---|---|
| 1 | Empty input validation | Passed |
| 2 | Generate a new email | Passed |
| 3 | Suggest an email reply | Passed |
| 4 | Categorize an email | Passed |
| 5 | Handle unclear instructions | Passed |
| 6 | Edit and save a draft | Passed |
| 7 | Verify database persistence after restart | Passed |
| 8 | Handle unavailable Ollama server | Passed |
| 9 | Handle invalid AI JSON response | Passed |

## 🔒 Important Notes

- The application uses a locally running language model.
- Generated emails are not sent automatically.
- Users can review and edit drafts before saving them.
- Email drafts are stored locally using SQLite.
- Ollama must be running to use AI-powered features.

## 🎯 Project Objective

The objective of this project is to demonstrate how Generative AI, local Large Language Models, Python, and database integration can be used to build a practical AI-powered email assistant.

## 👩‍💻 Author

**AI Email Assistant Agent – Internship Project**

**Technologies:** Python | Streamlit | Generative AI | Ollama | LangChain | SQLite
