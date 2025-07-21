

# ===================== Imports and Environment Setup =====================

import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai
# --- OCR Library ---
import pytesseract

# Load environment variables
load_dotenv()

# --- Google Generative AI Client Initialization ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("Google API Key not found. Please set the GOOGLE_API_KEY environment variable.")
    st.stop()
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')



# ===================== AI Response Function =====================
def get_ai_response(input_text, image, prompt):
    """
    Get a response from the AI model.
    Args:
        input_text (str): The main prompt or question.
        image (list): List containing image data dict.
        prompt (str): Additional prompt for the model.
    Returns:
        str: AI-generated response text or None on error.
    """
    try:
        response = model.generate_content([input_text, image[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None


# ===================== Image Input Processing =====================
def input_image_details(uploaded_file):
    """
    Prepare image data for AI model input.
    Args:
        uploaded_file: Streamlit UploadedFile object.
    Returns:
        list: List containing image data dict.
    """
    if uploaded_file is not None:
        byte_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": byte_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No image file uploaded, please upload an image.")


# ===================== Streamlit App UI and Logic =====================

# --- Set up the Streamlit page (UI theme and title) ---
st.set_page_config(page_title="Multi-language Image Processor", page_icon=":camera:", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #f7f7fa;}
    .stButton>button {background-color: #4CAF50; color: white; font-weight: bold; border-radius: 6px;}
    .stExpanderHeader {font-size: 1.1em;}
    .stTextInput>div>input {border-radius: 6px;}
    .stFileUploader>div {border-radius: 6px;}
    </style>
    """, unsafe_allow_html=True)
st.title(":camera: Multi-language Image Processor")
st.caption("Analyze, translate, and ask questions about any image in any language.")

# --- Sidebar: Language Selection and About ---
with st.sidebar:
    st.header("Settings")
    predefined_languages = [
        "English", "Spanish", "French", "Arabic", "Chinese", "Urdu", "Bengali", "Other (type below)"
    ]
    language_choice = st.selectbox("Select output language", predefined_languages, index=0)
    custom_language = ""
    if language_choice == "Other (type below)":
        custom_language = st.text_input("Enter any language (e.g., German, Swahili, Japanese, etc.)", "German")
        selected_language = custom_language.strip() if custom_language.strip() else "English"
    else:
        selected_language = language_choice
    st.markdown("---")
    with st.expander("About this App"):
        st.markdown("""
        **Multi-language Image Processor**
        - Powered by Google Gemini AI
        - Supports image content analysis, translation, and Q&A in any language
        - Developed by Mohammed Kabir
        """)

# --- Instructions Section ---
with st.expander("Instructions", expanded=False):
    st.markdown("""
    1. Upload an image containing text in any language.
    2. Select the output language from the sidebar.
    3. The app will analyze, translate, and describe the image content.
    4. Ask follow-up questions about the image in the question box below.
    """)

# --- Prompt Template ---
input_prompt_template = f"""
You are an expert in understanding image content and generating descriptive text in any language.
Analyze the image and generate a detailed description, summary, and answers in the following language: {{language}}.

Instructions:
1. Analyze the image content thoroughly.
2. If the image contains text in a language other than the requested output, translate it first.
3. If the image contains text in multiple languages, translate all to the requested output language.
4. If you cannot understand or process the text, mention it.
5. If any part of the image is unclear, mention it.
6. Be precise and accurate in your analysis, translation, and answers.
"""

# --- Main Layout: Image Upload and AI Response ---
col1, col2 = st.columns([1, 2])

# --- Main Layout: Image Upload, OCR Preview, and AI Response ---
uploaded_file = st.file_uploader("Upload an image ...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    st.image(uploaded_file, caption='Uploaded Image', use_column_width=True)
    # --- OCR Preview Section ---
    with st.expander("🔍 Preview Extracted Text (OCR)"):
        try:
            image_pil = Image.open(uploaded_file)
            ocr_text = pytesseract.image_to_string(image_pil)
            if ocr_text.strip():
                st.code(ocr_text, language="text")
            else:
                st.info("No readable text detected in the image.")
        except Exception as e:
            st.warning(f"OCR extraction failed: {e}")

with col2:
    if uploaded_file is not None:
        try:
            image = input_image_details(uploaded_file)
            st.success("Image uploaded successfully! You can now ask questions about the image or view the analysis below.")
            # --- Generate AI Response for Image Description ---
            prompt = input_prompt_template.format(language=selected_language)
            response = get_ai_response(prompt, image, f"Generate a detailed description, summary, and translation in {selected_language}.")
            if response:
                st.subheader(f"AI Response in {selected_language}")
                st.write(response)
                st.download_button(
                    label="Download AI Response as Text",
                    data=response,
                    file_name="ai_image_analysis.txt",
                    mime="text/plain"
                )
        except FileNotFoundError as e:
            st.error(str(e))
    else:
        st.info("Please upload an image to begin.")

# --- Question Box Section ---
st.markdown("---")
st.subheader(":question: Ask a question about the uploaded image")
user_question = st.text_input("Type your question here:", key="user_question")
ask_button = st.button("Ask AI about the image", key="ask_button")
if ask_button:
    if uploaded_file is None:
        st.error("Please upload an image before asking a question.")
    elif not user_question:
        st.error("Please enter a question about the image.")
    else:
        with st.spinner("Analyzing image and answering your question..."):
            image_parts = input_image_details(uploaded_file)
            followup_prompt = input_prompt_template.format(language=selected_language)
            response = get_ai_response(user_question, image_parts, f"Answer the following question about the image in {selected_language}: {user_question}")
            if response:
                st.success(f"Image Analyzer's Answer in {selected_language}:")
                st.write(response)
            else:
                st.error("Failed to generate a response. Please try again.")