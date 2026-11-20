"""Simple Streamlit chat UI with a human approval step."""
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import run_agent
from approval import record_decision

st.set_page_config(page_title="Inventory Rescue Agent", page_icon="📦", layout="centered")
st.title("📦 Inventory Rescue Agent")
st.caption("Ask about inventory risk. The agent reads inventory.csv from object storage and proposes actions.")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_recommendation" not in st.session_state:
    st.session_state.pending_recommendation = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Example: Find stores at risk of stocking out of P100 and suggest transfers.")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking inventory and generating recommendations..."):
            try:
                answer = run_agent(prompt)
            except Exception as exc:
                answer = f"Sorry, I couldn't complete the request: `{exc}`"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    if not answer.startswith("Sorry,"):
        st.session_state.pending_recommendation = answer

if st.session_state.pending_recommendation:
    st.divider()
    st.subheader("Review recommendation")
    st.markdown(st.session_state.pending_recommendation)
    st.warning("Approval records the decision only. It does not execute an inventory transfer.")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve recommendation", type="primary", use_container_width=True):
            try:
                key = record_decision(st.session_state.pending_recommendation, "approved")
                st.success(f"Approval saved to object storage: `{key}`")
                st.session_state.pending_recommendation = None
            except Exception as exc:
                st.error(f"Could not save approval: {exc}")

    with col2:
        if st.button("Reject recommendation", use_container_width=True):
            try:
                key = record_decision(st.session_state.pending_recommendation, "rejected")
                st.info(f"Rejection saved to object storage: `{key}`")
                st.session_state.pending_recommendation = None
            except Exception as exc:
                st.error(f"Could not save decision: {exc}")
