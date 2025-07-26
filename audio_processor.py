import datetime
import os
import subprocess


def convert_to_audio(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Input file not found: {filename}")

    output_filename = (
        filename[:-4] + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.wav'
    )
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
        output_filename,
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=300
    )  # 5 minute timeout

    if result.returncode != 0:
        raise Exception(f"FFmpeg failed: {result.stderr}")

    if not os.path.exists(output_filename):
        raise Exception("Audio file was not created")

    return output_filename
