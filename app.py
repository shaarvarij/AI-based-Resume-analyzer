import streamlit as st
import nltk
from pdfminer.high_level import extract_text
import docx2txt
import re
from transformers import pipeline

# Ensure the 'punkt' tokenizer is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)

# Function to extract text from DOCX
def extract_text_from_docx(docx_path):
    return docx2txt.process(docx_path)

# Load the NER model from Hugging Face
ner_model = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english", aggregation_strategy="simple")

# Function to extract relevant information from the resume using NER
def extract_info_with_ner(resume_text):
    entities = ner_model(resume_text)
    info = {"Name": "", "Contact": [], "Education": [], "Skills": [], "Experience": []}

    # Extract name (first PER entity found)
    for entity in entities:
        if entity['entity_group'] == 'PER':
            info["Name"] = entity['word']
            break

    # Extract contact info
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{10}\b|\(\d{3}\)\s*\d{3}-\d{4}|\d{3}-\d{3}-\d{4}'
    info["Contact"].extend(re.findall(email_pattern, resume_text))
    info["Contact"].extend(re.findall(phone_pattern, resume_text))

    # Parse sections
    lines = resume_text.splitlines()
    section = None
    for line in lines:
        line = line.strip()
        if not line: continue
        if "education" in line.lower():
            section = "Education"
        elif "skills" in line.lower():
            section = "Skills"
        elif "experience" in line.lower():
            section = "Experience"
        elif section and any(k in line.lower() for k in ["education", "skills", "experience"]):
            section = None
        elif section:
            info[section].append(line)
    return info

# Display info in Streamlit
def display_info(info):
    st.markdown(f"**Name:** {info['Name']}")
    if info["Contact"]:
        st.markdown("**Contact Information:**")
        for c in info["Contact"]: st.write(f"- {c}")
    if info["Education"]:
        st.markdown("**Education:**")
        for e in info["Education"]: st.write(f"- {e}")
    if info["Skills"]:
        st.markdown("**Skills:**")
        for s in info["Skills"]: st.write(f"- {s}")
    if info["Experience"]:
        st.markdown("**Experience:**")
        for x in info["Experience"]: st.write(f"- {x}")

# Skills required for job profiles (shortened here for brevity — keep full dict from your code)
skills_for_job_profiles = {
    "Frontend Developer": ["HTML", "CSS", "JavaScript", "React", "Angular", "Vue.js"],
    "Data Scientist": ["Python", "R", "Pandas", "NumPy", "Machine Learning", "SQL"],
    "Software Engineer": ["C++", "Java", "Python", "Data Structures", "Algorithms"],
    "Business Analyst": ["Business Analysis", "SQL", "JIRA", "Market Research"],
    # ... (add full dictionary from your code)
}

# Matching score
def calculate_matching_score(resume_skills, required_skills):
    rs = set(s.lower() for s in resume_skills)
    rq = set(s.lower() for s in required_skills)
    return (len(rs & rq) / len(rq)) * 100 if rq else 0

# Missing skills
def find_missing_skills(resume_skills, required_skills):
    rs = set(s.lower() for s in resume_skills)
    rq = set(s.lower() for s in required_skills)
    return [s.capitalize() for s in rq - rs]

# Best matching profile
def find_best_matching_profile(resume_skills):
    best, score = None, 0
    for job, req in skills_for_job_profiles.items():
        sc = calculate_matching_score(resume_skills, req)
        if sc > score: best, score = job, sc
    return best, score

# --- Streamlit UI ---
st.title("📄 Resume Analyzer (AI-powered)")

user_type = st.selectbox("Select User Type", ["Student/Employee", "Employer/HR"])

# Student/Employee workflow
if user_type == "Student/Employee":
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])
    if uploaded_file:
        text = extract_text_from_pdf(uploaded_file) if uploaded_file.name.endswith('.pdf') else extract_text_from_docx(uploaded_file)
        info = extract_info_with_ner(text)
        st.subheader("Resume Summary")
        display_info(info)
        resume_skills = [s.strip() for s in info["Skills"]]

        job = st.selectbox("Select Job Profile", list(skills_for_job_profiles.keys()))
        required = skills_for_job_profiles.get(job, [])
        st.subheader(f"Skills Required for {job}")
        for s in required: st.write(f"- {s}")

        score = calculate_matching_score(resume_skills, required)
        st.subheader(f"Matching Score: {score:.2f}%")
        missing = find_missing_skills(resume_skills, required)
        if missing: st.markdown("**Missing Skills:**"); [st.write(f"- {m}") for m in missing]

        best, best_score = find_best_matching_profile(resume_skills)
        st.subheader(f"Best Match: {best} ({best_score:.2f}%)")

# Employer/HR workflow
elif user_type == "Employer/HR":
    files = st.file_uploader("Upload resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
    if files:
        job_desc = st.text_area("Enter Job Description (comma-separated skills)")
        if job_desc:
            jd_skills = [s.strip() for s in job_desc.split(',')]
            results = []
            for f in files:
                text = extract_text_from_pdf(f) if f.name.endswith('.pdf') else extract_text_from_docx(f)
                info = extract_info_with_ner(text)
                score = calculate_matching_score(info["Skills"], jd_skills)
                missing = find_missing_skills(info["Skills"], jd_skills)
                results.append({"Name": info["Name"], "Score": score, "Missing": missing})
            results.sort(key=lambda x: x["Score"], reverse=True)
            st.subheader("Candidate Ranking")
            for i, r in enumerate(results, 1):
                st.markdown(f"**{i}. {r['Name']}** – {r['Score']:.2f}%")
                if r["Missing"]: st.write("Missing:", ", ".join(r["Missing"]))
