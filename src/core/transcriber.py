from typing import Callable, Dict, List, Optional
import whisperx
import torch
import time


class TranscriptionResult:
    def __init__(self, segments: List[Dict], processing_time: float, word_count: int):
        self.segments = segments
        self.processing_time = processing_time
        self.word_count = word_count
        self.text = ' '.join(segment['text'] for segment in segments)


class WhisperXTranscriber:
    def __init__(self, model_size: str = "base", language: str = "en"):
        self.model_size = model_size
        self.language = language
        self.model = None
        self._setup_device()

    def _setup_device(self):
        """Configure device and compute type based on hardware"""
        if torch.cuda.is_available():
            self.device = "cuda"
            self.compute_type = "float16"
        else:
            self.device = "cpu"
            self.compute_type = "int8"  # Recommended for Mac

        print(f"Using device: {self.device} with compute_type: {self.compute_type}")

    def load_model(self):
        """Load the WhisperX model"""
        if self.model is None:
            asr_options = {
                "temperatures": 0,
                "beam_size": 1,
                "without_timestamps": True,
            }

            self.model = whisperx.load_model(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
                asr_options=asr_options,
                language=self.language,
            )

    def transcribe_audio(
        self,
        audio_path: str,
        batch_size: int = 16,
    ) -> TranscriptionResult:
        """
        Transcribe audio file

        Args:
            audio_path: Path to audio file
            progress_callback: Optional callback for progress updates (0.0 to 1.0)
            batch_size: Batch size for processing

        Returns:
            TranscriptionResult with segments and metadata
        """
        if not self.model:
            self.load_model()

        audio = whisperx.load_audio(audio_path)

        # Transcribe
        start_time = time.time()
        result = self.model.transcribe(audio, batch_size=batch_size)
        processing_time = time.time() - start_time

        # Calculate word count
        word_count = sum(len(segment['text'].split()) for segment in result['segments'])

        return TranscriptionResult(
            segments=result['segments'],
            processing_time=processing_time,
            word_count=word_count,
        )

    def cleanup(self):
        """Clean up model to free memory"""
        if self.model:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


if __name__ == "__main__":
    transcriber = WhisperXTranscriber(model_size="base")

    def progress_update(progress):
        print(f"Progress: {progress:.1%}")

    try:
        result = transcriber.transcribe_audio(
            "examples/3331.mp4", progress_callback=progress_update
        )

        print(f"Transcription completed in {result.processing_time:.2f} seconds")
        print(f"Word count: {result.word_count}")
        print(f"Text preview: {result.text[:200]}...")

    finally:
        transcriber.cleanup()
