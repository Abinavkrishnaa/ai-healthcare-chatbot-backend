from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
User = get_user_model()

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chatbot_response(request):
    user = request.user  
    message = request.data.get("message")

    # Get user details
    user_data = {
        "age": user.age,
        "gender": user.gender,
        "medical_history": user.medical_history,
        "medications": user.medications,
    }

    response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
        f"""
        User Details:
        - Age: {user_data['age']}
        - Gender: {user_data['gender']}
        - Medical History: {user_data['medical_history']}
        - Medications: {user_data['medications']}
        
        Message from user: {message}

        Your Task: Predict the possible disease, suggest a specialist, and provide a YouTube link about the condition.
        """
    )

    ai_response = response.text

    return Response({"response": ai_response})