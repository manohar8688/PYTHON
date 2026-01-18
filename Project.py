import streamlit as st
import pandas as pd
import fitz

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
    "CAPGEMINI": ["java", "python", "sql", "html", "css", "communication"]}

skill_weights = {"python": 30, "java": 28, "sql": 25, "html": 10, "css": 8,
                 "datastructures": 30, "communication": 10, "cloud": 25,
                 "linux": 20, "testing": 12, "aiml": 22, "systemdesign": 26, "c": 20}

skill_aliases = {
    "python": ["py", "python3"],
    "java": ["core java", "java8"],
    "sql": ["mysql", "postgresql", "dbms"],
    "html": ["html5"],
    "css": ["css3"],
    "datastructures": ["ds", "dsa", "data structures", "data-structures"],
    "communication": ["soft skills", "communication skills"],
    "cloud": ["aws", "azure", "gcp", "cloud computing"],
    "linux": ["unix"],
    "testing": ["qa", "manual testing", "automation testing"],
    "aiml": ["ai", "ml", "ai/ml", "artificial intelligence", "machine learning"],
    "systemdesign": ["system design", "low level design", "high level design"],
    "c": ["c language"]}

Total_skill_weightage = sum(skill_weights.values())

def skill_found(skill, full_text, tokens):
    if skill in tokens:
        return True
    if skill in skill_aliases:
        for alias in skill_aliases[skill]:
            if alias in full_text:
                return True
    return False

if "candidates" not in st.session_state:
    st.session_state.candidates = []

st.set_page_config(page_title="Resume Analyzer")

if st.sidebar.button("🔄 Upload New Resume"):
    for key in ["name", "age", "resume_text", "uploaded_file", "option"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

st.title("📄Resume Analysis & Placement Recommendation System")

name = st.text_input("👤 Enter your name", key="name")
age = st.number_input("👤Enter your age", min_value=10, max_value=60, key="age")

if age < 18 or age > 26:
    st.error("❌You are not eligible for job roles based on age.")
    st.stop()
else:
    st.success("✅You are eligible for job roles.")

resume_text = ""
st.subheader("📄Upload Resume")
opts = ["📝Enter Resume Text", "📁Upload PDF Resume"]
option = st.radio("Choose input type:", opts, key="option")

if option == "📝Enter Resume Text":
    resume_text = st.text_area("Paste your resume text here", height=200, key="resume_text")

elif option == "📁Upload PDF Resume":
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key="uploaded_file")
    if uploaded_file:
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            resume_text = text
            st.success("✅PDF text extracted successfully.")
        except:
            st.error("🙅Unable to read PDF.")

if st.button("🧐Analyze Resume"):
    if resume_text.strip() == "":
        st.warning("Please provide proper resume")
    else:
        user_input = resume_text.lower().replace(",", " ").replace(".", " ")
        clean_resume = user_input.split()
        best_score = 0
        best_companies = []
        companies_score = {}

        for company, skills in companies.items():
            score = 0
            for s in skills:
                if skill_found(s, user_input, clean_resume):
                    score += skill_weights.get(s, 0)
            companies_score[company] = score

            if score > best_score:
                best_score = score
                best_companies = [company]
            elif score == best_score and score != 0:
                best_companies.append(company)

        if best_score == 0:
            st.error("😥You do not have enough skills for these companies.")
            st.write("Companies:", list(companies.keys()))
        else:
            st.subheader("Company-wise Score and Missing Skills")
            ranked_score = sorted(companies_score.items(), key=lambda x: x[1], reverse=True)

            result_data = []
            for company, score in ranked_score:
                missing_skills = []
                for req in companies[company]:
                    if not skill_found(req, user_input, clean_resume):
                        missing_skills.append(req)
                result_data.append({"Company": company, "Score": score, "Missing skills": ",".join(missing_skills)})

            df = pd.DataFrame(result_data)
            st.dataframe(df, use_container_width=True)

            st.success(f"🏆 Best Matching Companies: {', '.join(best_companies)}")
            st.info(f"📊 Highest Score: {best_score}")

            strength = (best_score / Total_skill_weightage * 100)
            st.write("💪Resume strength : ", strength, "%")

            if name.strip() != "":
                st.session_state.candidates.append({"Name": name, "Best Company": ", ".join(best_companies), "Score": best_score})
                st.success("Candidate saved for comparison")
            else:
                st.warning("Enter your name to save result for comparison")

st.markdown("---")

if st.button("📊 Compare All Candidates"):
    if len(st.session_state.candidates) == 0:
        st.warning("No candidates added yet.")
    else:
        df_compare = pd.DataFrame(st.session_state.candidates)
        st.subheader("All Candidates Comparison")
        st.dataframe(df_compare, use_container_width=True)

        max_score = df_compare["Score"].max()
        winners = df_compare[df_compare["Score"] == max_score]["Name"].tolist()
        st.success(f"🏆 Winner(s): {', '.join(winners)} with score {max_score}")
if st.button("🧹 Clear All Data"):
    if st.checkbox("⚠️ Confirm: This will delete ALL candidate data"):
        st.session_state.clear()
        st.rerun()
