import pytest
import json

# PYTEST PLUGINS
# - pytest-console-scripts
# - pytest-cov

import cppcheck_codequality as uut

pytest_plugins = "console-scripts"

CPPCHECK_XML_ERRORS_START = r"""<?xml version="1.0" encoding="UTF-8"?><results version="2"><cppcheck version="1.90"/><errors>"""
CPPCHECK_XML_ERRORS_END = r"""</errors></results>"""


# @pytest.mark.script_launch_mode('subprocess')
def test_cli_opts(script_runner):
    ret = script_runner.run("cppcheck-codequality", "-h")
    assert ret.success

    ret = script_runner.run("cppcheck-codequality", "-i")
    assert not ret.success

    ret = script_runner.run(
        "cppcheck-codequality", "--input-file", "./tests/cppcheck_simple.xml"
    )
    assert ret.success

    ret = script_runner.run(
        "cppcheck-codequality", "-i", "./tests/cppcheck_simple.xml", "-o"
    )
    assert not ret.success

    ret = script_runner.run(
        "cppcheck-codequality",
        "-i",
        "./tests/cppcheck_simple.xml",
        "-o",
        "cppcheck.json",
    )
    assert ret.success

    ret = script_runner.run("cppcheck-codequality", "--version")
    assert ret.success


def test_convert_no_messages():
    xml_in = CPPCHECK_XML_ERRORS_START + CPPCHECK_XML_ERRORS_END
    assert uut.__convert(xml_in) == "[]"


def test_convert_severity_warning():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="warning" msg="Ur c0de suks" verbose="i can right go0d3r c0d3 thAn u" cwe="123456789"> <location file="tests/cpp_src/bad_code_1.cpp" line="123" column="456"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    # print(json_out)

    assert len(json_out) == 1
    out = json_out[0]
    assert out["type"] == "issue"
    assert out["check_name"] == "uninitMemberVar"
    assert "CWE" in out["description"]
    assert out["categories"][0] == "Bug Risk"
    assert out["categories"][1] == "warning"
    assert out["location"]["path"] == "tests/cpp_src/bad_code_1.cpp"
    assert out["location"]["positions"]["begin"]["line"] == 123
    assert out["location"]["positions"]["begin"]["column"] == 456
    assert out["fingerprint"] == "a8ead7ccbd052933ff38eb7aeb76b306"


def test_convert_severity_error():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message" cwe="123456789"> <location file="tests/cpp_src/bad_code_1.cpp" line="123" column="456"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["categories"][0] == "Bug Risk"
    assert out["categories"][1] == "error"


def test_convert_no_cwe():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="123" column="456"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["categories"][0] == "Bug Risk"
    assert out["categories"][1] == "error"


def test_convert_multiple_errors():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="information" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="123" column="456"/></error>'
    xml_in += r'<error id="uninitMemberVar" severity="warning" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="246" column="9"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 2
    assert json_out[0]["categories"][1] == "information"
    assert json_out[1]["categories"][1] == "warning"


def test_convert_location_file0():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="cppCheckType" severity="error" msg="message" verbose="message"> <location file0="tests/cpp_src/Foo.cpp" file="tests/cpp_src/Foo.h" line="3"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert json_out[0]["location"]["path"] == "tests/cpp_src/Foo.h"


def test_convert_multiple_locations():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += (
        r'<error id="cppCheckType" severity="error" msg="message" verbose="message">'
    )
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="1"/>'
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="2"/>'
    xml_in += r'<location file="tests/cpp_src/Foo.h" line="3" column="3" />'
    xml_in += r" </error>"
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))

    assert json_out[0]["location"]["path"] == "tests/cpp_src/Foo.h"
    assert json_out[0]["location"]["positions"]["begin"]["line"] == 1

    for i in range(0, 1):
        assert json_out[0]["other_locations"][i]["path"] == "tests/cpp_src/Foo.h"
        assert json_out[0]["other_locations"][i]["positions"]["begin"]["line"] == i + 2


def test_convert_no_loc_column():
    xml_in = CPPCHECK_XML_ERRORS_START
    xml_in += r'<error id="uninitMemberVar" severity="error" msg="message" verbose="verbose message"> <location file="tests/cpp_src/bad_code_1.cpp" line="123"/></error>'
    xml_in += CPPCHECK_XML_ERRORS_END

    json_out = json.loads(uut.__convert(xml_in))
    assert len(json_out) == 1
    out = json_out[0]
    assert out["location"]["positions"]["begin"]["line"] == 123
    assert out["location"]["positions"]["begin"]["column"] == 0


def test_convert_file():
    assert uut.convert_file("tests/cppcheck_simple.xml", "cppcheck.json")

    is_file_actually_json = False
    try:
        with open("cppcheck.json") as fin:
            json.load(fin)
        is_file_actually_json = True
    except ValueError:
        is_file_actually_json = False

    assert is_file_actually_json
