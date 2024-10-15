
# Real Estate Call Analysis Bot

## Overview

The **Real Estate Call Analysis Bot** is a web-based tool that allows users to upload audio recordings of real estate conversations, transcribe the audio using Whisper (an automatic speech recognition model), and analyze the conversation to determine customer interest in the property. The tool also provides Hindi-to-English translation for better comprehension of the conversation. The output includes a detailed transcript, translated transcript, customer interest analysis, and the ability to download the analysis in CSV format.

## Features

- **Audio Transcription**: Converts spoken conversations into text using Whisper.
- **Hindi-to-English Translation**: Automatically translates the transcribed Hindi audio into English.
- **Customer Interest Analysis**: Analyzes the conversation to determine if the customer is interested in the property based on specific keywords.
- **CSV Export**: Provides an option to download the call analysis in a CSV file.
- **Real-time Progress Feedback**: Shows progress feedback while processing the audio file.
  
## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, Bootstrap
- **Realtime Feedback**: Flask-SocketIO
- **Audio Processing**: Whisper (Automatic Speech Recognition)
- **Translation**: Googletrans
- **Data Export**: Pandas
- **Audio Preprocessing**: FFmpeg

## Requirements

Before running the project, make sure you have the following installed:

- Python 3.8+
- FFmpeg (for audio preprocessing)
- Whisper (PyTorch-based ASR model)
- Googletrans (for Hindi to English translation)
- Flask and Flask-SocketIO for web and real-time feedback

### Python Packages
All the required Python packages are listed in the `requirements.txt`. You can install them using the following command:

```bash
pip install -r requirements.txt
```

**`requirements.txt` includes:**
```
Flask
whisper
torch
pandas
googletrans==4.0.0-rc1
Flask-SocketIO
eventlet
```

## Project Structure

```
├── app.py                  # Main Flask application
├── templates/
│   └── index.html          # HTML template for the web interface
├── static/
│   └── style.css           # Custom CSS styles
├── uploads/                # Folder to store uploaded audio files
├── results/                # Folder to store analysis results (CSV)
├── requirements.txt        # Python package dependencies
└── README.md               # Project documentation
```

## Installation

### Clone the Repository
```bash
git clone https://github.com/your-username/real-estate-call-analysis-bot.git
cd real-estate-call-analysis-bot
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Install FFmpeg
FFmpeg is required for audio preprocessing. Install it using:

- **For Windows**: Download FFmpeg from [here](https://ffmpeg.org/download.html) and add it to your system's PATH.
- **For MacOS**: Install using Homebrew:
  ```bash
  brew install ffmpeg
  ```
- **For Linux**:
  ```bash
  sudo apt install ffmpeg
  ```

## Usage

1. **Start the Flask Server:**

   In your project root directory, run the following command:
   ```bash
   python app.py
   ```

2. **Access the Web Interface:**

   Open your web browser and go to `http://127.0.0.1:5000/`. You will be presented with an interface to upload audio files.

3. **Upload a Call Recording:**

   - Fill in the client and customer name fields.
   - Upload a `.wav` or `.mp3` file containing the call recording.
   - Click on the "Submit" button to begin processing.

4. **View Results:**

   Once the file is processed, the web page will display:
   - **Client and Customer Names**
   - **Conversation Transcript**: The original transcript of the call.
   - **Translated Transcript**: The transcript translated into English.
   - **Customer Interest**: The result of analyzing the customer’s interest in the property.
   - **Processing Time**: Time taken to process the file.

   You will also have an option to download the results as a CSV file.

## How It Works

1. **Audio Preprocessing**: 
   - The uploaded audio is converted to mono and resampled to 16kHz using FFmpeg.

2. **Speech Transcription**:
   - Whisper, a state-of-the-art automatic speech recognition model, transcribes the speech into text.

3. **Translation**:
   - If the conversation is in Hindi, the transcript is automatically translated to English using Googletrans.

4. **Interest Analysis**:
   - The system analyzes the transcript for keywords to determine whether the customer is interested in the property.

5. **Progress Updates**:
   - Throughout the process, progress is displayed in real-time via a progress bar, powered by SocketIO.

## Customization

### Change the Whisper Model
The model used for transcription is currently set to `base`. If you want to use a larger or smaller model, you can modify this in `app.py`:

```python
# Load Whisper model
model = whisper.load_model("base").to(device)
```
Change `"base"` to `"small"`, `"medium"`, or `"large"` depending on your needs. Larger models improve transcription accuracy but are slower and more resource-intensive.

## Issues

If you encounter any issues while running the project, feel free to open an issue on GitHub or reach out via email.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Acknowledgements

- **Whisper Model**: OpenAI
- **Translation API**: Googletrans
- **FFmpeg**: For audio processing
- **Bootstrap**: For front-end styling
- **Flask-SocketIO**: For real-time updates
- **Pandas**: For generating CSV reports

please contact itisaddy7@gmail.com for any help !
