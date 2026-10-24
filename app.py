

import pandas as pd
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from modules.pdf_parser import extract_resume_text
from modules.skill_extractor import extract_skills_from_text
from modules.report_generator import generate_resume_feedback


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------
import streamlit as st

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# 2. CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
.main-title {
    text-align: center;
    color: #8b5cf6;
    font-size: 38px;
    font-weight: bold;
    margin-bottom: 8px;
}

.subtitle {
    text-align: center;
    color: #a1a1aa;
    margin-bottom: 28px;
}

.section-title {
    color: #a78bfa;
    font-size: 23px;
    font-weight: bold;
    margin-top: 20px;
    margin-bottom: 12px;
}

.result-card {
    padding: 20px;
    border-radius: 12px;
    background: #1e1b2e;
    border: 1px solid #51416f;
    text-align: center;
}

.card-label {
    font-size: 15px;
    color: #d4d4d8;
}

.card-value {
    font-size: 30px;
    font-weight: bold;
    color: #c4b5fd;
    margin-top: 8px;
}

.stButton > button {
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 3. HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">📄 AI Resume Analyzer & Matcher</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Upload your resume, compare your skills with a job description, '
    'and generate a detailed analysis report.'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# --------------------------------------------------
# 4. RESUME UPLOAD AND JOB DESCRIPTION
# --------------------------------------------------

left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.subheader("📁 Upload Resume")

    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf", "docx"],
        help="Upload a text-based PDF or a DOCX document."
    )

with right_col:
    st.subheader("📋 Job Description")

    job_description = st.text_area(
        "Paste the job requirements",
        height=200,
        placeholder=(
            "Example: We are looking for a Python Developer "
            "with SQL, Django, Git, and problem-solving skills."
        )
    )


# --------------------------------------------------
# 5. ANALYZE BUTTON
# --------------------------------------------------

analyze_button = st.button(
    "🚀 Analyze Resume & View Report",
    type="primary",
    use_container_width=True
)


