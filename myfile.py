# app.py
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from typing import List
from pydantic import BaseModel, Field

from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain_core.tools import tool

from gmail_draft import create_draft


# ---------------- Pydantic models ----------------

class Lead(BaseModel):
    name: str = Field(description="Person name")
    email: str = Field(description="Email of person")
    business_type: str = Field(description="Business type")


class Leads(BaseModel):
    leads: List[Lead]


# ---------------- LLM setup ----------------

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

structured_llm = llm.with_structured_output(Leads)


# ---------------- Tool ----------------

@tool
def create_mail_draft(to: str, subject: str, body: str):
    """
    Create email draft.

    Args:
        to: Receiver email
        subject: Email subject
        body: Email body
    """
    return create_draft(to, subject, body)


agent = create_agent(
    model=llm,
    tools=[create_mail_draft],
    system_prompt="""
    You are an employee at an AI automation agency.
    For every lead, create a personalized email draft according to their business type.
    Write a details email for there business the services that we can provide them according to there business and much more details a Employeee
    """
)


# ---------------- Main logic functions ----------------

def save_uploaded_file_as_leads_txt(uploaded_file):
    content = uploaded_file.read().decode("utf-8")

    with open("leads.txt", "w", encoding="utf-8") as file:
        file.write(content)

    return content


def extract_leads_from_file():
    with open("leads.txt", "r", encoding="utf-8") as file:
        data = file.read()

    clean_data = structured_llm.invoke(
        f"""
        Extract all leads from this text.

        Text:
        {data}
        """
    )

    return clean_data


def create_email_drafts(clean_data):
    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": str(clean_data)
            }
        ]
    })

    return response


# ---------------- Streamlit UI ----------------

st.set_page_config(page_title="AI Lead Email  Agent", page_icon="📩")

st.title("📩 AI Lead Email  Agent")
st.write("Upload a `.txt` file. ")

prompt = st.chat_input(
    "Upload your  file here...",
    accept_file=True,
    file_type=["txt"]
)

if prompt:
    if len(prompt.files) == 0:
        st.warning("Please upload a .txt file.")
    else:
        uploaded_file = prompt.files[0]

        with st.chat_message("user"):
            st.write(f"Uploaded file: `{uploaded_file.name}`")

        with st.spinner("Working"):
            save_uploaded_file_as_leads_txt(uploaded_file)

        st.success("Thinking")

        with st.spinner("Extracting clean leads ..."):
            clean_data = extract_leads_from_file()

        st.subheader("Clean Leads Found")

        for lead in clean_data.leads:
            st.write(f"**Name:** {lead.name}")
            st.write(f"**Email:** {lead.email}")
            st.write(f"**Business Type:** {lead.business_type}")
            st.divider()

        with st.spinner("Sending mail"):
            create_email_drafts(clean_data)

        st.success("✅ Email send successfully!")