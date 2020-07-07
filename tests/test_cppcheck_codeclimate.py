
import pytest
import json
# PYTEST PLUGINS
# - pytest-console-scripts
# - pytest-cov

import src.cppcheck_codeclimate as uut

pytest_plugins = ("console-scripts")

CPPCHECK_XML_ERRORS_START = r"""<?xml version="1.0" encoding="UTF-8"?><results version="2"><cppcheck version="1.90"/><errors>"""
CPPCHECK_XML_ERRORS_END = r"""</errors></results>"""


#@pytest.mark.script_launch_mode('subprocess')
@pytest.mark.skip(reason="not sure how to get this to work")
def test_cli_opts(script_runner):
  ret = script_runner.run('cppcheck-codeclimate', '-h')
  assert ret.success

  #ret = script_runner.run('cppcheck-codeclimate', '-i')
  #assert ret.success != 0

def test_convert_no_messages():
  xml_in = CPPCHECK_XML_ERRORS_START + CPPCHECK_XML_ERRORS_END
  assert uut.__convert(xml_in) == '[]'

def test_convert_severity_warning():
  xml_in = CPPCHECK_XML_ERRORS_START
  xml_in += r'<error id="uninitMemberVar" severity="warning" msg="Ur c0de suks" verbose="i can right go0d3r c0d3 thAn u" cwe="123456789"> <location file="main.cpp" line="123" column="456"/></error>'
  xml_in += CPPCHECK_XML_ERRORS_END

  json_out = json.loads(uut.__convert(xml_in))
  print(json_out)
  
  assert len(json_out) == 1
  out = json_out[0]
  assert out["type"] == "issue"
  assert out["check_name"] == "uninitMemberVar"
  assert "CWE" in out["description"]
  assert out["categories"][0] == "Bug Risk"
  assert out["categories"][1] == "warning"
  assert out["location"]["path"] == "main.cpp"
  assert out["location"]["positions"]["begin"]["line"] == 123
  assert out["location"]["positions"]["begin"]["column"] == 456
  assert out["fingerprint"] == "b1947b0a4c6e0d29a9ff8cdcc9856fb5"


@pytest.mark.skip(reason="TODO")
def test_convert_severity_error():
  raise NotImplementedError("todo")


@pytest.mark.skip(reason="TODO")
def test_convert_no_cwe():
  raise NotImplementedError("todo")


@pytest.mark.skip(reason="TODO")
def test_convert_multiple_errors():
  raise NotImplementedError("todo")

@pytest.mark.skip(reason="TODO")
def test_convert_multiple_locations():
  raise NotImplementedError("todo")

@pytest.mark.skip(reason="TODO")
def test_convert_file():
  raise NotImplementedError("todo")
