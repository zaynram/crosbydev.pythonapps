from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.resolve(strict=True)
DATA_DIR = (ROOT_DIR / "data").resolve(strict=True).as_posix()
LOG_DIR = (ROOT_DIR / "logs").resolve(strict=True)
