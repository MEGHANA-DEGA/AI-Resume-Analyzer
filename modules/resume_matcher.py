
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_match_score(resume_text, job_description):

    # Convert inputs into strings
    if isinstance(resume_text, list):
        resume_text = " ".join(str(skill) for skill in resume_text)

    if isinstance(job_description, list):
        job_description = " ".join(
            str(skill) for skill in job_description
        )

    resume_text = str(resume_text).strip()
    job_description = str(job_description).strip()

    if not resume_text or not job_description:
        return 0.0

    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    return round(similarity * 100, 2)
