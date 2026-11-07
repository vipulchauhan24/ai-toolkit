import logging

logger = logging.getLogger(__name__)


def load(raw: str) -> int:
    try:
        return int(raw)
    except:
        logger.warning("bad number")
        return 0
