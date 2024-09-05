from dotenv import load_dotenv
import os
from groq import Groq
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
client = Groq()

def transcribe_single_file():
    
    # Use Tkinter to open a file dialog and select a single audio file
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = filedialog.askopenfilename(
        title="Select an audio file",
        filetypes=[("Audio Files", "*.wav *.mp3 *.m4a")]
    )

    if not file_path:
        print("No file selected.")
        return

    # Transcribe the selected file
    transcribe_file(file_path)


##### TRANSCRIPTION FUNCTION #####

def transcribe_file(file_path):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            # prompt="Give urdu text of audio",  # Optional
            response_format="json",  # Optional
            language="ur",  # Optional
            temperature=0.0  # Optional
        )

    transcription_text = transcription.text
    print(f"Transcription of {file_path}:\n{transcription_text}")

    # Save the transcription text to a file
    output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
    with open(output_file_name, "w", encoding="utf-8") as output_file:
        output_file.write(transcription_text)
    print(f"Transcription saved to {output_file_name}.")


### SEQUENTIAL AUDIO HANDLING ###
def transcribe_files_sequentially(audio_files, store_in_kaldi_format):
    if store_in_kaldi_format:
        kaldi_transcription = []
    
    for file_path in audio_files:
        transcription_text = transcribe_file_for_batch(file_path)
        
        if store_in_kaldi_format:
            # Format the transcription in Kaldi structure and add to the list
            audio_file_name = os.path.splitext(os.path.basename(file_path))[0]
            kaldi_transcription.append(f"{audio_file_name} {transcription_text}")
        else:
            # Store each transcription separately
            output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
            with open(output_file_name, "w", encoding="utf-8") as output_file:
                output_file.write(transcription_text)
            print(f"Transcription saved to {output_file_name}.")
    
    if store_in_kaldi_format:
        # Save all transcriptions in a single Kaldi structure file
        with open("transcription.txt", "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(kaldi_transcription))
        print("All transcriptions saved in 'transcription.txt'.")

### PARALLEL AUDIO HANDLING ###
def transcribe_files_parallel(audio_files, store_in_kaldi_format):
    if store_in_kaldi_format:
        kaldi_transcription = []
    
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(transcribe_file_for_batch, file_path): file_path for file_path in audio_files}
        for future in as_completed(futures):
            file_path = futures[future]
            try:
                transcription_text = future.result()
                
                if store_in_kaldi_format:
                    # Format the transcription in Kaldi structure and add to the list
                    audio_file_name = os.path.splitext(os.path.basename(file_path))[0]
                    kaldi_transcription.append(f"{audio_file_name} {transcription_text}")
                else:
                    # Store each transcription separately
                    output_file_name = f"{os.path.splitext(file_path)[0]}_transcription.txt"
                    with open(output_file_name, "w", encoding="utf-8") as output_file:
                        output_file.write(transcription_text)
                    print(f"Transcription saved to {output_file_name}.")
                
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
    
    if store_in_kaldi_format:
        # Save all transcriptions in a single Kaldi structure file
        with open("transcription.txt", "w", encoding="utf-8") as output_file:
            output_file.write("\n".join(kaldi_transcription))
        print("All transcriptions saved in 'transcription.txt'.")

def transcribe_file_for_batch(file_path):
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(file_path, file.read()),
            model="whisper-large-v3",
            prompt="Give urdu text of audio",  # Optional
            response_format="json",  # Optional
            language="ur",  # Optional
            temperature=0.0  # Optional
        )

    transcription_text = transcription.text
    print(f"Transcription of {file_path} completed.")
    return transcription_text

def list_and_transcribe_audio_files_in_single_folder():
    # Use Tkinter to open a directory dialog and select a folder
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    folder_path = filedialog.askdirectory(
        title="Select a folder containing audio files"
    )

    if not folder_path:
        print("No folder selected.")
        return

    # List all audio files in the folder
    audio_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if file.endswith((".wav", ".mp3", ".m4a"))
    ]

    if not audio_files:
        print("No audio files found in the selected folder.")
        return

    print("Found the following audio files:")
    for audio_file in audio_files:
        print(audio_file)

    # Ask user how to store the output
    print("\nHow would you like to store the transcriptions?")
    print("Press 1 to store transcription separately with files")
    print("Press 2 to store in Kaldi Structure")

    store_choice = input("Enter your choice (1 or 2): ").strip()
    store_in_kaldi_format = (store_choice == '2')

    # User choice for sequential or parallel processing
    print("\nHow would you like to transcribe the audio files?")
    print("Press 1 to transcribe audio/s sequentially")
    print("Press 2 to transcribe audio/s in parallel")

    transcribe_choice = input("Enter your choice (1 or 2): ").strip()

    if transcribe_choice == '1':
        transcribe_files_sequentially(audio_files, store_in_kaldi_format)
    elif transcribe_choice == '2':
        transcribe_files_parallel(audio_files, store_in_kaldi_format)
    else:
        print("Invalid choice. Please enter 1 or 2.")

def list_and_transcribe_audio_files_in_kaldi_structure():
    # Use Tkinter to open a directory dialog and select a folder
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    folder_path = filedialog.askdirectory(
        title="Select a folder containing sub-folders with audio files"
    )

    if not folder_path:
        print("No folder selected.")
        return

    # List all audio files in the folder and sub-folders
    audio_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith((".wav", ".mp3", ".m4a")):
                audio_files.append(os.path.join(root, file))

    if not audio_files:
        print("No audio files found in the selected folder.")
        return

    print("Found the following audio files:")
    for audio_file in audio_files:
        print(audio_file)

    # Ask user how to store the output
    print("\nHow would you like to store the transcriptions?")
    print("Press 1 to store transcription separately with files")
    print("Press 2 to store in Kaldi Structure")

    store_choice = input("Enter your choice (1 or 2): ").strip()
    store_in_kaldi_format = (store_choice == '2')

    # User choice for sequential or parallel processing
    print("\nHow would you like to transcribe the audio files?")
    print("Press 1 to transcribe audio/s sequentially")
    print("Press 2 to transcribe audio/s in parallel")

    transcribe_choice = input("Enter your choice (1 or 2): ").strip()

    if transcribe_choice == '1':
        transcribe_files_sequentially(audio_files, store_in_kaldi_format)
    elif transcribe_choice == '2':
        transcribe_files_parallel(audio_files, store_in_kaldi_format)
    else:
        print("Invalid choice. Please enter 1 or 2.")

# Main function to display menu and handle user input
def main():
    
    ####### BASE MENU #######

    print("Load Audio/s")
    print("\tPress 1 for Single File")
    print("\tPress 2 for Multiple Audios")

    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == '1':
        
        ### SINGLE FILE HANDLING ###
        transcribe_single_file()

    elif choice == '2':
        
        ### MULTI FILES HANDLING ###
        print("\nLoad Multiple Audio Files")
        print("\tPress 1 to load single folder audios")
        print("\tPress 2 to load Kaldi Structure Audios")

        folder_choice = input("Enter your choice (1 or 2): ").strip()

        if folder_choice == '1':
            list_and_transcribe_audio_files_in_single_folder()
        elif folder_choice == '2':
            list_and_transcribe_audio_files_in_kaldi_structure()
        else:
            print("Invalid choice. Please enter 1 or 2.")
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
