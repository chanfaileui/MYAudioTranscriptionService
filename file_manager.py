import os
import datetime
from pathlib import Path


def save_transcript(transcript_data, original_filename, output_dir="transcripts"):
    """Save transcript as text file"""
    os.makedirs(output_dir, exist_ok=True)

    base_name = Path(original_filename).stem
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{base_name}_transcript_{timestamp}.txt"

    with open(output_file, 'w', encoding='utf-8') as f:
        for segment in transcript_data['segments']:
            f.write(segment['text'] + '\n')

    return output_file


def cleanup_temp_file(file_path):
    """Remove temp file"""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError:
            pass
