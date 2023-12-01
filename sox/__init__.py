#!/usr/bin/env python
""" init method for sox module """
import os

from .log import logger

# Check that SoX is installed and callable
NO_SOX = False
stream_handler = os.popen("sox -h")
if not len(stream_handler.readlines()):
    logger.warning(
        """SoX could not be found!

    If you do not have SoX, proceed here:
     - - - http://sox.sourceforge.net/ - - -

    If you do (or think that you should) have SoX, double-check your
    path variables.
    """
    )
    NO_SOX = True
stream_handler.close()

from . import file_info
from .combine import Combiner
from .core import SoxError, SoxiError
from .transform import Transformer
from .version import version as __version__
