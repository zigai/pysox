"""Base module for calling SoX """

import subprocess
import time
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Iterable, Tuple

import numpy as np
from typing_extensions import Literal

from . import NO_SOX
from .log import logger

SOXI_ARGS = ["B", "b", "c", "a", "D", "e", "t", "s", "r"]

ENCODING_VALS = [
    "signed-integer",
    "unsigned-integer",
    "floating-point",
    "a-law",
    "u-law",
    "oki-adpcm",
    "ima-adpcm",
    "ms-adpcm",
    "gsm-full-rate",
]
EncodingValue = Literal[
    "signed-integer",
    "unsigned-integer",
    "floating-point",
    "a-law",
    "u-law",
    "oki-adpcm",
    "ima-adpcm",
    "ms-adpcm",
    "gsm-full-rate",
]


def sox(
    args: Iterable[str],
    src_array: np.ndarray | None = None,
    decode_out_with_utf: bool = True,
) -> Tuple[int, str | np.ndarray | None, str | None]:
    """Pass an argument list to SoX.

    Parameters
    ----------
    args : iterable
        Argument list for SoX. The first item can, but does not
        need to, be 'sox'.
    src_array : np.ndarray, or None
        If src_array is not None, then we make sure it's a numpy
        array and pass it into stdin.
    decode_out_with_utf : bool, default=True
        Whether or not sox is outputting a bytestring that should be
        decoded with utf-8.

    Returns
    -------
    status : bool
        True on success.
    out : str, np.ndarray, or None
        Returns a np.ndarray if src_array was an np.ndarray.
        Returns the stdout produced by sox if src_array is None.
        Otherwise, returns None if there's an error.
    err : str, or None
        Returns stderr as a string.

    """
    # Explicitly convert python3 pathlib.Path objects to strings.
    args = [str(x) for x in args]

    if args[0].lower() != "sox":
        args.insert(0, "sox")
    else:
        args[0] = "sox"

    try:
        logger.info(f"Executing: '{' '.join(args)}'")
        start_time = time.time()
        if src_array is None:
            process_handle = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            out, err = process_handle.communicate()
            returncode = process_handle.returncode
            if decode_out_with_utf:
                out = out.decode("utf-8")
        elif isinstance(src_array, np.ndarray):
            process_handle = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            # We do order "F" for Fortran formatting of the numpy array, which is
            # sox expects. When we reshape stdout later, we need to use the same
            # order, otherwise tests fail.
            out, err = process_handle.communicate(src_array.T.tobytes(order="F"))
            returncode = process_handle.returncode
        else:
            raise TypeError(f"'src_array' must be an np.ndarray! ({type(src_array)})")

        time_taken = time.time() - start_time
        logger.info(f"SoX took {time_taken:.2f} seconds")

        err = err.decode("utf-8")
        return returncode, out, err

    except OSError as error_msg:
        logger.error("SoX failed!", error=error_msg)
    except TypeError as error_msg:
        logger.error("SoX failed!", error=error_msg)
    return 1, None, None


class SoxError(Exception):
    """Exception to be raised when SoX exits with non-zero status."""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def _get_valid_formats() -> list[str]:
    """Calls SoX help for a lists of audio formats available with the current
    install of SoX.

    Returns
    -------
    formats : list
        List of audio file extensions that SoX can process.

    """
    if NO_SOX:
        return []

    so = subprocess.check_output(["sox", "-h"])
    if type(so) is not str:
        so = str(so, encoding="UTF-8")
    so = so.split("\n")
    idx = [i for i in range(len(so)) if "AUDIO FILE FORMATS:" in so[i]][0]
    formats = so[idx].split(" ")[3:]

    return formats


VALID_FORMATS = _get_valid_formats()


def soxi(filepath: str | Path, argument: str) -> str:
    """Base call to SoXI.

    Parameters
    ----------
    filepath : path-like (str or pathlib.Path)
        Path to audio file.

    argument : str
        Argument to pass to SoXI.

    Returns
    -------
    shell_output : str
        Command line output of SoXI
    """
    filepath = str(filepath)

    if argument not in SOXI_ARGS:
        raise ValueError("Invalid argument '{}' to SoXI".format(argument))

    args = ["sox", "--i"]
    args.append("-{}".format(argument))
    args.append(filepath)

    try:
        shell_output = subprocess.check_output(args, stderr=subprocess.PIPE)
    except CalledProcessError as cpe:
        logger.info("SoXI error message: {}".format(cpe.output))
        raise SoxiError("SoXI failed with exit code {}".format(cpe.returncode))

    shell_output = shell_output.decode("utf-8")

    return str(shell_output).strip("\n\r")


def play(args: Iterable[str]) -> bool:
    """Pass an argument list to play.

    Parameters
    ----------
    args : iterable
        Argument list for play. The first item can, but does not
        need to, be 'play'.

    Returns
    -------
    status : bool
        True on success.

    """
    # Make sure all inputs are strings (eg not pathlib.Path)
    args = [str(x) for x in args]

    if args[0].lower() != "play":
        args.insert(0, "play")
    else:
        args[0] = "play"

    try:
        logger.info("Executing: %s", " ".join(args))
        process_handle = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        status = process_handle.wait()
        if process_handle.stderr is not None:
            logger.info(process_handle.stderr)

        if status == 0:
            return True
        else:
            logger.info("Play returned with error code %s", status)
            return False
    except OSError as error_msg:
        logger.error("OSError: Play failed! %s", error_msg)
    except TypeError as error_msg:
        logger.error("TypeError: %s", error_msg)
    return False


class SoxiError(Exception):
    """Exception to be raised when SoXI exits with non-zero status."""

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


def is_number(var: Any) -> bool:
    """Check if variable is a numeric value.

    Parameters
    ----------
    var : object

    Returns
    -------
    is_number : bool
        True if var is numeric, False otherwise.
    """
    try:
        float(var)
        return True
    except ValueError:
        return False
    except TypeError:
        return False


def all_equal(list_of_things: list[Any]) -> bool:
    """Check if a list contains identical elements.

    Parameters
    ----------
    list_of_things : list
        list of objects

    Returns
    -------
    all_equal : bool
        True if all list elements are the same.
    """
    return len(set(list_of_things)) <= 1
