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
    if st.button("🔍 Generate Answer"):
        with st.spinner("Thinking..."):
            answer = ask_gemini(user_question, file_text)
        st.markdown("### 🧠 Answer:")
        st.write(answer)

    if st.button("📝 Generate MCQs"):
        with st.spinner("Creating MCQs..."):
            prompt = (
                "Generate exactly 5 multiple choice questions based on the text below. Each question must follow this strict format:\n\n"
                "Q1: What is ...?\n"
                "a) ...\n"
                "b) ...\n"
                "c) ...\n"
                "d) ...\n"
                "Answer: b\n\n"
                "Only use plain text. Do not use Markdown or bullets.\n\n"
                "Text:\n" + file_text
            )
            raw_mcqs = ask_gemini(prompt, "")

        st.session_state.quiz_data = raw_mcqs
        st.session_state.submitted = False

    # ✅ Show debug output
    if "quiz_data" in st.session_state and st.session_state.quiz_data:
        st.subheader("Here YOU GO")


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

        if questions:
            st.subheader("🧪 Quiz Time!")
            user_answers = []

            for idx, q in enumerate(questions):
                st.markdown(f"**Q{idx+1}: {q['question']}**")
                selected = st.radio(f"Choose an answer for Q{idx+1}", q["options"], key=f"q_{idx}")
                user_answers.append(selected[0].lower())  # store a/b/c/d

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
        else:
            st.error("⚠️ Could not parse MCQs. Try regenerating or simplify your PDF.")
