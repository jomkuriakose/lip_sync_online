# Code to do online lip syncing.
This is a simple lip syncing code.

## Installation
* Python(>3.7)
```bash
pip install -r requirements.txt
```
## How to use
```bash
python lip_sync_online_v1.py
```

```python
from lip_sync_online_v1 import lip_sync

video_path = "test_data/video.mp4"
srt_path = "test_data/subs.srt"
audio_dir = "test_data/audio_1min"
output_video = "test_data/output_video.mp4"
output_srt = "test_data/output_video.srt"

audio_list = os.listdir(audio_dir)
audio_list = [os.path.join(audio_dir, file) for file in audio_list]

lip_sync(video_path, srt_path, audio_list, output_video, output_srt)
```

## Some extra commands
```bash
ffmpeg -y -f lavfi -i "anullsrc=channel_layout=mono:sample_rate=44100" -t 0.1 silence.wav
```
