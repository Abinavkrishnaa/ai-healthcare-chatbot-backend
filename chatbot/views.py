import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import requests
import re

# Load API Key from environment variables
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')  # Ensure you set this in your environment

def get_yt_video(query):
    """Fetch the top YouTube video link for a given search query."""
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={YOUTUBE_API_KEY}&maxResults=1&type=video"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("items"):
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
    return None  # Return None if no video found

@csrf_exempt
def chatbot_response(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract user responses
            user_name = data.get("name", "User")
            age = data.get("age", "Unknown")
            gender = data.get("gender", "Unknown")
            symptoms = data.get("symptoms", "").strip()
            duration = data.get("duration", "Unknown")
            severity = data.get("severity", "Unknown")
            existing_conditions = data.get("existing_conditions", "None")
            medications = data.get("medications", "None")
            recent_travel = data.get("recent_travel", "No")
            contact_with_sick = data.get("contact_with_sick", "No")

            if not symptoms:
                return JsonResponse({"error": "Please provide symptoms."}, status=400)

            # Step 1: Refined Gemini Prompt
            prompt = f"""
            You are an AI medical assistant. Based on the user's details, return a JSON response **ONLY**.

            **User Details:**
            - Name: {user_name}
            - Age: {age}
            - Gender: {gender}
            - Symptoms: {symptoms}
            - Duration: {duration}
            - Severity: {severity}
            - Existing Conditions: {existing_conditions}
            - Medications: {medications}
            - Recent Travel: {recent_travel}
            - Contact with Sick Person: {contact_with_sick}

            **Strict JSON Output Format:**
            ```json
            {{
                "possible_condition": "<likely medical condition>",
                "specialist": "<specific medical specialist (e.g., Cardiologist, Neurologist, Pulmonologist, etc.)>",
                "explanation": "<brief medical explanation>",
                "youtube_query": "<best YouTube search query for this condition>"
            }}
            ```
            Ensure your response is a **valid JSON object** and does **not include General Practitioner** as a specialist.
            """

            # Step 2: Call Gemini API
            gemini_response = model.generate_content(prompt)

            chatbot_reply = gemini_response.text if gemini_response else None
            if not chatbot_reply:
                return JsonResponse({"error": "Gemini did not return a response."}, status=500)

            print("Raw Gemini Response:", chatbot_reply)  # Debugging Log

            # Step 3: Extract JSON data from Gemini's response
            try:
                chatbot_reply = re.sub(r"^```json|```$", "", chatbot_reply.strip()).strip()
                structured_response = json.loads(chatbot_reply)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid response format from Gemini."}, status=500)

            # Step 4: Fetch YouTube video for the predicted condition
            youtube_query = structured_response.get("youtube_query", "")
            youtube_video = get_yt_video(youtube_query) if youtube_query else None
            structured_response["youtube_link"] = youtube_video if youtube_video else "No video found"

            return JsonResponse(structured_response)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
