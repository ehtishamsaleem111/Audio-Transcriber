import os
from dotenv import load_dotenv
from groq import Groq
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

# Load environment variables from .env file
load_dotenv()
st.title("Audio Transcription Application")

# Initialize Groq client
client = Groq()
lanng = st.radio("Choose a language of the audio 'en' for English | 'ur' for Urdu", ["en", "ur"])

# Function to transcribe a single file
def transcribe_single_file(file_path, store_in_kaldi_format):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            # prompt="Give urdu text of audio",  # Optional
            response_format="json",  # Optional
            language=lanng,  # Optional
            temperature=0.0  # Optional
        )

    transcription_text = transcription.text

    # Save the transcription text to a file in the chosen format
    if store_in_kaldi_format:
        # Save in Kaldi format
        audio_file_name = os.path.splitext(os.path.basename(file_path))[0]
        kaldi_transcription = f"{audio_file_name} {transcription_text}"
        with open("transcription.txt", "w", encoding="utf-8") as output_file:
            output_file.write(kaldi_transcription)
        st.write(f"Transcription saved in 'transcription.txt' in Kaldi format.")
    else:
        # Save in simple form
        output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
        with open(output_file_name, "w", encoding="utf-8") as output_file:
            output_file.write(transcription_text)
        st.write(f"Transcription saved in '{output_file_name}'.")

    return transcription_text  # Return the transcription text for displaying

# Transcription function for batch processing
def transcribe_file_for_batch(file_path):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            # prompt="Give urdu text of audio",  # Optional
            response_format="json",  # Optional
            language=lanng,  # Optional
            temperature=0.0  # Optional
        )

    transcription_text = transcription.text
    return transcription_text

# Sequential transcription
def transcribe_files_sequentially(audio_files, store_in_kaldi_format):
    transcriptions = {}  # Dictionary to store transcriptions

    if store_in_kaldi_format:
        kaldi_transcription = []

    for file_path in audio_files:
        transcription_text = transcribe_file_for_batch(file_path)
        transcriptions[file_path] = transcription_text  # Store transcription in dictionary

        if store_in_kaldi_format:
            audio_file_name = os.path.splitext(os.path.basename(file_path))[0]
            kaldi_transcription.append(f"{audio_file_name} {transcription_text}")
        else:
            output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
            with open(output_file_name, "w", encoding="utf-8") as output_file:
                output_file.write(transcription_text)

    if store_in_kaldi_format:
        with open("transcription.txt", "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(kaldi_transcription))
        st.write("All transcriptions saved in 'transcription.txt'.")

    return transcriptions

# Parallel transcription
def transcribe_files_parallel(audio_files, store_in_kaldi_format):
    transcriptions = {}  # Dictionary to store transcriptions

    if store_in_kaldi_format:
        kaldi_transcription = []

    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(transcribe_file_for_batch, file_path): file_path for file_path in audio_files}
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                transcription_text = future.result()
                transcriptions[file_path] = transcription_text  # Store transcription in dictionary

                if store_in_kaldi_format:
                    audio_file_name = os.path.splitext(os.path.basename(file_path))[0]
                    kaldi_transcription.append(f"{audio_file_name} {transcription_text}")
                else:
                    output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
                    with open(output_file_name, "w", encoding="utf-8") as output_file:
                        output_file.write(transcription_text)

            except Exception as e:
                st.write(f"Error processing file {file_path}: {e}")

    if store_in_kaldi_format:
        with open("transcription.txt", "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(kaldi_transcription))
        st.write("All transcriptions saved in 'transcription.txt'.")

    return transcriptions

# Function to list audio files in a folder and its subfolders
def list_audio_files_in_folder(folder_path):
    # List all audio files in the specified folder and its subdirectories
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".wav", ".mp3", ".m4a")):
                audio_files.append(os.path.join(root, file))
    return audio_files

# Main function to display the Streamlit interface
def main():
    # Main menu options
    choice = st.radio("Choose an option:", ["Select a Single File", "Load Multiple Audios"])

    if choice == "Select a Single File":
        uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "m4a"])

        if uploaded_file is not None:
            file_path = uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Ask user to choose the format for saving transcription
            store_choice = st.radio("How would you like to store the transcription?", ["Store Simple Transcription", "Store in Kaldi Structure"])
            store_in_kaldi_format = (store_choice == "Store in Kaldi Structure")
            
            # Add a "Transcribe" button
            if st.button("Transcribe"):
                transcription_text = transcribe_single_file(file_path, store_in_kaldi_format)

                # Display audio file name and transcription side by side
                st.write("Audio File Name And Transcriptions ")
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.write(f"A: {file_path}")
                with col2:
                    st.write(f"T: {transcription_text}")

    elif choice == "Load Multiple Audios":
        # Input for the folder path
        folder_path = st.text_input("Enter the path to the folder containing audio files:")

        if folder_path:
            if os.path.isdir(folder_path):
                audio_files = list_audio_files_in_folder(folder_path)

                if audio_files:
                    st.write(f"Found these following audio files in folder '{folder_path}' and its subdirectories:")
                    for audio_file in audio_files:
                        st.write(audio_file)

                    # Choose storage format
                    store_choice = st.radio("How would you like to store the transcriptions?", ["Store separately with files", "Store in Kaldi Structure"])
                    store_in_kaldi_format = (store_choice == "Store in Kaldi Structure")

                    # Choose transcription mode
                    transcribe_choice = st.radio("How would you like to transcribe the audio files?", ["Sequentially", "In Parallel"])

                    # Add a "Transcribe" button
                    if st.button("Transcribe"):
                        # Transcribe files based on user choice
                        if transcribe_choice == "Sequentially":
                            transcriptions = transcribe_files_sequentially(audio_files, store_in_kaldi_format)
                        elif transcribe_choice == "In Parallel":
                            transcriptions = transcribe_files_parallel(audio_files, store_in_kaldi_format)

                        # Display each audio file name and its transcription side by side
                        st.write("Audio File Name And Transcriptions")
                        for audio_file, transcription in transcriptions.items():
                            col1, col2 = st.columns([1, 5])
                            with col1:
                                st.write(f"A: {audio_file}     ")
                            with col2:
                                st.write(f"T: {transcription}")
                else:
                    st.write("No audio files found in the specified folder and its subdirectories.")
            else:
                st.write("Please enter a valid folder path.")

if __name__ == "__main__":
    main()