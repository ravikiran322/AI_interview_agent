import os
import tempfile
import openai
import pyttsx3

def tts_speak(text: str):
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # silent fail
        pass


def stt_from_file(fileobj, api_key: str = None, model: str = None) -> str:
    """Try to transcribe audio file using OpenAI Whisper (if available). fileobj is a file-like object."""
    if api_key:
        openai.api_key = api_key
    model = model or os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(fileobj.read())
            tmp.flush()
            tmp_filename = tmp.name
        with open(tmp_filename, "rb") as audio_file:
            # The exact function name may vary; try common one
            try:
                resp = openai.Audio.transcribe(model=model, file=audio_file)
                return resp.get("text", "")
            except Exception:
                try:
                    resp = openai.Whisper.transcribe(model=model, file=audio_file)
                    return resp.get("text", "")
                except Exception:
                    return ""
    except Exception:
        return ""
