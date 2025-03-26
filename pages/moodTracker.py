import os
import requests
from io import BytesIO
import json
import streamlit as st
import openai
import azure.cognitiveservices.speech as speechsdk
from azure.ai.textanalytics import TextAnalyticsClient
from azure.cognitiveservices.vision.face import FaceClient
from azure.core.credentials import AzureKeyCredential
from msrest.authentication import CognitiveServicesCredentials

# ------------------------- AZURE CONFIGURATION -------------------------
AZURE_TEXT_KEY = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
AZURE_TEXT_ENDPOINT = "https://ai-aihackthonhub282549186415.cognitiveservices.azure.com/"

AZURE_SPEECH_KEY = os.environ.get("SPEECH_KEY")
AZURE_SPEECH_REGION = os.environ.get("SPEECH_REGION")

# Debug prints
print(f"SPEECH_KEY: {AZURE_SPEECH_KEY}, SPEECH_REGION: {AZURE_SPEECH_REGION}")

FACE_ENDPOINT = "https://api.luxand.cloud/photo/emotions"
FACE_API_TOKEN = "d818b857376246968518f98c0f3dcf1c"

AZURE_OPENAI_KEY = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
AZURE_OPENAI_ENDPOINT = "https://ai-aihackthonhub282549186415.openai.azure.com/"
AZURE_GPT4_DEPLOYMENT = "gpt-4"
AZURE_GPT4_API_VERSION = "2025-01-01-preview"

# ------------------------- TEXT & SPEECH CLIENT SETUP -------------------------
try:
    text_client = TextAnalyticsClient(
        endpoint=AZURE_TEXT_ENDPOINT,
        credential=AzureKeyCredential(AZURE_TEXT_KEY)
    )
except Exception as e:
    st.error(f"⚠ Error initializing Azure Text client: {e}")

# OpenAI client setup
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_GPT4_API_VERSION

# ------------------------- STREAMLIT UI -------------------------
st.title("🧠 AI-Powered Mental Health Analyzer")
st.write("Analyze emotional sentiment from text, voice, and images.")

# Variables to store analysis results
sentiment = "Unknown"
speech_sentiment = "Unknown"
gpt4_emotion = ""  # Will hold the emotion derived from GPT‑4's response

# ------------------------- TEXT SENTIMENT ANALYSIS -------------------------
st.header("📄 Text Sentiment Analysis")
text_input = st.text_area("Enter your thoughts or feelings:")

if st.button("Analyze Text"):
    if text_input.strip():
        try:
            response = text_client.analyze_sentiment([text_input])
            if response and response[0]:
                sentiment = response[0].sentiment
                st.write(f"Sentiment: {sentiment.capitalize()}")
            else:
                st.warning("Unable to analyze sentiment.")
        except Exception as e:
            st.error(f"⚠ Error in text sentiment analysis: {e}")
    else:
        st.warning("Please enter some text.")

# ------------------------- SPEECH SENTIMENT ANALYSIS -------------------------
st.header("🎤 Speech Sentiment Analysis")

languages = ["en-US", "hi-IN", "fr-FR", "es-ES", "de-DE", "it-IT", "pt-PT", "zh-CN", "ja-JP", "ko-KR"]
language_choice = st.selectbox("Select Language", languages)

if st.button("Record & Analyze Speech"):
    try:
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = language_choice

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        st.write("🎙 Recording... Please speak now.")
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
            recognized_text = speech_recognition_result.text
            st.success(f"Recognized: {recognized_text}")

            # Analyze sentiment of recognized speech
            response = text_client.analyze_sentiment([recognized_text])
            if response and response[0]:
                speech_sentiment = response[0].sentiment
                st.write(f"Speech Sentiment: {speech_sentiment.capitalize()}")
            else:
                st.warning("Unable to analyze speech sentiment.")
        elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
            st.warning(f"No speech recognized: {speech_recognition_result.no_match_details}")
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            st.error(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancellation_details.error_details}")
                st.error("Check speech resource key & region values.")
    except Exception as e:
        st.error(f"⚠ Error in speech analysis: {e}")

