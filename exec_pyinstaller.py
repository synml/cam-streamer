import shutil
import subprocess
from pathlib import Path


def main():
    subprocess.run(
        [
            "pyinstaller",
            "cam_streamer.py",
            "--onefile",
            "--console",
            "--clean",
            "--icon",
            "res/icon.ico",
            "--name",
            "cam_streamer",
        ],
        check=True,
    )
    shutil.rmtree("build")
    Path("cam_streamer.spec").unlink()


if __name__ == "__main__":
    main()
