# Warmup
import whisperx
import torch
import time
# import evaluate

# wer = evaluate.load("wer")
# cer = evaluate.load("cer")

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
model = whisperx.load_model("base", device=device, compute_type=compute_type, asr_options=asr_options, language="en")


# Warm up
audio = whisperx.load_audio("./examples/3331.mp4")

start = time.time()
output = model.transcribe(audio, batch_size=16)
end = time.time()

print(f"Transcription time: {end - start}")

print(output)

for segment in output['segments']:
    print(segment['text'])
