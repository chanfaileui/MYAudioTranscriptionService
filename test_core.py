from src.core.audio_processor import convert_to_audio
from src.core.transcriber import WhisperXTranscriber
from src.core.file_manager import save_transcript, cleanup_temp_file

video_file = "./examples/3331.mp4"
transcriber = WhisperXTranscriber(model_size="base")

try:
    audio_file = convert_to_audio(video_file)
    result = transcriber.transcribe_audio(audio_file)
    
    # Fix: result, not transcript
    transcript_data = {'segments': result.segments}
    output_file = save_transcript(transcript_data, video_file)
    cleanup_temp_file(audio_file)
    
    print(f"Done! Saved to {output_file}")
finally:
    transcriber.cleanup()