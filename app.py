from groq import Groq
import streamlit as st
import json
import PyPDF2
import os
from datetime import datetime
import uuid

# --- Configuration ---
# MODIFIED: Initialize the Groq client.
# Make sure your secret is named GROQ_API_KEY in your secrets.toml file.
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    MODEL = "llama-3.1-8b-instant" # Define the model we'll use
except Exception as e:
    st.error("Groq API key not found. Please add it to your Streamlit secrets.", icon="🚨")
    st.stop()

# --- History File (No changes needed here) ---
ACTIVITY_HISTORY_FILE = "activity_history.json"

# --- Helper Functions (No changes needed here) ---
def load_history(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try: return json.load(f)
            except json.JSONDecodeError: return []
    return []

def save_history(filename, history):
    with open(filename, 'w') as f:
        json.dump(history, f, indent=2)

def add_to_activity_history(activity_type, content):
    history_entry = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": activity_type,
        "content": content
    }
    st.session_state.activity_history.append(history_entry)
    save_history(ACTIVITY_HISTORY_FILE, st.session_state.activity_history)

# --- Session State (No changes needed here) ---
st.session_state.setdefault('quiz_generated', None)
st.session_state.setdefault('quiz_results', None)
st.session_state.setdefault('flashcards_generated', None)
st.session_state.setdefault('current_card_index', 0)
st.session_state.setdefault('card_is_flipped', False)
st.session_state.setdefault('uploaded_text', "")
st.session_state.setdefault('activity_history', load_history(ACTIVITY_HISTORY_FILE))
st.session_state.setdefault('doc_quiz_generated', None)
st.session_state.setdefault('doc_quiz_results', None)

# --- Streamlit App Interface ---
st.set_page_config(page_title="AI Powered Study Buddy", page_icon="🎓")
st.title("🎓 AI Powered Study Buddy")

# --- Feature Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Study Tools 📝", "Writing Assistant ✍️", "Planner & Visualizer 🗓️", "Chat with Docs 💬", "Activity History 📜"])

# --- Helper function for Groq API calls ---
def get_groq_response(prompt):
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
    )
    return chat_completion.choices[0].message.content

