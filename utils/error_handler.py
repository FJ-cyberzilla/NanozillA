import streamlit as st
from google.genai.errors import APIError


def handle_api_error(error: APIError):
    """Handle Gemini API errors with user-friendly messages"""
    error_message = str(error)

    if "API key not valid" in error_message or "PERMISSION_DENIED" in error_message:
        st.error("🔐 **Authentication Error**: Please check your API key in the .env file")
        st.code("Status: 403 PERMISSION_DENIED")

    elif "INVALID_ARGUMENT" in error_message:
        st.error("📝 **Invalid Request**: Please check your prompt or uploaded image")
        st.code("Status: 400 INVALID_ARGUMENT")

    elif "RESOURCE_EXHAUSTED" in error_message:
        st.warning("⏳ **Quota Exceeded**: You've reached your usage limit. Please try again later.")
        st.code("Status: 429 RESOURCE_EXHAUSTED")

    elif "NOT_FOUND" in error_message:
        st.error("🔍 **Model Not Found**: The requested model is unavailable")
        st.code("Status: 404 NOT_FOUND")

    elif "INTERNAL" in error_message or "UNAVAILABLE" in error_message:
        st.warning("🛠️ **Service Temporarily Unavailable**: Please try again in a few moments")
        st.code("Status: 500/503 Service Error")

    else:
        st.error("❌ **API Error**: An unexpected error occurred")
        st.code(f"Error: {error_message[:200]}...")
