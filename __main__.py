#!/usr/bin/env python3
import argparse
import sys
import os
sys.path.insert(0, os.path.abspath("./gladostts")) # Hack so I don't have to edit gladostts
os.chdir("./gladostts")
import asyncio
import logging
from functools import partial

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from nltk import download
from gladostts.glados import tts_runner
from server.handler import GladosEventHandler

_LOGGER = logging.getLogger(__name__)


async def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", default="stdio://", help="unix:// or tcp://")
    parser.add_argument( # TODO
        "--models-dir",
        help="Data directory to check for downloaded model(s)",
    )
    parser.add_argument( 
        "--auto-punctuation", default=".?!", help="Automatically add punctuation"
    )
    parser.add_argument("--samples-per-chunk", type=int, default=1024)
    #
    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)


    voices = [
        TtsVoice(
            name="default",
            description="default GLaDOS voice",
            attribution=Attribution(
                name="R2D2FISH", url="https://github.com/R2D2FISH/glados-tts"
            ),
            installed=True,
            languages=["en"]
        )
    ]


    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="glados-tts",
                description="A GLaDOS TTS, using Forward Tacotron and HiFiGAN. ",
                attribution=Attribution(
                    name="R2D2FISH", url="https://github.com/R2D2FISH/glados-tts"
                ),
                installed=True,
                voices=voices,
            )
        ],
    )

    # Start gladostts
    # TODO specify the model dir for glados_tts using args.models_dir
    glados_tts = tts_runner(True, False)
    download('punkt', quiet=True)


    # Start server
    server = AsyncServer.from_uri(args.uri)

    _LOGGER.info("Ready")
    await server.run(
        partial(
            GladosEventHandler,
            wyoming_info,
            args,
            glados_tts
        )
    )


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass