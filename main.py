import streamlit as st
import re
from utils import extract_text_from_pdf
from agent import ask_gemini

st.set_page_config(page_title="📚 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy for Students")

uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])
if uploaded_file:
    file_text = extract_text_from_pdf(uploaded_file)
    st.success("✅ PDF text extracted successfully!")

    user_question = st.text_input("❓ Ask a question based on your PDF")
    if st.button("Generate Answer"):
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_question, file_text)
        st.markdown("###  Answer:")
        st.write(answer)

    # --- MCQ Quiz Logic ---
    if st.button("📝 Generate MCQs"):
        with st.spinner("Creating MCQs..."):
            prompt = (
                "Generate 5 multiple choice questions from the content below. "
                "Each question should have 4 options (a–d). "
                "Also include the correct answer separately in the format:\n\n"
                "Q1: ...\na) ...\nb) ...\nc) ...\nd) ...\nAnswer: b\n\n"
                + file_text
            )
            raw_mcqs = ask_gemini(prompt, "")

        st.session_state.quiz_data = raw_mcqs
        st.session_state.submitted = False

    if "quiz_data" in st.session_state and st.session_state.quiz_data:
        def parse_mcqs(text):
            pattern = r"Q\d+:\s*(.*?)\n\s*a\)\s*(.*?)\n\s*b\)\s*(.*?)\n\s*c\)\s*(.*?)\n\s*d\)\s*(.*?)\n(?:\*\*|\*|)?Answer:\s*([a-dA-D])(?:\*\*|\*|)?"
            matches = re.findall(pattern, text, re.DOTALL)

            mcqs = []
            for q, a, b, c, d, ans in matches:
                mcqs.append({
                    "question": q.strip(),
                    "options": [
                        f"a) {a.strip()}",
                        f"b) {b.strip()}",
                        f"c) {c.strip()}",
                        f"d) {d.strip()}",
                    ],
                    "answer": ans.strip().lower()
                })
            return mcqs

        questions = parse_mcqs(st.session_state.quiz_data)

        st.subheader("🧪 Quiz Time!")
        user_answers = []

        for idx, q in enumerate(questions):
            st.markdown(f"**Q{idx+1}: {q['question']}**")
            selected = st.radio(
                f"Choose an answer for Q{idx+1}", 
                q["options"], 
                key=f"q_{idx}"
            )
            user_answers.append(selected[0].lower())  # Store only a/b/c/d

        if st.button("✅ Submit Answers"):
            st.session_state.submitted = True
            st.session_state.user_answers = user_answers

        if st.session_state.get("submitted"):
            st.subheader("📝 Results")
            correct_count = 0
            for idx, q in enumerate(questions):
                correct = q["answer"]
                selected = st.session_state.user_answers[idx]
                if selected == correct:
                    st.success(f"✅ Q{idx+1}: Correct!")
                    correct_count += 1
                else:
                    correct_option = q["options"][ord(correct) - ord('a')]
                    st.error(f"❌ Q{idx+1}: Wrong. Correct answer was: {correct_option}")
            st.info(f"🎯 Your Score: {correct_count} / {len(questions)}")
