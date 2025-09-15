# 📄 Resume Analyzer (AI-powered with Streamlit & Transformers)

This project is a **Resume Analyzer App** built with **Streamlit, Hugging Face Transformers, and NLP techniques**.  
It extracts key details (name, contact, education, skills, experience) from resumes, and matches them with **job profiles** or a **job description**.  

---

## 📌 Features  

- Extracts information from **PDF & DOCX resumes**  
- Uses **Named Entity Recognition (NER)** to identify names, skills, etc.  
- Matches candidate skills with predefined **job profiles** (e.g., Data Scientist, Frontend Dev, Product Manager)  
- Allows **Employers/HR** to upload multiple resumes and compare candidates against a **job description**  
- Calculates **matching score** (%) and lists **missing skills**  

---

## ⚙️ Tech Stack  

- **Python 3.8+**  
- **Streamlit** – Web app framework  
- **nltk** – Tokenization  
- **pdfminer.six** – PDF text extraction  
- **docx2txt** – DOCX parsing  
- **Hugging Face Transformers** – NER model (`bert-large-cased-finetuned-conll03-english`)  
- **Regex** – Contact info extraction  

---