if analyze_button:

    # Validate inputs
    if uploaded_file is None:
        st.error("Please upload your resume first.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:

        try:
            with st.spinner("Reading resume and analyzing skills..."):

                # --------------------------------------
                # 6. EXTRACT RESUME TEXT
                # --------------------------------------

                uploaded_file.seek(0)
                resume_text = extract_resume_text(uploaded_file)

                if not isinstance(resume_text, str) or not resume_text.strip():
                    st.error(
                        "No readable text was found. "
                        "Please upload a valid text-based PDF or DOCX."
                    )
                    st.stop()

                # --------------------------------------
                # 7. EXTRACT SKILLS
                # --------------------------------------

                resume_skills = extract_skills_from_text(resume_text)
                job_skills = extract_skills_from_text(job_description)

                # Normalize the returned skill lists
                resume_skills = sorted({
                    str(skill).strip().lower()
                    for skill in resume_skills
                    if str(skill).strip()
                })

                job_skills = sorted({
                    str(skill).strip().lower()
                    for skill in job_skills
                    if str(skill).strip()
                })

                # --------------------------------------
                # 8. COMPARE SKILLS
                # --------------------------------------

                matched_skills = sorted(
                    set(resume_skills) & set(job_skills)
                )

                missing_skills = sorted(
                    set(job_skills) - set(resume_skills)
                )

                # --------------------------------------
                # 9. CALCULATE SKILL MATCH SCORE
                # --------------------------------------

                if job_skills:
                    skill_score = (
                        len(matched_skills) / len(job_skills)
                    ) * 100
                else:
                    skill_score = 0.0

                # --------------------------------------
                # 10. CALCULATE TEXT SIMILARITY
                # --------------------------------------

                try:
                    vectorizer = TfidfVectorizer(
                        stop_words="english",
                        ngram_range=(1, 2)
                    )

                    tfidf_matrix = vectorizer.fit_transform([
                        resume_text,
                        job_description
                    ])

                    text_score = (
                        cosine_similarity(
                            tfidf_matrix[0:1],
                            tfidf_matrix[1:2]
                        )[0][0] * 100
                    )

                except ValueError:
                    # Handles text with no usable TF-IDF terms
                    text_score = 0.0

                # Combine skill match and text similarity
                match_score = round(
                    (0.8 * skill_score) + (0.2 * text_score),
                    2
                )

                match_score = max(0.0, min(100.0, match_score))

                # --------------------------------------
                # 11. DISPLAY RESULTS
                # --------------------------------------

                st.divider()

                st.markdown(
                    '<div class="section-title">'
                    '📊 Resume Analysis Results'
                    '</div>',
                    unsafe_allow_html=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="card-label">🎯 Resume Match Score</div>
                        <div class="card-value">{match_score:.2f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="card-label">✅ Matched Skills</div>
                        <div class="card-value">{len(matched_skills)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="result-card">
                        <div class="card-label">📌 Missing Skills</div>
                        <div class="card-value">{len(missing_skills)}</div>
                    </div>
                    """, unsafe_allow_html=True)

                st.progress(
                    int(round(match_score)),
                    text=f"Overall Resume Match: {match_score:.2f}%"
                )

                # --------------------------------------
                # 12. MATCHED AND MISSING SKILLS
                # --------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    '🧩 Skill Comparison'
                    '</div>',
                    unsafe_allow_html=True
                )

                skill_col1, skill_col2 = st.columns(2)

                with skill_col1:
                    st.success("✅ Matched Skills")

                    if matched_skills:
                        for skill in matched_skills:
                            st.write(f"✓ {skill.title()}")
                    else:
                        st.write("No matching skills found.")

                with skill_col2:
                    st.error("❌ Skills to Develop")

                    if missing_skills:
                        for skill in missing_skills:
                            st.write(f"• {skill.title()}")
                    else:
                        st.write(
                            "All recognized required skills were found."
                        )

                # --------------------------------------
                # 13. ALL RESUME SKILLS
                # --------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    '🧠 Skills Found in Resume'
                    '</div>',
                    unsafe_allow_html=True
                )

                if resume_skills:
                    st.write(", ".join(
                        skill.title() for skill in resume_skills
                    ))
                else:
                    st.warning(
                        "No recognized skills were found. "
                        "Check your skill_extractor.py file."
                    )

                # --------------------------------------
                # 14. SKILL COMPARISON TABLE
                # --------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    '📋 Detailed Skill Report'
                    '</div>',
                    unsafe_allow_html=True
                )

                report_rows = []

                for skill in job_skills:
                    report_rows.append({
                        "Required Skill": skill.title(),
                        "Status": (
                            "Matched"
                            if skill in matched_skills
                            else "Missing"
                        )
                    })

                report_df = pd.DataFrame(
                    report_rows,
                    columns=["Required Skill", "Status"]
                )

                if report_df.empty:
                    st.info(
                        "No recognized skills were found in the job "
                        "description. Add required skills to generate "
                        "the comparison table."
                    )
                else:
                    st.dataframe(
                        report_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # CSV download
                    csv_data = report_df.to_csv(
                        index=False
                    ).encode("utf-8-sig")

                    st.download_button(
                        label="📥 Download Skill Report (CSV)",
                        data=csv_data,
                        file_name="resume_analysis.csv",
                        mime="text/csv"
                    )

                # --------------------------------------
                # 15. TEXT SIMILARITY
                # --------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    '📝 Text Similarity Analysis'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.metric(
                    "Resume and Job Description Similarity",
                    f"{text_score:.2f}%"
                )

                st.caption(
                    "Text similarity measures the overlap in textual "
                    "content. It is not a probability of being hired."
                )

                # --------------------------------------
                # 16. PERSONALIZED FEEDBACK
                # --------------------------------------

                st.markdown(
                    '<div class="section-title">'
                    '💡 Resume Feedback'
                    '</div>',
                    unsafe_allow_html=True
                )

                feedback = generate_resume_feedback(
                    resume_skills,
                    job_skills,
                    match_score
                )

                if isinstance(feedback, str):
                    st.info(feedback)
                else:
                    st.write(feedback)

                # --------------------------------------
                # 17. RESUME TEXT PREVIEW
                # --------------------------------------

                with st.expander("📄 View Extracted Resume Text"):
                    st.text(resume_text)

        except Exception as error:
            st.error(
                "Resume analysis failed. Check the project modules "
                "and make sure the uploaded file is readable."
            )

            with st.expander("Technical error details"):
                st.exception(error)


# --------------------------------------------------
# 18. FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    <p style="text-align:center; color:#a78bfa;">
        AI Resume Analyzer | Built with Python, Streamlit and NLP
    </p>
    """,
    unsafe_allow_html=True
)
