import sys

from loguru import logger
from stdl.log import loguru_formater

logger.remove()
logger = logger.bind(title="SOX")
logger.add(sys.stdout, format=loguru_formater, level="DEBUG")  # type: ignore