# ------------------------- IMAGE EMOTION (VISION + GPT-4) -------------------------
st.header("🔍 Image Emotion Analysis via GPT‑4")

AZURE_VISION_KEY = os.getenv("VISION_KEY")
AZURE_VISION_ENDPOINT = os.getenv("VISION_ENDPOINT")

if not AZURE_VISION_KEY or not AZURE_VISION_ENDPOINT:
    st.error("🚨 Azure Vision API credentials are missing! Please set VISION_KEY and VISION_ENDPOINT.")
    st.stop()

AZURE_VISION_ENDPOINT = AZURE_VISION_ENDPOINT.rstrip("/")

image_file = st.file_uploader("📤 Upload an image for analysis:", type=["jpg", "jpeg", "png"])

if image_file is not None:
    # Display the uploaded image
    image_bytes = image_file.read()
    st.image(image_file, caption="📷 Uploaded Image", use_container_width=True)

    # 1. Vision API (v3.2/analyze) to get a description
    vision_api_url = f"{AZURE_VISION_ENDPOINT}/vision/v3.2/analyze"
    vision_params = {
        "visualFeatures": "Faces,Description",
        "language": "en"
    }
    vision_headers = {
        "Ocp-Apim-Subscription-Key": AZURE_VISION_KEY,
        "Content-Type": "application/octet-stream"
    }

    try:
        vision_response = requests.post(vision_api_url, headers=vision_headers, params=vision_params, data=image_bytes)
        vision_response.raise_for_status()
        vision_result = vision_response.json()

        st.subheader("📜 Vision API JSON Response:")
        st.json(vision_result)

        # Extract description from Vision API
        description_text = ""
        if ("description" in vision_result 
            and "captions" in vision_result["description"] 
            and len(vision_result["description"]["captions"]) > 0):
            description_text = vision_result["description"]["captions"][0]["text"]
        
        if not description_text:
            description_text = "No description available."
        st.write("Extracted Description:", description_text)

        # 2. GPT-4 for emotion analysis
        gpt4_url = (
            f"{AZURE_OPENAI_ENDPOINT}/openai/deployments/{AZURE_GPT4_DEPLOYMENT}/chat/completions"
            f"?api-version={AZURE_GPT4_API_VERSION}"
        )
        gpt_headers = {
            "Content-Type": "application/json",
            "api-key": AZURE_OPENAI_KEY
        }
        prompt = (
            f"Analyze this image description and provide the main emotion in one word: {description_text}"
        )
        gpt_data = {
            "messages": [
                {"role": "system", "content": "You are an expert in analyzing emotions in images."},
                {"role": "user", "content": prompt}
            ]
        }

        gpt_response = requests.post(gpt4_url, headers=gpt_headers, json=gpt_data)
        gpt_response.raise_for_status()
        gpt_result = gpt_response.json()

        st.subheader("💬 GPT‑4 Emotion Analysis:")
        if "choices" in gpt_result and len(gpt_result["choices"]) > 0:
            gpt4_text = gpt_result["choices"][0]["message"]["content"]
            st.write("GPT‑4 Raw Answer:", gpt4_text)

            # A simple approach to parse the single-word emotion from GPT-4's text
            gpt4_text_lower = gpt4_text.lower()

            # Basic keyword matching (improve as needed)
            if any(word in gpt4_text_lower for word in ["happy", "happiness", "joy"]):
                gpt4_emotion = "happiness"
            elif any(word in gpt4_text_lower for word in ["sad", "sadness", "sorrow", "depressed"]):
                gpt4_emotion = "sadness"
            elif any(word in gpt4_text_lower for word in ["anger", "angry"]):
                gpt4_emotion = "anger"
            elif any(word in gpt4_text_lower for word in ["fear", "afraid", "scared"]):
                gpt4_emotion = "fear"
            else:
                gpt4_emotion = "neutral"

            st.success(f"Parsed Emotion: {gpt4_emotion.capitalize()}")
        else:
            st.error("No valid answer from GPT‑4.")
            gpt4_emotion = "neutral"
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 API Request Failed: {e}")
        gpt4_emotion = "neutral"
