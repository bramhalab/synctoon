class WhisperXTranscriptionService:
    """Gentle (Docker) ka drop-in replacement. Same constructor signature
    (files=...) aur .send_request() method -- core.py mein bina kuch aur
    badle isse Gentle ki jagah use kar sakte ho."""

    def __init__(self, files, **kwargs):
        self.transcript_path = next(p for n, p, _ in files if n == "transcript")
        self.audio_path = next(p for n, p, _ in files if n == "audio")

    def send_request(self):
        import whisperx

        device = "cuda"
        model = whisperx.load_model("base", device, compute_type="float16")
        audio = whisperx.load_audio(self.audio_path)
        result = model.transcribe(audio, batch_size=16)

        align_model, metadata = whisperx.load_align_model(
            language_code=result["language"], device=device
        )
        aligned = whisperx.align(result["segments"], align_model, metadata, audio, device)

        words = []
        for seg in aligned["segments"]:
            for w in seg.get("words", []):
                words.append({
                    "word": w["word"],
                    "alignedWord": w["word"],
                    "start": w.get("start", 0.0),
                    "end": w.get("end", 0.0),
                    "case": "success",
                })

        with open(self.transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        return {"transcript": transcript_text, "words": words}
