import streamlit as st
from utils import extract_text_from_pdf
from agent import ask_gemini

st.set_page_config(page_title="📚 AI Study Buddy", layout="wide")
st.title("📘 AI Study Buddy for Students")

uploaded_file = st.file_uploader("📤 Upload a PDF", type=["pdf"])
if uploaded_file:
    file_text = extract_text_from_pdf(uploaded_file)
    st.success("✅ PDF text extracted successfully!")

    user_question = st.text_input("❓ Ask a question based on your PDF")
    if st.button(" Generate Answer"):
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_question, file_text)
        st.markdown("###  Answer:")
        st.write(answer)

    # Generate MCQs and conduct quiz
    if st.button("📝 Generate MCQs"):
        with st.spinner("Creating MCQs..."):
            prompt = (
                "Generate 5 multiple choice questions from the content below. "
                "Each question should have 4 options. Also include the correct answer separately in the format:\n\n"
                "Q1: ...\n"
                "a)...\n"
                "b)...\n"
                "c)...\n"
                "d)...\n"
                "Answer: b\n\n"
                + file_text
            )
            raw_mcqs = ask_gemini(prompt, file_text)


        st.session_state.quiz_data = raw_mcqs
        st.session_state.submitted = False

    if "quiz_data" in st.session_state and st.session_state.quiz_data:
        import re

        def parse_mcqs(text):
            pattern = r"Q\d+: (.*?)\n(a.*?)\n(b.*?)\n(c.*?)\n(d.*?)\nAnswer: ([a-dA-D])"
            matches = re.findall(pattern, text, re.DOTALL)
            mcqs = []
            for q, a, b, c, d, ans in matches:
                mcqs.append({
                    "question": q.strip(),
                    "options": [a.strip(), b.strip(), c.strip(), d.strip()],
                    "answer": ans.strip().lower()
                })
            return mcqs

        questions = parse_mcqs(st.session_state.quiz_data)

        st.subheader("🧪 Quiz Time!")
        user_answers = []

        for idx, q in enumerate(questions):
            st.markdown(f"**Q{idx+1}: {q['question']}**")
            selected = st.radio(f"Choose an answer for Q{idx+1}", q["options"], key=f"q_{idx}")
            user_answers.append(selected[0].lower())  # store only 'a', 'b', 'c', or 'd'

        if st.button("✅ Submit Answers"):
            st.session_state.submitted = True

        if st.session_state.submitted:
            st.subheader("📝 Results")
            correct_count = 0
            for idx, q in enumerate(questions):
                correct = q["answer"]
                selected = user_answers[idx]
                if selected == correct:
                    st.success(f"✅ Q{idx+1}: Correct!")
                    correct_count += 1
                else:
                    st.error(f"❌ Q{idx+1}: Wrong. Correct answer was: {correct.upper()}")
            st.info(f"🎯 Your Score: {correct_count} / {len(questions)}")
