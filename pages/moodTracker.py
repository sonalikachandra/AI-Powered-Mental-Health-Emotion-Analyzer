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
# from dotenv import load_dotenv

# load_dotenv()

# ------------------------- AZURE CONFIGURATION -------------------------
# (Replace the hardcoded values with secure methods later)
AZURE_TEXT_KEY = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
AZURE_TEXT_ENDPOINT = "https://ai-aihackthonhub282549186415.cognitiveservices.azure.com/"

# Speech credentials from environment variables (matching the tutorial snippet)
AZURE_SPEECH_KEY = os.environ.get("SPEECH_KEY")
AZURE_SPEECH_REGION = os.environ.get("SPEECH_REGION")

FACE_ENDPOINT = "https://api.luxand.cloud/photo/emotions"
FACE_API_TOKEN = "d818b857376246968518f98c0f3dcf1c"

AZURE_OPENAI_KEY = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
AZURE_OPENAI_ENDPOINT = "https://ai-aihackthonhub282549186415.openai.azure.com/"
AZURE_GPT4_DEPLOYMENT = "gpt-4"
AZURE_GPT4_API_VERSION = "2025-01-01-preview"

# ------------------------- AZURE CLIENTS -------------------------
try:
    text_client = TextAnalyticsClient(
        endpoint=AZURE_TEXT_ENDPOINT,
        credential=AzureKeyCredential(AZURE_TEXT_KEY)
    )
    
except Exception as e:
    st.error(f"⚠ Error initializing Azure clients: {e}")

# ------------------------- OPENAI CLIENT SETUP -------------------------
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
detected_emotion = "Unknown"

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

# Dropdown for selecting language
languages = ["en-US", "hi-IN", "fr-FR", "es-ES", "de-DE", "it-IT", "pt-PT", "zh-CN", "ja-JP", "ko-KR"]
language_choice = st.selectbox("Select Language", languages)

