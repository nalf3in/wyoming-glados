# Wyoming GLaDOS

[Wyoming protocol](https://github.com/rhasspy/wyoming) server for the [GLaDOS](https://github.com/R2D2FISH/glados-tts) text to speech system from R2D2FISH. Its uses CUDA acceleration if supported.

The server part is an heavily stripped down version of [wyoming-piper](https://github.com/rhasspy/wyoming-piper) and the gladostts folder is a [Git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules) of R2D2FISH's repo

TODOS: 
- Docker image ✅
- Automatic download of model files ✅ (please use download.py)
- Add options to the docker container
- Code cleanup
- Speedup the tts engine for rtx gpus ? See [here](https://developer.nvidia.com/tensorrt)
- PyPI package ? 

## How to run locally

```
git clone --recurse-submodules https://github.com/nalf3in/wyoming-glados # You will probably get a git lfs error, this is fine
cd wyoming-glados
python3 download.py # Can be done in the venv if you prefer
python3 -m venv .venv
source .venv/bin/activate
pip install -R requirements.txt
python __main__.py --uri tcp://0.0.0.0:10201
```

## Docker Image

### docker-compose (recommended)
```
---
version: "3"
services:
  wyoming-glados:
    image: docker.io/nalf3in/wyoming-glados:latest
    container_name: wyoming-glados
    ports:
      - 10201:10201
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### docker cli

```
docker run --restart unless-stopped -p 10201:10201 --runtime=nvidia docker.io/nalf3in/wyoming-glados:latest
```