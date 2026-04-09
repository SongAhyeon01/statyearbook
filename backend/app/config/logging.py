import logging
import sys

def setup_logger():

    # 포맷 설정
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 콘솔 출력 핸들러
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # 루트 로거 설정
    root_logger = logging.getLogger("app")
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    return root_logger

def get_logger(name: str):
    return logging.getLogger(f"app.{name}")