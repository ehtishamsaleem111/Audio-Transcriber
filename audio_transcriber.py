from dotenv import load_dotenv
import os
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq()

# Define the filename of the audio file to be transcribed
filename = os.path.dirname(__file__) + "/Arslan4.wav"

# Open the audio file in binary read mode
with open(filename, "rb") as file:
    # Create an audio transcription request
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="whisper-large-v3",
      prompt="Give urdu text of audio",  # Optional
      response_format="json",  # Optional
      language="ur",  # Optional
      temperature=0.0  # Optional
    )

    # Get the transcription text
    transcription_text = transcription.text
    print(transcription_text)  # Print the transcription (for debugging or confirmation)

    # Save the transcription text to a file
    with open("transcription_output.txt", "w", encoding="utf-8") as output_file:
        output_file.write(transcription_text)
