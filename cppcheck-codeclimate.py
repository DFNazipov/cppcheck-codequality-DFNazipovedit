#!/usr/bin/env python3
"""CppCheck XML to Code Quality JSON

"""
import os
import sys
import logging
from copy import deepcopy
import argparse
import json
import re

# Non-system
import xmltodict
import hashlib
import linecache
import anybadge


# Package information
version = __version__ = "v0.1.0"
__version_info__ = tuple(re.split("[.-]", __version__))
__title__ = "cppcheck-codeclimate"
__author__ = "Alex Hogen <code.ahogen@outlook.com>"
__summary__ = "Convert CppCheck XML to Code Climate JSON report"
__uri__ = "https://github.com/ahogen/cppcheck-codeclimate"

log = logging.getLogger(__title__)

# Source: https://github.com/codeclimate/platform/blob/master/spec/analyzers/SPEC.md#data-types
CODE_QUAL_ELEMENT = {
    "type": "issue",
    "check_name": "--REQUIRED-FOR-CODEQUALITY--",
    "description": "--REQUIRED-FOR-CODEQUALITY--",
    "categories": "--REQUIRED-FOR-CODEQUALITY--",
    "fingerprint": "--REQUIRED-FOR-GITLAB--",
    "location": {"path": "", "lines": {"begin": -1}},
}


def _init_logging():
    """Setup root logger to log to console, when this is run as a script"""
    h_console = logging.StreamHandler()
    log_fmt_short = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s: %(message)s", datefmt="%H:%M:%S"
    )
    h_console.setFormatter(log_fmt_short)

    # Add console handler to root logger
    logging.getLogger("").addHandler(h_console)


def _get_args() -> argparse.Namespace:
    """Parse CLI args with argparse"""
    # Make parser object
    p = argparse.ArgumentParser(
        description=__doc__ + "\n\nVersion: " + __version__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    p.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        dest="input_file",
        type=str,
        # default="STDIN",
        default="./",
        help="the cppcheck XML output file to read defects from (default: %(default)s)",
    )

    p.add_argument(
        "-o",
        "--output-file",
        metavar="FILE",
        dest="output_file",
        type=str,
        default="cppcheck.json",
        help="output filename to write JSON to (default: %(default)s)",
    )

    # p.add_argument(
    #     "-s",
    #     "--source-dir",
    #     metavar="SOURCE_DIR",
    #     type=str,
    #     default=".",
    #     help="Base directory where source code files can be found. (default: '%(default)s')",
    # )

    p.add_argument(
        "-l",
        "--loglevel",
        metavar="LVL",
        type=str,
        choices=["debug", "info", "warn", "error"],
        default="info",
        help="set logging message severity level (default: '%(default)s')",
    )

    p.add_argument(
        "-v",
        "--version",
        dest="print_version",
        action="store_true",
        help="print version and exit",
    )

    return p.parse_args()


def _get_codeclimate_category(cppcheck_severity: str) -> str:
    # CppCheck: error, warning, style, performance, portability, information
    # CodeQuality: Bug Risk, Clarity, Compatibility, Complexity, Duplication,
    #              Performance, Security, Style
    MAP_SEVERITY_TO_CATEGORY = {
        "error": "Bug Risk",
        "warning": "Bug Risk",
        "style": "Style",
        "performance": "Performance",
        "portability": "Compatibility",
        "information": "Style",
    }
    return MAP_SEVERITY_TO_CATEGORY[cppcheck_severity]