# --- TAB 1: Study Tools ---
with tab1:
    st.header("1. Explain a Complex Topic")
    explain_topic_input = st.text_input("Enter a topic:", placeholder="e.g., Photosynthesis")
    if st.button("Explain Topic", key="explain_button"):
        if explain_topic_input:
            prompt = f"Explain '{explain_topic_input}' simply for a high school student."
            with st.spinner("🧠 Thinking..."):
                # MODIFIED: Switched to Groq
                response_text = get_groq_response(prompt)
                st.info(response_text)
                add_to_activity_history("Explain Topic", {"topic": explain_topic_input, "explanation": response_text})
        else: st.warning("Please enter a topic.")
    
    st.divider()
    st.header("2. Summarize Your Notes")
    notes_input_summary = st.text_area("Paste notes to summarize:", height=150, key="summary_notes")
    if st.button("Summarize Notes", key="summarize_button"):
        if notes_input_summary:
            prompt = f"Summarize these notes into key bullet points:\n\n{notes_input_summary}"
            with st.spinner("📝 Summarizing..."):
                # MODIFIED: Switched to Groq
                response_text = get_groq_response(prompt)
                st.success(response_text)
                add_to_activity_history("Summarize Notes", {"notes": "...", "summary": response_text})
        else: st.warning("Please paste your notes.")

    st.divider()
    st.header("3. Generate an Interactive Quiz")
    notes_input_quiz = st.text_area("Paste notes for a quiz:", height=150, key="quiz_notes")
    difficulty = st.selectbox("Difficulty:", ("Easy", "Medium", "Hard"), key="difficulty_selector")
    if st.button("Generate Quiz", key="generate_quiz_button"):
        if notes_input_quiz:
            prompt = f"""Create a 5-question multiple-choice quiz of '{difficulty}' difficulty from these notes. Output as a valid JSON list only. Each object must have "question", "options" (a list), "answer", and "explanation". Do not write any text outside the JSON block. Notes: {notes_input_quiz}"""
            with st.spinner(f"🧐 Generating a {difficulty} Quiz..."):
                try:
                    # MODIFIED: Switched to Groq
                    response_text = get_groq_response(prompt)
                    cleaned_response = response_text.strip().replace("```json", "").replace("```", "")
                    quiz_data = json.loads(cleaned_response)
                    st.session_state.quiz_generated = quiz_data
                    st.session_state.quiz_results = None
                    history_content = {"difficulty": difficulty, "notes": "...", "quiz_questions": [{ "question": q['question'], "answer": q['answer'] } for q in quiz_data]}
                    add_to_activity_history("Generate Quiz", history_content)
                except (json.JSONDecodeError, Exception) as e:
                    st.error(f"Failed to generate quiz. The model output may not be valid JSON. Error: {e}")
        else: st.warning("Please paste notes for the quiz.")
    
    # The rest of the quiz logic remains the same
    if st.session_state.quiz_generated and not st.session_state.quiz_results:
        with st.form("quiz_form"):
            user_answers = {i: st.radio(f"**{q['question']}**", q['options'], key=f"q{i}", index=None) for i, q in enumerate(st.session_state.quiz_generated)}
            if st.form_submit_button("Submit Answers"):
                if None in user_answers.values(): st.warning("Please answer all questions.")
                else:
                    score = 0; results = []
                    for i, q in enumerate(st.session_state.quiz_generated):
                        is_correct = user_answers[i].strip() == q['answer'].strip()
                        if is_correct:
                            score += 1
                            results.append(f"✅ **Q{i+1}: Correct!**")
                        else:
                            results.append(f"❌ **Q{i+1}: Incorrect.** Correct answer: **{q['answer']}**\n\n   *Explanation: {q.get('explanation', 'N/A')}*")
                    st.session_state.quiz_results = {"score": score, "total": len(st.session_state.quiz_generated), "details": results}
                    
    if st.session_state.quiz_results:
        res = st.session_state.quiz_results
        st.success(f"🎉 You scored {res['score']} out of {res['total']}!")
        for detail in res['details']:
            st.markdown(detail)

    st.divider()
    st.header("4. Generate Flashcards")
    notes_input_flashcards = st.text_area("Paste notes for flashcards:", height=150, key="flashcards_notes")
    if st.button("Generate Flashcards", key="generate_flashcards_button"):
        if notes_input_flashcards:
            prompt = f"""Create 10 flashcards from these notes. Output as a valid JSON list only. Each object needs "front" and "back" keys. Do not write any text outside the JSON block. Notes: {notes_input_flashcards}"""
            with st.spinner("✨ Creating Flashcards..."):
                try:
                    # MODIFIED: Switched to Groq
                    response_text = get_groq_response(prompt)
                    cleaned_response = response_text.strip().replace("```json", "").replace("```", "")
                    flashcard_data = json.loads(cleaned_response)
                    st.session_state.flashcards_generated = flashcard_data
                    st.session_state.current_card_index = 0; st.session_state.card_is_flipped = False
                    add_to_activity_history("Generate Flashcards", {"notes": "...", "flashcards": flashcard_data})
                except (json.JSONDecodeError, Exception) as e: st.error(f"Failed to create flashcards. Error: {e}")
        else: st.warning("Please paste notes for flashcards.")

    # The rest of the flashcard logic remains the same
    if st.session_state.flashcards_generated:
        total_cards = len(st.session_state.flashcards_generated); card_index = st.session_state.current_card_index
        if card_index >= total_cards: card_index = st.session_state.current_card_index = 0
        st.write(f"Card {card_index + 1} of {total_cards}")
        card = st.session_state.flashcards_generated[card_index]
        with st.container(border=True):
            content = card['back'] if st.session_state.card_is_flipped else card['front']
            st.markdown(f"<div style='text-align: center; font-size: 20px; min-height: 120px; display: flex; align-items: center; justify-content: center;'>{content}</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        if col1.button("⬅️ Previous", use_container_width=True, disabled=(card_index == 0)):
            st.session_state.current_card_index -= 1; st.session_state.card_is_flipped = False; st.rerun()
        if col2.button("🔄 Flip Card", type="primary", use_container_width=True):
            st.session_state.card_is_flipped = not st.session_state.card_is_flipped; st.rerun()
        if col3.button("Next ➡️", use_container_width=True, disabled=(card_index >= total_cards - 1)):
            st.session_state.current_card_index += 1; st.session_state.card_is_flipped = False; st.rerun()

# --- TAB 2: Writing Assistant ---
with tab2:
    st.header("Essay & Paragraph Helper")
    writing_topic = st.text_input("Enter your essay topic:", placeholder="The impact of renewable energy...")
    writing_points = st.text_area("Enter key points or requirements (optional):", height=100, placeholder="Mention solar and wind power...")
    writing_task = st.selectbox("What do you need help with?", ("Generate an Outline", "Draft a Paragraph", "Improve Writing Style"))
    if st.button("Get Help", key="writing_help_button"):
        if writing_topic:
            prompt = f"Task: {writing_task}\nTopic: {writing_topic}\nKey Points: {writing_points}"
            with st.spinner("✍️ Working on it..."):
                # MODIFIED: Switched to Groq
                response_text = get_groq_response(prompt)
                st.info(response_text)
                add_to_activity_history(writing_task, {"topic": writing_topic, "points": "...", "result": response_text})
        else: st.warning("Please enter a topic.")

# --- TAB 3: Planner & Visualizer ---
with tab3:
    st.header("Study Schedule Planner")
    planner_details = st.text_area("Enter your subjects, exam dates, and available study times:", height=150, placeholder="Subjects: Math, History, Science.\nExams: Math on Oct 15, History on Oct 20.\nAvailable: 2 hours on weekdays, 4 hours on weekends.")
    if st.button("Create Schedule", key="planner_button"):
        if planner_details:
            prompt = f"Create a balanced study schedule based on these details:\n\n{planner_details}"
            with st.spinner("🗓️ Planning your schedule..."):
                # MODIFIED: Switched to Groq
                response_text = get_groq_response(prompt)
                st.markdown(response_text)
                add_to_activity_history("Create Schedule", {"details": planner_details, "schedule": response_text})
        else: st.warning("Please enter your study details.")
    
    st.divider()
    st.header("Concept Visualizer (Mind Map)")
    mind_map_topic = st.text_input("Enter a topic to visualize:", placeholder="The Water Cycle")
    if st.button("Generate Mind Map", key="mind_map_button"):
        if mind_map_topic:
            prompt = f"Generate a mind map outline for '{mind_map_topic}'. Use nested markdown bullets."
            with st.spinner("🗺️ Visualizing concepts..."):
                # MODIFIED: Switched to Groq
                response_text = get_groq_response(prompt)
                st.markdown(response_text)
                add_to_activity_history("Generate Mind Map", {"topic": mind_map_topic, "map": response_text})
        else: st.warning("Please enter a topic.")

# --- TAB 4: Chat with Your Documents ---
with tab4:
    st.header("Chat with Your Documents")
    
    uploaded_file = st.file_uploader("Upload a PDF document", type="pdf", key="doc_uploader")
    if uploaded_file:
        try:
            reader = PyPDF2.PdfReader(uploaded_file); text = "".join(page.extract_text() for page in reader.pages)
            if st.session_state.uploaded_text != text: 
                st.session_state.uploaded_text = text
                st.success("File uploaded. You can now chat with it.")
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            st.session_state.uploaded_text = ""
    
    if st.session_state.uploaded_text:
        doc_chats = [item for item in st.session_state.activity_history if item['type'] == 'Chat with Docs']
        for chat in doc_chats:
            with st.chat_message("user"): st.write(chat["content"]["question"])
            with st.chat_message("assistant"): st.write(chat["content"]["answer"])

        user_question = st.chat_input("Ask a question, or type 'generate a quiz'...")
        if user_question:
            if "quiz" in user_question.lower():
                st.session_state.doc_quiz_results = None 
                prompt = f"""Based on the document, {user_question}. Output as a valid JSON list only. Each object must have "question", "options", "answer", and "explanation". Do not write any text outside the JSON block. Document: {st.session_state.uploaded_text}"""
                with st.spinner("🧐 Generating a quiz from your document..."):
                    try:
                        # MODIFIED: Switched to Groq
                        response_text = get_groq_response(prompt)
                        cleaned_response = response_text.strip().replace("```json", "").replace("```", "")
                        doc_quiz_data = json.loads(cleaned_response)
                        st.session_state.doc_quiz_generated = doc_quiz_data
                        history_content = {"filename": uploaded_file.name, "request": user_question, "quiz_data": doc_quiz_data}
                        add_to_activity_history("Doc Quiz Generated", history_content)
                        
                    except (json.JSONDecodeError, Exception) as e: st.error(f"Failed to generate quiz. Error: {e}")
            else:
                # Display the user's question immediately
                with st.chat_message("user"):
                    st.write(user_question)

                # Prepare the prompt for the AI
                prompt = f"Based on this document, answer the question.\n\nDocument:\n{st.session_state.uploaded_text}\n\nQuestion: {user_question}"

                # Get the AI's answer and display it in a new message
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching document..."):
                        answer = get_groq_response(prompt)
                        st.write(answer) # <-- THE KEY FIX: Display the answer now!

                # Now, save the conversation to the history AFTER it has been displayed
                add_to_activity_history("Chat with Docs", {"question": user_question, "answer": answer})
                    
        # The rest of the doc quiz logic remains the same
        if st.session_state.doc_quiz_generated and not st.session_state.doc_quiz_results:
            st.info("A quiz has been generated. Please submit your answers below.")
            with st.form("doc_quiz_form"):
                user_answers = {i: st.radio(f"**{q['question']}**", q['options'], key=f"doc_q{i}", index=None) for i, q in enumerate(st.session_state.doc_quiz_generated)}
                if st.form_submit_button("Submit Document Quiz"):
                    if None in user_answers.values(): st.warning("Please answer all questions.")
                    else:
                        score = 0; results = []
                        for i, q in enumerate(st.session_state.doc_quiz_generated):
                            is_correct = user_answers[i].strip() == q['answer'].strip()
                            if is_correct:
                                score += 1
                                results.append(f"✅ **Q{i+1}: Correct!**")
                            else:
                                results.append(f"❌ **Q{i+1}: Incorrect.** Correct answer: **{q['answer']}**\n\n   *Explanation: {q.get('explanation', 'N/A')}*")
                        st.session_state.doc_quiz_results = {"score": score, "total": len(st.session_state.doc_quiz_generated), "details": results}
                        
        if st.session_state.doc_quiz_results:
            res = st.session_state.doc_quiz_results
            st.success(f"🎉 You scored {res['score']} out of {res['total']}!")
            for detail in res['details']:
                st.markdown(detail)

# --- TAB 5: Activity History (No changes needed here) ---
with tab5:
    st.header("Your Activity History")
    
    if st.button("Clear All Activity History"):
        st.session_state.activity_history = []; save_history(ACTIVITY_HISTORY_FILE, []); st.success("Activity history cleared."); st.rerun()
        
    if not st.session_state.activity_history:
        st.info("Your activity history is empty.")
    else:
        for item in reversed(st.session_state.activity_history):
            col1, col2 = st.columns([4, 1])
            with col1:
                with st.expander(f"**{item['type']}** - {item['timestamp']}"):
                    content = item.get('content', {})
                    if item['type'] == 'Explain Topic':
                        st.subheader(f"Topic: {content.get('topic', 'N/A')}")
                        st.markdown(content.get('explanation', 'No explanation available.'))
                    elif item['type'] == 'Summarize Notes':
                        st.subheader("Summary")
                        st.markdown(content.get('summary', 'No summary available.'))
                    elif item['type'] == 'Generate Quiz':
                        st.subheader(f"Quiz on {content.get('difficulty', 'N/A')} difficulty")
                        for i, q_item in enumerate(content.get('quiz_questions', [])):
                            st.markdown(f"**{i+1}. {q_item.get('question', 'N/A')}**")
                            st.write(f"*Answer: {q_item.get('answer', 'N/A')}*")
                    elif item['type'] == 'Generate Flashcards':
                        st.subheader("Flashcards Generated")
                        for i, card in enumerate(content.get('flashcards', [])):
                            st.markdown(f"**{i+1}. Front:** {card.get('front', 'N/A')}")
                            st.write(f"**Back:** {card.get('back', 'N/A')}")
                            st.markdown("---")
                    elif item['type'] == 'Chat with Docs':
                        st.markdown(f"**You:** {content.get('question', 'N/A')}")
                        st.markdown(f"**Buddy:** {content.get('answer', 'N/A')}")
                    elif item['type'] == 'Doc Quiz Generated':
                        st.subheader(f"Quiz from: {content.get('filename', 'N/A')}")
                        st.write(f"Request: \"{content.get('request', 'N/A')}\"")
                        st.markdown("---")
                        for i, q in enumerate(content.get('quiz_data', [])):
                            st.markdown(f"**Q{i+1}: {q.get('question', 'N/A')}**")
                            st.write(f"*Correct Answer: {q.get('answer', 'N/A')}*")
                    elif item['type'] in ['Generate an Outline', 'Draft a Paragraph', 'Improve Writing Style']:
                        st.subheader(f"Topic: {content.get('topic', 'N/A')}")
                        st.markdown("---")
                        st.code(content.get('result', 'No result available.'), language=None)
                    elif item['type'] == 'Create Schedule':
                        st.subheader("Generated Schedule")
                        st.markdown(content.get('schedule', 'No schedule available.'))
                    elif item['type'] == 'Generate Mind Map':
                        st.subheader(f"Mind Map for: {content.get('topic', 'N/A')}")
                        st.markdown(content.get('map', 'No map available.'))
                    else:
                        st.json(content)
            with col2:
                item_id = item.get('id')
                if item_id:
                    if st.button("Delete", key=f"del_{item_id}", use_container_width=True):
                        st.session_state.activity_history = [i for i in st.session_state.activity_history if i.get('id') != item_id]
                        save_history(ACTIVITY_HISTORY_FILE, st.session_state.activity_history)
                        st.rerun()
                        