import logging

def setup_logger(debug: bool = False):
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        filename="logfile.log",
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filemode="a"
    )
    return logging.getLogger("modular-2")