if st.button("Record & Analyze Speech"):
    try:
        # 1. Initialize speech config with key and region
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_SPEECH_KEY,
            region=AZURE_SPEECH_REGION
        )
        
        # Set selected language for speech recognition
        speech_config.speech_recognition_language = language_choice

        # 2. Use the default microphone
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

        # 3. Create a SpeechRecognizer
        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        st.write("🎙 Recording... Please speak now.")
        # 4. Recognize speech once
        speech_recognition_result = speech_recognizer.recognize_once_async().get()

        # 5. Handle results
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
            st.warning(f"No speech could be recognized: {speech_recognition_result.no_match_details}")
        elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_recognition_result.cancellation_details
            st.error(f"Speech Recognition canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                st.error(f"Error details: {cancellation_details.error_details}")
                st.error("Did you set the speech resource key and region values?")
    except Exception as e:
        st.error(f"⚠ Error in speech analysis: {e}")

# ------------------------- IMAGE SENTIMENT ANALYSIS -------------------------

st.header("📸 Facial Emotion Detection")
image_file = st.file_uploader("Upload an image (Face Analysis):", type=["jpg", "png", "jpeg"])

if image_file is not None:
        # Read image bytes from the uploader.
        headers = {"token": FACE_API_TOKEN}
        image_bytes = image_file.read()
        image_stream = BytesIO(image_bytes)
        files = {"photo": image_stream}
        
        try:
            response = requests.post(FACE_ENDPOINT, headers=headers, files=files)
            result = json.loads(response.text)

            # st.write("API Response:")
            # st.json(result)
            
            if response.status_code == 200 and "faces" in result and len(result["faces"]) > 0:
                # Process the first detected face.
                emotions = result["faces"][0]["emotion"]
        
                # Display the emotions in Streamlit
                st.subheader("🎭 Detected Emotions:")
                for emotion, score in emotions.items():
                    st.write(f"{emotion.capitalize()}:** {score:.3f}")

                # # Highlight the dominant emotion
                dominant_emotion = result["faces"][0]["dominant_emotion"]
                st.success(f"Dominant Emotion: {dominant_emotion.capitalize()} ({emotions[dominant_emotion]:.3f})")
            else:
                st.warning("⚠ No face detected. Please try another image.")
        except Exception as e:
            st.error(f"⚠ Error in face analysis: {e}")
# ------------------------- ADDITIONAL FEATURE: MOOD-BASED ARTICLE RECOMMENDATIONS -------------------------
# ------------------------- ADDITIONAL FEATURE: MOOD-BASED ARTICLE RECOMMENDATIONS -------------------------
st.header("📚 Recommended Articles & Resources")

# Revised mood determination logic:
# Convert inputs to lower-case strings for comparison.
text_sent = sentiment.lower() if sentiment else ""
speech_sent = speech_sentiment.lower() if speech_sentiment else ""
face_emotion = detected_emotion.lower() if detected_emotion else ""

if ("negative" in [text_sent, speech_sent]) or (face_emotion in ["anger", "sadness", "fear", "disgust"]):
    mood_category = "negative"
elif ("positive" in [text_sent, speech_sent]) or (face_emotion == "happiness"):
    mood_category = "positive"
else:
    mood_category = "neutral"

# Define sample article recommendations for each mood category.
recommendations = {
    "negative": [
        {"title": "10 Effective Ways to Reduce Stress", "url": "https://www.drkapilsharma.in/blog/10-simple-ways-to-relieve-stress-and-anxiety/"},
        {"title": "Meditation Techniques for Anxiety", "url": "https://www.verywellmind.com/anti-anxiety-medications-2330663"},
        {"title": "How to Manage Negative Thoughts", "url": "https://r.search.yahoo.com/_ylt=AwrKEkbyNuNn8wEA9S67HAx.;_ylu=Y29sbwNzZzMEcG9zAzIEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153587/RO=10/RU=https%3a%2f%2fpositivepsychology.com%2fthought-stopping-techniques%2f/RK=2/RS=sNz1irKXxWLzEqoo4GuE3qqvJCs-"},
        {"title": "Coping Strategies for Depression", "url": "https://r.search.yahoo.com/_ylt=Awrx.uLRNuNnxQIApRO7HAx.;_ylu=Y29sbwNzZzMEcG9zAzIEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153553/RO=10/RU=https%3a%2f%2fwww.verywellhealth.com%2fcoping-skills-for-depression-8426424/RK=2/RS=WSJfBkJ_xT8GoGq1IATpGQs_cGk-"},
        {"title": "Mindfulness for Stress Reduction", "url": "https://r.search.yahoo.com/_ylt=AwrPpQNgNeNnBQIAn2W7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153185/RO=10/RU=https%3a%2f%2fpositivepsychology.com%2fmindfulness-based-stress-reduction-mbsr%2f/RK=2/RS=6uHREauKcmRsBnRg5qk4oiW_nNI-"}
    ],
    "neutral": [
        {"title": "Daily Habits for Maintaining a Balanced Life", "url": "https://r.search.yahoo.com/_ylt=Awrx.uKNNeNntQIAH6S7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153229/RO=10/RU=https%3a%2f%2fcuriousmindmagazine.com%2f10-healthy-habits-for-a-balanced-lifestyle%2f/RK=2/RS=7oFXNDh4HDOT1CvYJVLzRLbfejc-"},
        {"title": "Mindfulness: The Key to Everyday Calm", "url": "https://r.search.yahoo.com/_ylt=Awr1SbSkNeNnCAIAmBO7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153252/RO=10/RU=https%3a%2f%2fspiritualityshepherd.com%2fthe-art-of-mindfulness-6-strategies-for-everyday-calm%2f/RK=2/RS=6UE6dfxXxoeFUF4n.Fn.AmriZB4-"},
        {"title": "Simple Self-Care Tips for a Healthy Mind", "url": "https://r.search.yahoo.com/_ylt=AwrKA27DNeNnqQIAeL.7HAx.;_ylu=Y29sbwNzZzMEcG9zAzIEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153283/RO=10/RU=https%3a%2f%2fmind.help%2farticles%2fself-care-habits%2f/RK=2/RS=T2J2JvFKqLW1gJiSqQDqPwlZgac-"},
        {"title": "Improving Your Mental Well-being", "url": "https://r.search.yahoo.com/_ylt=Awr1Rf3dNeNnUQIA9wO7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153309/RO=10/RU=https%3a%2f%2fwww.nhs.uk%2fevery-mind-matters%2fmental-wellbeing-tips%2ftop-tips-to-improve-your-mental-wellbeing%2f/RK=2/RS=X3nE0WD_UvjB1WeGi01AKfjVoNU-"}
    ],
    "positive": [
        {"title": "How to Sustain a Positive Mindset", "url": "https://r.search.yahoo.com/_ylt=AwrKB5cJNuNnIAIAd0K7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153354/RO=10/RU=https%3a%2f%2fwww.psychologytoday.com%2fus%2fblog%2fclick-here-for-happiness%2f202105%2f9-ways-to-cultivate-a-positive-mindset/RK=2/RS=YE2h5zlA182BuOoT7wbYyIXafl8-"},
        {"title": "Embrace Happiness: Tips for a Fulfilling Life", "url": "https://r.search.yahoo.com/_ylt=Awrx.uIqNuNn2QIAuN67HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153386/RO=10/RU=https%3a%2f%2fmanibelde.medium.com%2fembracing-happiness-7-simple-tips-to-create-a-life-full-of-joy-and-contentment-9ae66d7f1341/RK=2/RS=MgKI9UWSv.B0zeWbeeIcHnuM9fI-"},
        {"title": "Boost Your Mood with These Healthy Habits", "url": "https://r.search.yahoo.com/_ylt=AwrPqmxKNuNneAIAX0a7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Ny/RV=2/RE=1744153419/RO=10/RU=https%3a%2f%2fwww.powerofpositivity.com%2fpsychologists-advice-10-activities-to-boost-mood-10-mins-or-less%2f/RK=2/RS=.6qCJVicPynxTJkoImKlS_dlbKg-"},
        {"title": "The Benefits of Gratitude for a Happy Life", "url": "https://r.search.yahoo.com/_ylt=AwrKDrZsNuNnIwIAHye7HAx.;_ylu=Y29sbwNzZzMEcG9zAzEEdnRpZAMEc2VjA3Nj/RV=2/RE=1744153452/RO=10/RU=https%3a%2f%2fwww.happierhuman.com%2fbenefits-of-gratitude%2f%23%3a~%3atext%3dGratitude%2520is%2520a%2520powerful%2520emotion%2520that%2520can%2520bring%2cgreater%2520mental%2520well-being%252C%2520higher%2520self-esteem%252C%2520and%2520life%2520satisfaction./RK=2/RS=I2cyo5iQfOYAt9_GxuRqekLTTZE-"}
    ]
}

# Get recommendations based on the mood category
recos = recommendations.get(mood_category, recommendations["neutral"])

st.write(f"Based on your overall mood ({mood_category.capitalize()}), here are some article recommendations:")
for article in recos:
    st.markdown(f"- [{article['title']}]({article['url']})")