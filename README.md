# MY Audio Transcription Service

**AS A STUDENT WITH GOLDFISH MEMORY WHO HAS TO ATTEND MANY MEETINGS, I WANT  TO HOST/MAKE MY OWN INSTANCE OF AN AUDIO TRANSCRIPTION SERVICE, SO I DON'T HAVE TO PAY.**

Simple GUI for converting speech in video/audio files to text transcripts.
Everything runs locally so you don't have to pay or worry about upload limits.

Using
- WhisperX - Fast AI transcription with word-level timestamps
- PySide6 - Cross-platform GUI framework
- FFmpeg - Audio/video processing

## Quick Start

```bash
git clone <repo>
cd <repo>
./start.sh
```

1. Drag & drop or select a video/audio file
2. Choose output folder
3. Select model size
4. Click "Start Transcription"

Transcripts are saved as `.txt` files with timestamps.

**Note:** Base model is heavily recommended unless you have a good GPU. If you have CUDA on NVIDIA, feel free to use Large. If you're running on a laptop, please don't.

### Supported Formats
Audio: MP3, WAV, FLAC, M4A, OGG, AAC  
Video: MP4, AVI, MOV, MKV, WEBM
