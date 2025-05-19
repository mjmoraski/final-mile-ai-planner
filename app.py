import streamlit as st
import pandas as pd
import openai

st.title("🗺️ Final Mile AI Planner")

uploaded_file = st.file_uploader("Upload your delivery data CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📦 Delivery Data", df)

    constraints = st.text_area("Constraints", 
        "Max 5 deliveries per route\nPrioritize 'High' priority deliveries first\nStay within time windows")

    if st.button("Generate Route Plan with GenAI"):
        prompt = f"""You are a logistics route planner. Based on the delivery data and constraints below, suggest an efficient route and explain why.

Constraints:
{constraints}

Delivery Data:
{df.to_csv(index=False)}
"""

        openai.api_key = st.secrets["OPENAI_API_KEY"]  # Add your API key in .streamlit/secrets.toml

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4
        )

        st.subheader("🧠 AI-Suggested Route Plan")
        st.write(response['choices'][0]['message']['content'])
