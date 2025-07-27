import datetime
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List
import whisperx
import torch
import time


class TranscriptionResult:
    def __init__(self, segments: List[Dict], processing_time: float, word_count: int):
        self.segments = segments
        self.processing_time = processing_time
        self.word_count = word_count
        self.text = ' '.join(segment['text'] for segment in segments)


class TranscriptionService:
    def __init__(self, model_size: str = "base.en", language: str = "en"):
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
            self.compute_type = "int8" # recommended for MacOS

        print(f"Using device: {self.device} with compute_type: {self.compute_type}")

    def _load_model(self):
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

    def _convert_to_audio(self, video_path: str) -> str:
        """Convert video to WAV using ffmpeg"""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Input file not found: {video_path}")

        # Create temp audio file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_audio_path = temp_file.name

        cmd = [
            'ffmpeg',
            '-i',
            video_path,
            '-vn',  # Strip video
            '-ac',
            '1',  # Mono
            '-ar',
            '16000',  # 16kHz
            '-acodec',
            'pcm_s16le',  # Raw PCM
            '-f',
            'wav',  # WAV container
            temp_audio_path,
            '-y',  # Overwrite output file
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            os.unlink(temp_audio_path)  # Clean up on failure
            raise Exception(f"FFmpeg failed: {result.stderr}")

        if not os.path.exists(temp_audio_path):
            raise Exception("Audio file was not created")

        return temp_audio_path

    def _save_transcript(
        self,
        segments: List[Dict],
        original_filename: str,
        output_dir: str = "transcripts",
    ) -> str:
        """Save transcript as text file"""
        os.makedirs(output_dir, exist_ok=True)

        base_name = Path(original_filename).stem
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{output_dir}/{base_name}_transcript_{timestamp}.txt"

        with open(output_file, 'w', encoding='utf-8') as f:
            for segment in segments:
                f.write(segment['text'] + '\n')

        return output_file

    def transcribe_video(
        self, video_path: str, output_dir: str = "transcripts"
    ) -> Dict[str, any]:
        """
        Complete transcription pipeline: video -> audio -> transcript -> save

        Args:
            video_path: Path to video file
            output_dir: Directory to save transcript

        Returns:
            Dict with transcript data and output file path
        """
        temp_audio_path = None

        try:
            # Convert video to audio
            temp_audio_path = self._convert_to_audio(video_path)

            # Load model if needed
            if not self.model:
                self._load_model()

            # Load and transcribe audio
            audio = whisperx.load_audio(temp_audio_path)
            start_time = time.time()
            result = self.model.transcribe(audio, batch_size=16)
            processing_time = time.time() - start_time

            # Calculate word count
            word_count = sum(
                len(segment['text'].split()) for segment in result['segments']
            )

            # Save transcript
            output_file = self._save_transcript(
                result['segments'], video_path, output_dir
            )

            return {
                'segments': result['segments'],
                'processing_time': processing_time,
                'word_count': word_count,
                'output_file': output_file,
                'text': ' '.join(segment['text'] for segment in result['segments']),
            }

        finally:
            # Clean up temp audio file
            if temp_audio_path and os.path.exists(temp_audio_path):
                try:
                    os.unlink(temp_audio_path)
                except OSError:
                    pass

    def cleanup(self):
        """Clean up model to free memory"""
        if self.model:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()


if __name__ == "__main__":
    service = TranscriptionService(model_size="base.en")

    try:
        result = service.transcribe_video("examples/3331.mp4")
        print(f"Done! Saved to {result['output_file']}")
        print(
            f"Processed {result['word_count']} words in {result['processing_time']:.2f} seconds"
        )
    finally:
        service.cleanup()
