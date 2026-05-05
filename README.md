🎓 AI Powered Study Buddy
An interactive web application built with Streamlit to help students with their learning and productivity. This tool leverages the high-speed Groq API with the Llama 3.1 model to provide a suite of powerful study aids, from explaining complex topics to generating quizzes from your own documents.

✨ Features
This application is organized into five main tabs, each packed with useful features:

📝 Study Tools
Explain a Complex Topic: Get simple, easy-to-understand explanations for any topic.
Summarize Your Notes: Paste in long-form notes and get a concise, bulleted summary of the key points.
Generate Interactive Quizzes: Create multiple-choice quizzes from your notes with adjustable difficulty levels.
Generate Flashcards: Instantly create digital flashcards (front and back) from your study materials and review them in an interactive viewer.

✍️ Writing Assistant
Essay & Paragraph Helper: Get help with your writing assignments. The assistant can:
Generate a structured outline.
Draft a paragraph on a specific topic.
Suggest improvements to your writing style.

🗓️ Planner & Visualizer
Study Schedule Planner: Input your subjects, exam dates, and available times to generate a balanced and effective study schedule.
Concept Visualizer: Enter a topic to generate a mind map outline, helping you visualize connections between different concepts.

💬 Chat with Your Documents
Upload & Chat: Upload a PDF document (lecture notes, textbook chapters, research papers) and ask questions directly about its content.
Quiz from Document: Ask the assistant to generate a quiz based on the content of your uploaded PDF.

📜 Activity History
Persistent Log: All your activities are saved locally. You can review past explanations, summaries, quizzes, and more.
Manage Your History: View the details of any past activity or delete entries you no longer need.

🛠️ Tech Stack
Framework: Streamlit - For building the interactive web interface.
Language: Python 3.11+
AI/LLM Provider: Groq API - For incredibly fast AI model inference.
Model: Llama 3.1 (llama-3.1-8b-instant)
PDF Processing: PyPDF2

🚀 Getting Started
Follow these instructions to set up and run the project on your local machine.
1. Prerequisites
Python 3.11 or higher installed.
A free API key from Groq.
2. Installation & Setup
1. Clone the repository:
git clone https://github.com/your-username/ai-study-buddy.git
cd ai-study-buddy
2. Create and activate a virtual environment:
This is a best practice to keep project dependencies isolated.
On Windows:
python -m venv venv
.\venv\Scripts\activate
On macOS & Linux:
python3 -m venv venv
source venv/bin/activate
3. Install the required libraries:
pip install -r requirements.txt
3. Configuration
The application requires an API key to connect to the Groq service.
1. Create the secrets file:
Create a folder named .streamlit in the root of your project directory.
Inside the .streamlit folder, create a file named secrets.toml.
2. Add your API key to the file:
Open secrets.toml and add your Groq API key in the following format:
GROQ_API_KEY = "gsk_YourSecretGroqApiKeyHere"

4. Running the Application
Once the setup and configuration are complete, you can run the app with a single command:
python -m streamlit run app.py
Your web browser should automatically open to the application's local URL.

📁 Project Structure

AI-Study-Buddy/
├── .streamlit/
│   └── secrets.toml      # Your secret API key (you create this)
├── app.py                # The main Streamlit application script
├── requirements.txt      # A list of all Python dependencies
└── README.md             # This file