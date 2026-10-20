# MindVault — Personal Knowledge Assistant

MindVault is a personal knowledge management web application built with Python, Flask, and SQLite. It helps users create, organize, search, update, and delete their notes through a simple dashboard.

## Features

- Create and save notes
- Organize notes by category
- Search notes by keyword
- Edit and delete notes
- Store notes persistently using SQLite
- Responsive web dashboard

## Tech Stack

- *Language:* Python
- *Backend:* Flask
- *Database:* SQLite
- *Frontend:* HTML, CSS, JavaScript
- *Tools:* VS Code, Git, GitHub

## Project Structure

text
personal-knowledge-assistant-test/
├── webapp/
│   ├── app.py
│   └── templates/
│       └── index.html
├── .gitignore
└── README.md


## Run Locally

1. Clone the repository:

   bash
   git clone https://github.com/satyam-more-dev/personal-knowledge-assistant.git
   

2. Open the project folder in VS Code.

3. Create and activate a virtual environment, then install Flask:

   bash
   python -m venv .venv
   

   Windows PowerShell:

   powershell
   .\.venv\Scripts\Activate.ps1
   pip install flask
   

4. Start the application from the project root:

   powershell
   python .\webapp\app.py
   

5. Open http://127.0.0.1:5000 in your browser.

## Current Status

Core note management features have been tested locally, including create, read, update, delete, search, and persistence after page refresh.

## Future Improvements

- Progressive Web App (PWA) installation
- Offline support
- Backup and restore
- AI-powered semantic search and question answering
- Deployment and automated tests

## Author

Satyam Nilesh More

B.Tech Information Technology Student