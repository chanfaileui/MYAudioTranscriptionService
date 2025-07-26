# Warmup
import datetime
import os
import whisperx
import torch
import time
import subprocess


def convertFileFormat(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Input file not found: {filename}")
    
    output_filename = filename[:-4] + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.wav'
    cmd = [
        'ffmpeg',
        '-i',
        filename,
        '-vn',  # Strip video
        '-ac',
        '1',  # Mono
        '-ar',
        '16000',  # 16kHz
        '-acodec',
        'pcm_s16le',  # Raw PCM
        '-f',
        'wav',  # WAV container
        output_filename
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300
    )  # 5 minute timeout

    if result.returncode != 0:
        raise Exception(f"FFmpeg failed: {result.stderr}")
    
    if not os.path.exists(output_filename):
        raise Exception("Audio file was not created")

    return output_filename

def transcriptService(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Audio file not found: {filename}")
    
    # For Mac, use CPU with int8 (as per official docs)
    if torch.cuda.is_available():
        device = "cuda"
        compute_type = "float16"
    else:
        device = "cpu"
        compute_type = "int8"  # Official recommendation for Mac

    print(f"Using device: {device} with compute_type: {compute_type}")

    asr_options = {"temperatures": 0, "beam_size": 1, "without_timestamps": True}
    # Run on GPU with FP8
    model = whisperx.load_model(
        "base",
        device=device,
        compute_type=compute_type,
        asr_options=asr_options,
        language="en",
    )

    # Warm up
    audio = whisperx.load_audio(filename)

    start = time.time()
    output = model.transcribe(audio, batch_size=16)
    end = time.time()

    print(f"Transcription time: {end - start}")

    for segment in output['segments']:
        print(segment['text'])


if __name__ == "__main__":
    filename = "./examples/3331.mp4"

    try:
        wav_filename = convertFileFormat(filename)
        transcriptService(wav_filename)
    finally:
        # Clean up the temporary WAV file
        if 'wav_filename' in locals() and os.path.exists(wav_filename):
            os.remove(wav_filename)
    
    print("Complete!")