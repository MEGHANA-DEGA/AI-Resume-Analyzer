def generate_resume_feedback(resume_skills, job_skills, match_score):
    feedback = []

    missing_skills = [
        skill for skill in job_skills
        if skill not in resume_skills
    ]

    if match_score >= 80:
        feedback.append("Your resume is a good match for the job.")
    elif match_score >= 50:
        feedback.append("Your resume is a moderate match. Improve your skills.")
    else:
        feedback.append("Your resume needs improvement for this job.")

    if missing_skills:
        feedback.append(
            "Consider learning these skills: "
            + ", ".join(missing_skills)
        )

    return "\n".join(feedback)