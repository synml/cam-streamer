# 웹캠 스트리머

연결된 웹캠의 영상을 HTTP를 통해 스트리밍하는 간단한 Flask 애플리케이션입니다.

## 설치

[uv](https://docs.astral.sh/uv/)가 필요합니다.

```bash
git clone https://github.com/syshin-cubox-ai/cam-streamer
cd cam-streamer
uv sync
```

## exe 실행파일 제작

```bash
uv run exec_pyinstaller.py
```

## 사용법

```bash
uv run cam_streamer.py [옵션]
```

### 옵션

- `--cam_id`: 사용할 카메라의 ID (기본값: `0`).
- `--width`: 비디오 스트림의 원하는 너비 (기본값: `640`).
- `--height`: 비디오 스트림의 원하는 높이 (기본값: `360`).
- `--fps`: 비디오 스트림의 원하는 FPS (기본값: `60`).
- `--quality`: JPEG 인코딩 품질, 0~100 (기본값: `95`).
- `--host`: 서버를 바인딩할 호스트 주소 (기본값: `127.0.0.1`).
- `--port`: 서버를 실행할 포트 번호 (기본값: `5000`).

## 스트림 접근

서버가 실행되면 웹 브라우저를 열고 다음 주소로 이동합니다:

```plain
http://<서버-IP>:<포트>
```

예를 들어, 로컬에서 기본 포트로 실행하는 경우: `http://127.0.0.1:5000`

## OpenCV에서 스트림 접근

카메라 index 자리에 주소를 입력합니다.

```python
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture("http://127.0.0.1:5000")
```

## WSL에서 접근

WSL2의 네트워킹 모드에 따라 접속 방법이 다릅니다.

- **mirrored 모드** (`.wslconfig`에 `networkingMode=mirrored`, Windows 11 22H2+): localhost가 양방향으로
  공유되므로 기본값 그대로 `http://127.0.0.1:5000`으로 접속하면 됩니다.
- **NAT 모드** (기본값): WSL에서 `127.0.0.1`로는 Windows의 서버에 접속할 수 없습니다.
  서버를 `--host 0.0.0.0`으로 실행하고, WSL에서 Windows 호스트 IP로 접속합니다:

  ```bash
  ip route show default | awk '{print $3}'  # Windows 호스트 IP 확인
  ```

## 대안: ffmpeg/mediamtx로 RTSP(H.264) 스트리밍

이 프로젝트의 MJPEG 방식은 단순하지만, H.264로 압축하는 RTSP 방식이 대역폭과 지연 면에서
유리하고 다중 클라이언트 처리도 안정적입니다. 코드 없이 두 프로그램만으로 구성할 수 있습니다.

1. [mediamtx](https://github.com/bluenviron/mediamtx/releases)와
   [ffmpeg](https://www.gyan.dev/ffmpeg/builds/)를 다운로드합니다.

2. `mediamtx.exe`를 실행합니다 (기본 설정으로 RTSP 서버가 8554 포트에 열립니다).

3. 카메라 이름을 확인합니다:

   ```bash
   ffmpeg -list_devices true -f dshow -i dummy
   ```

4. ffmpeg로 웹캠을 mediamtx에 송출합니다:

   ```bash
   ffmpeg -f dshow -framerate 30 -video_size 640x360 -i video="카메라 이름" -c:v libx264 -preset ultrafast -tune zerolatency -pix_fmt yuv420p -f rtsp rtsp://127.0.0.1:8554/cam
   ```

5. OpenCV에서 RTSP 주소로 접근합니다:

   ```python
   cap = cv2.VideoCapture("rtsp://127.0.0.1:8554/cam")
   ```

WSL에서의 접속 방법은 위의 [WSL에서 접근](#wsl에서-접근) 섹션과 동일합니다
(mirrored 모드면 `127.0.0.1` 그대로 사용).
