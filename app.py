import streamlit as st
import os
from PIL import Image
from streamlit import session_state as state
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
# Initialize the Google Generative AI client
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Using 'gemini-1.5-flash' for image generation and processing    
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_response(input, image, prompt):
    """Get a response from the AI model."""
    try:
        response = model.generate_content([input, image[0], prompt])
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None
    
# def input_image_details():
#     """Get image input from the user."""
#     st.subheader("Upload an Image")
#     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
#     if uploaded_file is not None:
#         image = Image.open(uploaded_file)
#         st.image(image, caption='Uploaded Image.', use_column_width=True)
#         return [uploaded_file], image
#     else:
#         st.warning("Please upload an image.")
#         return [], None

def input_image_details(uploaded_file):
    """Get image input from the user."""
    # st.subheader("Upload an Image")
    # if uploaded_file is None:
    #     uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Read the uploaded file as bytes
        byte_data = uploaded_file.getvalue()
        # Prepare the image data and MIME type for AI model input
        image_parts = [
            {
            "mime_type": uploaded_file.type,
            "data": byte_data
            }
        ]

        return image_parts
    else:
        raise FileNotFoundError("No image file uploaded, please upload an image.")

# Application Initialization
st.set_page_config(page_title="Multi-language Image Processor", page_icon=":camera:", layout="wide")
st.title("Multi-language Image Processor")

input_prompt = """
You are an expert in understanding image content and generating descriptive text 
in multiple languages including English, Spanish, French, Arabic, Chinese, Urdu and Bengali.
We will provide you with an image which may be in any other language. 
you will analyze the image and generate a detailed description of the image in the specified language.
you will also provide a summary of the image content in the specified language.
you will also answer any questions related to the image content in the specified language.

Important Instructions:
1. Analyze the image content thoroughly.
2. Regardless of the language in which the image is written,
   generate the description, summary, and answers in the English.
3. If the image contains text in a language other than English,
   translate the text to English before generating the description and summary.
4. Be precise and accurate in your analysis, translation, and answers.
5. if the image contains text in multiple languages,
   translate all the text to English before generating the description and summary.
6. If the image contains text in a language that you do not understand,
   please mention that you are unable to understand the text in the image.
7. If the image contains text in a language that you do not support,
   please mention that you are unable to process the text in the image.
8. If any part of the image is not clear or is not visible,
   please mention that the part is not clear or not visible.

Now, please analyze the image and generate a detailed description, summary, 
and answers to any questions related to the image content in English.

"""

Uploaded_file = st.file_uploader("Upload an image ...", type=["jpg", "jpeg", "png"])
if Uploaded_file is not None:
    try:
        image = input_image_details(Uploaded_file)
        if image:
            st.image(Uploaded_file, caption='Uploaded Image.', use_column_width=True)
            st.write("Image uploaded successfully.")
            
            # Get AI response
            response = get_ai_response(input_prompt, image, "Generate a detailed description of the image in English.")
            if response:
                st.subheader("AI Response")
                st.write(response)
    except FileNotFoundError as e:
        st.error(str(e))



# --- Question Box Section ---
with st.expander("Ask a question about the uploaded image"):
    user_question = st.text_input("Type your question here:", key="user_question")
    ask_button = st.button("Ask AI about the image", key="ask_button")
    if ask_button:
        if Uploaded_file is None:
            st.error("Please upload an image before asking a question.")
        elif not user_question:
            st.error("Please enter a question about the image.")
        else:
            with st.spinner("Analyzing image and answering your question..."):
                image_parts = input_image_details(Uploaded_file)
                # Only answer the user's question based on the image analysis
                response = get_ai_response(user_question, image_parts, f"Answer the following question about the image: {user_question}")
                if response:
                    st.subheader("Image Analyzer's Answer to Your Question")
                    st.write(response)
                    st.info("You can ask another question about the same image.")
                else:
                    st.error("Failed to generate a response. Please try again.")