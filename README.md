# README

- [README](#readme)
- [About](#about)
  - [Stinkin' Badges](#stinkin-badges)
  - [Usage](#usage)
    - [To-Do](#to-do)
  - [Contributing](#contributing)
  - [Credits & Trademarks](#credits--trademarks)

# About

I wanted reports from CppCheck to appear in GitLab Merge Requests as [Code
Quality reports](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#implementing-a-custom-tool), 
which is a JSON file defined by the Code Climate team/service.

That's all this does: convert CppCheck XML to Code Climate JSON.

## Stinkin' Badges

TODO: Coming soon...

*Reference: ["The Treasure of the Sierra Madre"](https://en.wikipedia.org/wiki/Stinking_badges)*

## Usage

CppCheck already has a script to convert its XML report to HTML for easy
human reading. See "Chapter 11 HTML Report" in the [CppCheck Manual v?.?](http://cppcheck.sourceforge.net/manual.pdf)

This script follows that example and provides similar command-line options. So
usage is as follows:

```bash
# Generate CppCheck report as XML
cppcheck --xml --enable=warning,style,performance ./my_src_dir/ 2> cppcheck_out.xml
# Convert to a Code Climate JSON report
python3 -m cppcheck-codequality --file=cppcheck_out.xml
```

### To-Do


* [X] Implement issue fingerprinting for GitLab
* [X] Logging instead of prints
* [ ] Versioning
* [ ] Ensure it works both as an importable module and as a script
* [X] Project's `pylint` badge
* [ ] Generate a badge with https://shields.io/ colors using [anybadge](https://pypi.org/project/anybadge/)
* [ ] Figure out PyPi packaging
* [ ] Generate Sphinx docs
* [X] Add license
* [ ] Add contributor agreement

## Contributing

* Sign the contributor agreement (coming soon)
* Format with [black](https://pypi.org/project/black/)
* Check with [pylint](https://pypi.org/project/pylint/)

## Credits & Trademarks

CppCheck is an open-source project with a GPL v3.0 license.
* http://cppcheck.sourceforge.net
* https://github.com/danmar/cppcheck

"Code Climate" may be a registered trademark of Code Climate, Inc. which provides
super-cool free and paid services to the developer community.
* https://codeclimate.com
* https://github.com/codeclimate

"GitLab" is a trademark of GitLab B.V.
* https://gitlab.com
* https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html

All other trademarks belong to their respective owners.