def convert(fname_in: str, fname_out: str) -> bool:
    """Convert CppCheck XML to Code Climate JSON

    Note:
        There isn't a great 1:1 conversion from CppCheck's "severity" level, to
        the Code Climate's "categories." To prevent information loss, the 
        original CppCheck severity is appended to the category list.

        In the future, maybe this conversion can be made using CppCheck's "id" 
        or check name.

    Args:
        fname_in (str): Filename of the XML from CppCheck 
        fname_out (str): Filename to write the JSON output

    Returns:
        bool: True if there were no errors during the conversion
    """
    fin = None
    tmp_dict_in = dict()

    try:
        if isinstance(fname_in, str):
            log.debug("Reading input file: %s", os.path.abspath(fname_in))
            fin = open(fname_in, mode="r")
        ## STDIN used when running as a script from command line. Not intended for
        ## use when being used as a library.
        # else:
        #     log.debug("Reading from STDIN")
        #     fin = fname

        tmp_dict_in = xmltodict.parse(fin.read())
    finally:
        if fin is not sys.stdin:
            log.debug("Closing input file")
            fin.close()

    # log.debug("Got the following dict:\n%s\n", str(tmp_dict_in))

    if len(tmp_dict_in) == 0:
        log.info("Empty file imported. Skipping...")
        return True

    if tmp_dict_in["results"]["cppcheck"]["@version"] < "1.82":
        log.warn("\nWARNING: This was tested against a newer version of CppCheck")

    tmp_dict_out = list()
    for error in tmp_dict_in["results"]["errors"]["error"]:
        # Some information messages are not related to the code.
        # Let's just skip those.
        if "location" not in error:
            continue

        tmp_dict = dict(CODE_QUAL_ELEMENT)
        tmp_dict["check_name"] = str(error["@id"])
        tmp_dict["description"] = str(error["@msg"])

        cats = list(_get_codeclimate_category(error["@severity"]).split("\n"))
        cats.append(error["@severity"])
        tmp_dict["categories"] = cats

        tmp_dict["location"]["path"] = str(error["location"]["@file"])
        tmp_dict["location"]["lines"]["begin"] = int(error["location"]["@line"])
        tmp_dict["content"] = {"data": ""}

        if "@cwe" in error:
            cwe_id = error["@cwe"]
            tmp_dict["description"] = (
                "[CWE-{}] ".format(cwe_id) + tmp_dict["description"]
            )
            msg = "[CWE-{}](https://cwe.mitre.org/data/definitions/{}.html)".format(
                cwe_id, cwe_id
            )
            tmp_dict["content"]["data"] += msg

        # Fingerprint should be a hash of the error ID + the line of code
        # that is generating the error.
        # E.g. "wrongPrintfScanfArgNum" + "  printf("Hello World: %d %s", 42);"
        # Refer to:
        # - https://github.com/codeclimate/codeclimate-duplication/blob/1c118a13b28752e82683b40d610e5b1ee8c41471/lib/cc/engine/analyzers/violation.rb#L83
        # - https://github.com/codeclimate/codeclimate-phpmd/blob/7d0aa6c652a2cbab23108552d3623e69f2a30282/tests/FingerprintTest.php

        # TODO: All this...
        # finger_str = tmp_dict["check_name"]
        str_code_line = linecache.getline(
            tmp_dict["location"]["path"], tmp_dict["location"]["lines"]["begin"]
        )
        # hashlib.md5("whatever your string is".encode('utf-8')).hexdigest()

        tmp_dict_out.append(deepcopy(tmp_dict))

    log.debug("Writing output file: %s", fname_out)
    with open(fname_out, "w") as f:
        f.write(json.dumps(tmp_dict_out))

    return True


if sys.version_info < (3, 5, 0):
    sys.stderr.write("You need python 3.5 or later to run this script\n")
    sys.exit(1)

if __name__ == "__main__":

    _init_logging()
    log = logging.getLogger(__title__)

    args = _get_args()
    log.setLevel(args.loglevel.upper())

    if args.print_version:
        print(__version__)
        sys.exit(0)

    if not convert(fname_in=args.input_file, fname_out=args.output_file)
        sys.exit(1)
    else:
        sys.exit(0)

    # log.debug("Generating SVG badge")
    # badge = anybadge.Badge("cppcheck", "-TESTING-")
    # badge.write_badge(os.path.splitext(args.output_file)[0] + ".svg", overwrite=True)
