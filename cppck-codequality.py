#!/usr/bin/env python3
"""CppCheck XML to Code Quality JSON

"""
import os
import sys
import logging
from copy import deepcopy
import argparse

import json
import xmltodict
import hashlib
import linecache


if sys.version_info < (3, 5, 0):
    sys.stderr.write("You need python 3.5 or later to run this script\n")
    sys.exit(1)

CODE_QUAL_ELEMENT = {
    "type": "issue",
    "check_name": "--REQUIRED-FOR-CODEQUALITY--",
    "description": "--REQUIRED-FOR-CODEQUALITY--",
    "categories": "--REQUIRED-FOR-CODEQUALITY--",
    "fingerprint": "--REQUIRED-FOR-GITLAB--",
    "location": {"path": "", "lines": {"begin": -1}},
}

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


def main(args: argparse):
    fin = None
    tmp_dict_in = dict()
    tmp_dict_out = list()

    # if args.fname:
    #     fin = open(args.fname)
    # else:
    # fin = sys.stdin
    fin = open("cppcheck_out.xml", mode="r")

    try:
        tmp_dict_in = xmltodict.parse(fin.read())
    finally:
        if fin is not sys.stdin:
            print("Closing file")
            fin.close()

    print("Got the following dict:")
    print(tmp_dict_in)

    for error in tmp_dict_in["results"]["errors"]["error"]:
        # Some information messages are not related to the code.
        # Let's just skip those.
        if "location" not in error:
            continue

        tmp_dict = dict(CODE_QUAL_ELEMENT)
        tmp_dict["check_name"] = str(error["@id"])
        tmp_dict["description"] = str(error["@msg"])
        tmp_dict["categories"] = list(
            MAP_SEVERITY_TO_CATEGORY[error["@severity"]].split("\n")
        )
        tmp_dict["categories"].append(error["@severity"])

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
        # hashlib.md5("whatever your string is".encode('utf-8')).hexdigest()

        tmp_dict_out.append(deepcopy(tmp_dict))

    print("Writing output")
    with open("cppcheck_codequality.json", "w") as fout:
        fout.write(json.dumps(tmp_dict_out))


if __name__ == "__main__":
    main(None)
