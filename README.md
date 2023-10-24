# Wyoming GLaDOS

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [GLaDOS](https://github.com/R2D2FISH/glados-tts) text to speech system from R2D2FISH.

The server part is just an heavily stripped down version of [wyoming-piper](https://github.com/rhasspy/wyoming-piper) and the gladostts folder is just a git clone of R2D2FISH's repo

TODOS: 
- Code cleanup
- Docker image
- Automatic download of model files
- PyPI package ? 

## How to run locally

```
git clone
python3 -m venv .venv
source .venv/bin/activate
pip install -R requirements.txt
python __main__.py --uri tcp://0.0.0.0:yourporthere
```

## Docker Image

```
TODO
```