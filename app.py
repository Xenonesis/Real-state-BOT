from flask import Flask, request, render_template, redirect, url_for, send_file, flash
import whisper
import pandas as pd
import datetime
import os
import subprocess
import uuid
import torch
import time
from googletrans import Translator  # For translation
from flask_socketio import SocketIO, emit  # For real-time updates
import eventlet  # Async library for SocketIO
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.secret_key = 'supersecretkey'
socketio = SocketIO(app, async_mode='eventlet')

# Set upload and results folders
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Use GPU if available
device = "cuda" if torch.cuda.is_available() else "cpu"
logging.info(f"Using device: {device}")

# Load Whisper model
model = whisper.load_model("base").to(device)

# Initialize Translator for Hindi to English
translator = Translator()

# Function to preprocess audio (convert to mono and resample to 16kHz)
def preprocess_audio(input_audio):
    try:
        output_audio = input_audio.replace(".wav", "_processed.wav")
        command = [
            "ffmpeg", "-i", input_audio, "-ac", "1", "-ar", "16000", output_audio, "-y"
        ]  # "-y" to overwrite the output file if it exists
        process = subprocess.run(command, capture_output=True, text=True)
        logging.info(f"FFmpeg output: {process.stdout}")
        if process.returncode != 0:
            logging.error(f"Error in FFmpeg: {process.stderr}")
            return None
        if not os.path.exists(output_audio):
            logging.error("Preprocessed audio file does not exist.")
            return None
        return output_audio
    except Exception as e:
        logging.error(f"Error in audio preprocessing: {e}")
        return None

# Function to handle transcription and translation with progress feedback
def transcribe_audio_with_progress(audio_file):
    try:
        logging.info("Preprocessing audio file...")
        preprocessed_audio = preprocess_audio(audio_file)
        if preprocessed_audio is None:
            logging.error("Preprocessing failed. No valid audio to transcribe.")
            return None, None, 0

        # Start transcription
        logging.info("Transcribing audio file...")
        start_time = time.time()

        # Emit progress at 0%
        socketio.emit('transcription_progress', {'progress': 0})

        result = model.transcribe(preprocessed_audio)

        # Emit progress at 50%
        socketio.emit('transcription_progress', {'progress': 50})

        transcript = result.get('text', "")
        if not transcript:
            logging.error("No transcription found.")
            return None, None, 0

        # Translate Hindi transcript to English
        logging.info("Translating transcript...")
        try:
            translation = translator.translate(transcript, src='hi', dest='en')
            english_transcript = translation.text
        except Exception as e:
            logging.error(f"Error during translation: {e}")
            return transcript, None, 0

        end_time = time.time()
        processing_time = end_time - start_time

        # Emit progress at 100%
        socketio.emit('transcription_progress', {'progress': 100})

        logging.info(f"Transcription result: {transcript}")
        logging.info(f"Translation result: {english_transcript}")
        logging.info(f"Transcription took {processing_time:.2f} seconds.")

        return transcript, english_transcript, processing_time
    except Exception as e:
        logging.error(f"Error during transcription: {e}")
        return None, None, 0

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling file upload and processing
@app.route('/upload', methods=['POST'])
def upload_file():
    client_name = request.form['client_name']
    customer_name = request.form['customer_name']
    file = request.files['audio_file']

    # Check if file is uploaded and is a valid audio file
    if file and file.filename.endswith('.wav'):
        # Generate unique filename to avoid overwriting
        filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Step 1: Transcribe the audio and show progress
        transcript, english_transcript, processing_time = transcribe_audio_with_progress(file_path)
        if transcript is None:
            flash("Error in transcribing audio.")
            return redirect(url_for('index'))

        # Step 2: Analyze the conversation
        is_interested = analyze_conversation(transcript)

        # Step 3: Get the current date
        call_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Step 4: Prepare the data for CSV
        result = {
            "Client Name": client_name,
            "Customer Name": customer_name,
            "Date of Call": call_date,
            "Conversation Transcript": transcript,
            "Translated Transcript (English)": english_transcript,
            "Interested in Property": is_interested,
            "Processing Time (seconds)": f"{processing_time:.2f}"
        }

        # Save the result in a CSV file in the results folder
        csv_filename = f"call_analysis_{uuid.uuid4()}.csv"
        csv_file_path = os.path.join(app.config['RESULTS_FOLDER'], csv_filename)
        df = pd.DataFrame([result])
        df.to_csv(csv_file_path, index=False)

        # Render the result back to the template with download option
        return render_template('index.html', result=result, csv_file=csv_file_path)

    flash("Please upload a valid .wav file.")
    return redirect(url_for('index'))

# Analyze the conversation to determine interest
def analyze_conversation(transcript):
    # Weighted keywords for more precise analysis
    interest_keywords = {
        "interested": 3,
        "buy": 4,
        "purchase": 4,
        "property": 3,
        "schedule a visit": 5,
        "within my budget": 4
    }

    disinterest_keywords = {
        "not interested": 4,
        "too expensive": 3,
        "maybe later": 2,
        "just looking": 2,
        "out of budget": 3,
        "not now": 2
    }

    interest_score = 0
    disinterest_score = 0

    transcript_lower = transcript.lower()

    # Calculate interest and disinterest scores based on weighted keywords
    for keyword, weight in interest_keywords.items():
        if keyword in transcript_lower:
            interest_score += weight

    for keyword, weight in disinterest_keywords.items():
        if keyword in transcript_lower:
            disinterest_score += weight

    # Final decision based on scores
    if interest_score > disinterest_score:
        return "Yes"
    else:
        return "No"

# SocketIO event listener for showing transcription progress
@socketio.on('transcription_progress')
def handle_transcription_progress(data):
    logging.info(f"Progress: {data['progress']}%")

# Route for downloading the CSV file
@app.route('/download/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    return send_file(filename, as_attachment=True)

# Run the app in debug mode with SocketIO
if __name__ == "__main__":
    socketio.run(app, debug=True)