else:
    # If no image uploaded, default
    gpt4_emotion = "neutral"

# ------------------------- MOOD-BASED ARTICLE RECOMMENDATIONS -------------------------
st.header("📚 Recommended Articles & Resources")

# Convert inputs to lower-case strings for comparison
text_sent_lower = sentiment.lower() if sentiment else ""
speech_sent_lower = speech_sentiment.lower() if speech_sentiment else ""
face_emotion_lower = gpt4_emotion.lower() if gpt4_emotion else ""

if ("negative" in [text_sent_lower, speech_sent_lower]) or (face_emotion_lower in ["anger", "sadness", "fear", "disgust"]):
    mood_category = "negative"
elif ("positive" in [text_sent_lower, speech_sent_lower]) or (face_emotion_lower == "happiness"):
    mood_category = "positive"
else:
    mood_category = "neutral"

recommendations = {
    "negative": [
        {"title": "10 Effective Ways to Reduce Stress", "url": "https://www.drkapilsharma.in/blog/10-simple-ways-to-relieve-stress-and-anxiety/"},
        {"title": "Meditation Techniques for Anxiety", "url": "https://www.verywellmind.com/anti-anxiety-medications-2330663"},
        {"title": "How to Manage Negative Thoughts", "url": "https://positivepsychology.com/thought-stopping-techniques/"},
        {"title": "Coping Strategies for Depression", "url": "https://www.verywellhealth.com/coping-skills-for-depression-8426424"},
        {"title": "Mindfulness for Stress Reduction", "url": "https://positivepsychology.com/mindfulness-based-stress-reduction-mbsr/"}
    ],
    "neutral": [
        {"title": "Daily Habits for Maintaining a Balanced Life", "url": "https://curiousmindmagazine.com/10-healthy-habits-for-a-balanced-lifestyle/"},
        {"title": "Mindfulness: The Key to Everyday Calm", "url": "https://spiritualityshepherd.com/the-art-of-mindfulness-6-strategies-for-everyday-calm/"},
        {"title": "Simple Self-Care Tips for a Healthy Mind", "url": "https://mind.help/articles/self-care-habits/"},
        {"title": "Improving Your Mental Well-being", "url": "https://www.nhs.uk/every-mind-matters/mental-wellbeing-tips/top-tips-to-improve-your-mental-wellbeing/"}
    ],
    "positive": [
        {"title": "How to Sustain a Positive Mindset", "url": "https://www.psychologytoday.com/us/blog/click-here-for-happiness/202105/9-ways-to-cultivate-a-positive-mindset"},
        {"title": "Embrace Happiness: Tips for a Fulfilling Life", "url": "https://manibelde.medium.com/embracing-happiness-7-simple-tips-to-create-a-life-full-of-joy-and-contentment-9ae66d7f1341"},
        {"title": "Boost Your Mood with These Healthy Habits", "url": "https://www.powerofpositivity.com/psychologists-advice-10-activities-to-boost-mood-10-mins-or-less/"},
        {"title": "The Benefits of Gratitude for a Happy Life", "url": "https://www.happierhuman.com/benefits-of-gratitude/#:~:text=Gratitude%20is%20a%20powerful%20emotion%20that%20can%20bring"}
    ]
}

recos = recommendations.get(mood_category, recommendations["neutral"])

st.write(f"Based on your overall mood ({mood_category.capitalize()}), here are some article recommendations:")
for article in recos:
    st.markdown(f"- [{article['title']}]({article['url']})")