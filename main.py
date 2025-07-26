from audio_processor import convert_to_audio
from transcriber import WhisperXTranscriber
from file_manager import cleanup_temp_file, save_transcript

video_file = "examples/3331.mp4"
transcriber = WhisperXTranscriber(model_size="base")

try:
    audio_file = convert_to_audio(video_file)
    result = transcriber.transcribe_audio(audio_file)

    transcript_data = {'segments': result.segments}
    output_file = save_transcript(transcript_data, video_file)
    cleanup_temp_file(audio_file)

    print(f"Done! Saved to {output_file}")
finally:
    transcriber.cleanup()
