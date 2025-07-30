import asyncio
import logging

import keyboard
from speechmatics.rt import (
    AsyncClient,
    AudioEncoding,
    AudioFormat,
    Microphone,
    OperatingPoint,
    ServerMessageType,
    TranscriptResult,
    TranscriptionConfig,
)


logging.basicConfig(level=logging.INFO)


import threading

async def start_transcribing(language_code: str = "en", device_index: int = None, stop_event: threading.Event = None, api_key: str = None, on_error=None) -> None:
    """Run async transcription with selected language and mic device. stop_event ile durdurulabilir."""
    transcript_parts = []

    # Configure audio format and transcription
    audio_format = AudioFormat(
        encoding=AudioEncoding.PCM_S16LE,
        chunk_size=4096,
        sample_rate=16000,
    )

    transcription_config = TranscriptionConfig(
        max_delay=0.8,
        enable_partials=True,
        operating_point=OperatingPoint.ENHANCED,
        language=language_code
    )

    mic = Microphone(
        sample_rate=audio_format.sample_rate,
        chunk_size=audio_format.chunk_size,
        device_index=device_index,
    )

    if not mic.start():
        print("PyAudio not installed - microphone not available")
        print("Install with: pip install pyaudio")
        return

    # Initialize client with API key from environment
    try:
        async with AsyncClient(api_key=api_key) as client:
            # Register callbacks for transcript events
            @client.on(ServerMessageType.ADD_TRANSCRIPT)
            def handle_final_transcript(message):
                result = TranscriptResult.from_message(message)
                if result.transcript:
                    transcript_parts.append(result.transcript)
                    keyboard.write(result.transcript)

            await client.start_session(
                transcription_config=transcription_config,
                audio_format=audio_format,
            )

            while True:
                if stop_event is not None and stop_event.is_set():
                    # End transcription loop
                    break
                frame = await mic.read(audio_format.chunk_size)
                await client.send_audio(frame)
    except Exception as e:
        if ("Not Authorized" in str(e)) or ("TranscriptionError" in str(e)):
            if on_error:
                on_error("Not Authorized")
        else:
            if on_error:
                on_error(str(e))
        print(f"Transcription error: {e}")