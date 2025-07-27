from transcriber import TranscriptionService

service = TranscriptionService(model_size="base.en")

try:
    result = service.transcribe_video("examples/3331.mp4")
    print(f"Done! Saved to {result['output_file']}")
    print(f"Text: {result['text'][:100]}...")  # Show first 100 chars
finally:
    service.cleanup()