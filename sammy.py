import os
import wave
import numpy as np
import speech_recognition as sr

# Function to enhance audio quality by increasing volume
def enhance_audio(input_audio_file, output_audio_file, volume_gain=1.5):
    with wave.open(input_audio_file, 'rb') as audio:
        params = audio.getparams()
        num_frames = audio.getnframes()

        with wave.open(output_audio_file, 'wb') as output_audio:
            output_audio.setparams(params)
            frames_per_read = 1024  # Number of frames to read at a time
            for _ in range(0, num_frames, frames_per_read):
                frames = audio.readframes(frames_per_read)
                enhanced_frames = enhance_audio_frames(frames, params.sampwidth, volume_gain)
                output_audio.writeframes(enhanced_frames)

    print(f"Enhanced audio temporarily created as {output_audio_file}")

def enhance_audio_frames(frames, sampwidth, volume_gain):
    if sampwidth == 1:  # 8-bit audio
        audio_samples = np.frombuffer(frames, dtype=np.uint8) - 128  # Convert to signed
    elif sampwidth == 2:  # 16-bit audio
        audio_samples = np.frombuffer(frames, dtype=np.int16)
    else:
        raise ValueError("Unsupported sample width")

    enhanced_samples = (audio_samples * volume_gain).astype(audio_samples.dtype)

    if sampwidth == 1:
        enhanced_samples = np.clip(enhanced_samples + 128, 0, 255)  # Convert back to unsigned
    elif sampwidth == 2:
        enhanced_samples = np.clip(enhanced_samples, -32768, 32767)

    return enhanced_samples.tobytes()

# Function to convert audio to text
def process_audio_chunk(chunk_filename, recognizer):
    with sr.AudioFile(chunk_filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            text = ""
        return text

# Function to split audio into chunks and transcribe each chunk
def audio_to_text(input_audio_file, output_text_file, chunk_size=1024):
    recognizer = sr.Recognizer()

    with wave.open(input_audio_file, 'rb') as audio:
        n_channels = audio.getnchannels()
        sampwidth = audio.getsampwidth()
        frame_rate = audio.getframerate()
        total_chunks = int(audio.getnframes() / chunk_size)

        collected_text = []  # Collect text from each chunk

        for i in range(total_chunks):
            chunk_filename = f"chunk_{i}.wav"
            with wave.open(chunk_filename, 'wb') as chunk:
                chunk.setnchannels(n_channels)
                chunk.setsampwidth(sampwidth)
                chunk.setframerate(frame_rate)
                frames = audio.readframes(chunk_size)
                chunk.writeframes(frames)

            text = process_audio_chunk(chunk_filename, recognizer)
            collected_text.append(text)  # Collect the text

            os.remove(chunk_filename)

        # Write all collected text to the file at once
        with open(output_text_file, 'w') as output_file:
            output_file.write("\n".join(collected_text))
        
        print(f"Writing all text to file: {output_text_file}")

    print(f"Audio conversion complete. Text saved to {output_text_file}")

# Main function to process audio files in a folder and save output in the specified folder
def process_audios_in_folder(audio_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(audio_folder):
        if filename.endswith('.wav'):
            audio_path = os.path.join(audio_folder, filename)
            base_name = os.path.splitext(filename)[0]
            enhanced_audio_path = f"{base_name}_enhanced_temp.wav"
            output_text_file = os.path.join(output_folder, f"{base_name}.txt")

            # Enhance audio quality
            enhance_audio(audio_path, enhanced_audio_path)

            # Convert enhanced audio to text
            audio_to_text(enhanced_audio_path, output_text_file)

            # Clean up: delete the temporary enhanced audio file
            os.remove(enhanced_audio_path)

            print(f"Processed audio {filename} and saved output as {output_text_file}")

# Example usage
audio_folder = "audio"
output_folder = "transcribed"
process_audios_in_folder(audio_folder,output_folder)