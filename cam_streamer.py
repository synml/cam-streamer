import argparse
import platform
import threading

import cv2
from flask import Flask, Response

app = Flask(__name__)


class Camera:
    """백그라운드 스레드에서 카메라를 읽고, 최신 JPEG 프레임을 모든 클라이언트에 공유한다."""

    def __init__(self, cam_id: int, width: int, height: int, fps: int, quality: int):
        if platform.system() == "Windows":
            self.cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
        else:
            self.cap = cv2.VideoCapture(cam_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"카메라를 열 수 없습니다 (cam_id={cam_id})")

        for prop, name, value in (
            (cv2.CAP_PROP_FRAME_WIDTH, "width", width),
            (cv2.CAP_PROP_FRAME_HEIGHT, "height", height),
            (cv2.CAP_PROP_FPS, "fps", fps),
        ):
            # 드라이버에 따라 set()이 False를 반환해도 동작에는 문제없는 경우가 많다.
            if not self.cap.set(prop, value):
                print(f"경고: {name}={value} 설정이 적용되지 않았습니다.")

        self.quality = quality
        self.frame: bytes | None = None
        self.stopped = False
        self.condition = threading.Condition()
        threading.Thread(target=self._capture_loop, daemon=True).start()

    def _capture_loop(self):
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    print("프레임을 읽지 못해 캡처를 중단합니다.")
                    break
                ret, jpg = cv2.imencode(
                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality]
                )
                if not ret:
                    continue
                with self.condition:
                    self.frame = jpg.tobytes()
                    self.condition.notify_all()
        finally:
            self.cap.release()
            with self.condition:
                self.stopped = True
                self.condition.notify_all()

    def frames(self):
        while True:
            with self.condition:
                self.condition.wait()
                if self.stopped:
                    return
                frame = self.frame
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                + f"Content-Length: {len(frame)}\r\n\r\n".encode()
                + frame
                + b"\r\n"
            )


@app.route("/")
def video():
    return Response(
        app.config["camera"].frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--cam_id", type=int, default=0)
    args.add_argument("--width", type=int, default=640)
    args.add_argument("--height", type=int, default=360)
    args.add_argument("--fps", type=int, default=60)
    args.add_argument("--quality", type=int, default=95)
    args.add_argument("--host", type=str, default="127.0.0.1")
    args.add_argument("--port", type=int, default=5000)
    opt = args.parse_args()

    app.config["camera"] = Camera(
        opt.cam_id, opt.width, opt.height, opt.fps, opt.quality
    )
    app.run(host=opt.host, port=opt.port)
