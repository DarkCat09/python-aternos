"""Creates a logger"""

import logging


log = logging.getLogger('aternos')
handler = logging.StreamHandler()
fmt = logging.Formatter('%(asctime)s %(levelname)-5s %(message)s')

handler.setFormatter(fmt)
log.addHandler(handler)


def is_debug() -> bool:
    """Is debug logging enabled"""

    return log.level == logging.DEBUG


def set_debug(state: bool) -> None:
    """Enable debug logging"""

    if state:
        set_level(logging.DEBUG)
    else:
        set_level(logging.WARNING)


def set_level(level: int) -> None:
    log.setLevel(level)
    handler.setLevel(level)
