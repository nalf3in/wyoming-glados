"""Event handler for clients of the server."""
import argparse
import logging
import math
import os
import wave
import tempfile

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.event import Event
from wyoming.info import Describe, Info
from wyoming.server import AsyncEventHandler
from wyoming.tts import Synthesize

from nltk.tokenize import sent_tokenize
from pydub import AudioSegment
from gladostts.glados import tts_runner

_LOGGER = logging.getLogger(__name__)


class GladosEventHandler(AsyncEventHandler):
    def __init__(
        self,
        wyoming_info: Info,
        cli_args: argparse.Namespace,
        glados_tts: tts_runner,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.cli_args = cli_args
        self.wyoming_info_event = wyoming_info.event()
        self.glados_tts = glados_tts

    def handle_tts_request(self, text: str, delay: float=250):
        sentences = sent_tokenize(text)
        audio = self.glados_tts.run_tts(sentences[0])
        pause = AudioSegment.silent(duration=delay)
        
        if len(sentences) > 1:
            for idx in range(1, len(sentences)):
                new_line = self.glados_tts.run_tts(sentences[idx])
                audio = audio + pause + new_line

        temp_file = tempfile.NamedTemporaryFile(delete=False)
        audio.export(temp_file.name, format = "wav")

        return temp_file.name

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            await self.write_event(self.wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        if not Synthesize.is_type(event.type):
            _LOGGER.warning("Unexpected event: %s", event)
            return True

        synthesize = Synthesize.from_event(event)
        _LOGGER.debug(synthesize)

        raw_text = synthesize.text

        # Join multiple lines
        text = " ".join(raw_text.strip().splitlines())

        if self.cli_args.auto_punctuation and text:
            # Add automatic punctuation (important for some voices)
            has_punctuation = False
            for punc_char in self.cli_args.auto_punctuation:
                if text[-1] == punc_char:
                    has_punctuation = True
                    break

            if not has_punctuation:
                text = text + self.cli_args.auto_punctuation[0]

        # Actual tts here
        _LOGGER.debug("synthesize: raw_text=%s, text='%s'", raw_text, text)
        wav_path = None
        if len(text) > 0:
            wav_path = self.handle_tts_request(text)

        _LOGGER.debug(wav_path)

        wav_file: wave.Wave_read = wave.open(wav_path, "rb")
        with wav_file:
            rate = wav_file.getframerate()
            width = wav_file.getsampwidth()
            channels = wav_file.getnchannels()

            await self.write_event(
                AudioStart(
                    rate=rate,
                    width=width,
                    channels=channels,
                ).event(),
            )

            # Audio
            audio_bytes = wav_file.readframes(wav_file.getnframes())
            bytes_per_sample = width * channels
            bytes_per_chunk = bytes_per_sample * self.cli_args.samples_per_chunk
            num_chunks = int(math.ceil(len(audio_bytes) / bytes_per_chunk))

            # Split into chunks
            for i in range(num_chunks):
                offset = i * bytes_per_chunk
                chunk = audio_bytes[offset : offset + bytes_per_chunk]
                await self.write_event(
                    AudioChunk(
                        audio=chunk,
                        rate=rate,
                        width=width,
                        channels=channels,
                    ).event(),
                )

        await self.write_event(AudioStop().event())
        _LOGGER.debug("Completed request")

        os.unlink(wav_path)

        return True