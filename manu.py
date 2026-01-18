import streamlit as st
import fitz  # PyMuPDF
#----------------
# ------------------ DATA (UNCHANGED CORE LOGIC) ------------------

companies = {
    "TCS": ["python", "java", "sql", "html", "css", "datastructures", "communication"],
    "INFOSYS": ["python", "java", "sql", "c", "datastructures", "cloud", "communication"],
    "WIPRO": ["java", "python", "sql", "linux", "cloud", "communication"],
    "ACCENTURE": ["python", "sql", "cloud", "datastructures", "c", "communication", "testing"],
    "GOOGLE": ["python", "java", "datastructures", "aiml", "cloud", "linux"],
    "AMAZON": ["java", "python", "datastructures", "cloud", "systemdesign"],
    "MICROSOFT": ["python", "java", "datastructures", "cloud", "systemdesign", "linux"],
    "IBM": ["python", "sql", "cloud", "linux", "testing", "communication"],
    "DELOITTE": ["sql", "python", "cloud", "c", "communication", "testing"],
    "CAPGEMINI": ["java", "python", "sql", "html", "css", "communication"]
}

skill_weights = {
    "python": 30, "java": 28, "sql": 25, "html": 10, "css": 8,
    "datastructures": 30, "communication": 10, "cloud": 25,
    "linux": 20, "testing": 12, "aiml": 22, "systemdesign": 26, "c": 20
}

# ------------------ STREAMLIT UI ------------------

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 Resume Analysis & Placement Recommendation System")

age = st.number_input("Enter your age", min_value=18, max_value=26)

if age < 18 or age > 26:
    st.error("You are not eligible for job roles based on age.")
    st.stop()
else:
    st.success("You are eligible for job roles.")

resume_text = ""

st.subheader("Upload Resume")

option = st.radio("Choose input type:", ["Enter Resume Text", "Upload PDF Resume"])

if option == "Enter Resume Text":
    resume_text = st.text_area("Paste your resume text here", height=200)

elif option == "Upload PDF Resume":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            resume_text = text
            st.success("PDF text extracted successfully.")
        except:
            st.error("Unable to read PDF.")

# ------------------ PROCESSING ------------------

if st.button("Analyze Resume"):
    if resume_text.strip() == "":
        st.warning("Please provide resume text first.")
    else:
        user_input = resume_text.lower().replace(",", " ").replace(".", " ")
        clean_resume = user_input.split()

        best_score = 0
        best_companies = []
        companies_score = {}

        for company, skills in companies.items():
            score = 0
            for s in skills:
                if " " in s:
                    if s in user_input:
                        score += skill_weights.get(s, 0)
                else:
                    if s in clean_resume:
                        score += skill_weights.get(s, 0)

            companies_score[company] = score

            if score > best_score:
                best_score = score
                best_companies = [company]
            elif score == best_score and score != 0:
                best_companies.append(company)

        if best_score == 0:
            st.error("You do not have enough skills for these companies.")
            st.write("Companies:", list(companies.keys()))
        else:
            st.subheader("Company-wise Score and Missing Skills")

            ranked_score = sorted(companies_score.items(), key=lambda x: x[1], reverse=True)

            for company, score in ranked_score:
                missing_skills = []
                for req in companies[company]:
                    if " " in req:
                        if req not in user_input:
                            missing_skills.append(req)
                    else:
                        if req not in clean_resume:
                            missing_skills.append(req)

                st.write(f"**{company}** → Score: {score}")
                st.write("Missing Skills:", ", ".join(missing_skills))
                st.write("---")

            st.success(f"Best Matching Companies: {', '.join(best_companies)}")
            st.info(f"Highest Score: {best_score}")
