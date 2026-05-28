from flask import Flask, render_template, request

import os
import PyPDF2
import google.generativeai as genai


app = Flask(__name__)


# Gemini API setup

genai.configure(
    api_key=""
)

model = genai.GenerativeModel(
    "models/gemini-2.5-flash-lite"
)


# Upload folder setup

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# Create uploads folder

if not os.path.exists(UPLOAD_FOLDER):

    os.makedirs(UPLOAD_FOLDER)


# Global variables

analysis_result = ""

roadmap_result = ""

interview_result = ""


# Home page

@app.route("/")

def home():

    return render_template("home.html")


# Analyze resume

@app.route(
    "/analyze",
    methods=["POST"]
)

def analyze_resume():

    global analysis_result
    global roadmap_result
    global interview_result


    # Get uploaded file

    file = request.files["resume"]


    # Get job role

    job_role = request.form["job_role"]


    # Check if file exists

    if file:

        # Save file

        filepath = os.path.join(

            app.config["UPLOAD_FOLDER"],

            file.filename

        )

        file.save(filepath)


        # Read PDF

        pdf = PyPDF2.PdfReader(filepath)

        text = ""


        # Extract text

        for page in pdf.pages:

            extracted_text = page.extract_text()

            if extracted_text:

                text += extracted_text


        # Prompt 1

        prompt1 = f"""

You are an AI Career Mentor.

Analyze this resume for the role of:

{job_role}

Resume Content:

{text}

Give:

1. Skills the user already has vs missing skills in a comparative table form with only 2 columns

2. Give one-line explanation for each point below the table

Do not mention user's name anywhere and don  not write anything else

"""


        # Prompt 2

        prompt2 = f"""

You are an AI Career Mentor.

Analyze this resume for the role of:

{job_role}

Resume Content:

{text}

Give:

1. Suggested learning roadmap in diagram from, no sentences

2. Career improvement suggestions in short

Do not mention user's name anywhere.

"""


        # Prompt 3

        prompt3 = f"""

You are an AI Career Mentor.

Analyze this resume for the role of:

{job_role}

Resume Content:

{text}

Give:

1. Interview preparation tips in short

2. Most expected interview questions in short

Do not mention user's name anywhere.

"""


        # Gemini responses

        response1 = model.generate_content(prompt1)

        response2 = model.generate_content(prompt2)

        response3 = model.generate_content(prompt3)


        # Save responses

        analysis_result = response1.text

        roadmap_result = response2.text

        interview_result = response3.text


        # Open analysis page first

        return render_template(

            "analysis.html",

            analysis=analysis_result

        )


# Analysis page

@app.route("/analysis")

def analysis():

    return render_template(

        "analysis.html",

        analysis=analysis_result

    )


# Roadmap page

@app.route("/roadmap")

def roadmap():

    return render_template(

        "roadmap.html",

        analysis=roadmap_result

    )


# Interview page

@app.route("/interview")

def interview():

    return render_template(

        "interview.html",

        analysis=interview_result

    )


# Run app

if __name__ == "__main__":

    app.run(debug=True)
