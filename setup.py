import os
import regex as re
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Build version number from GIT information that GitLab CI puts into env vars
#git_tag = os.environ.get("CI_COMMIT_TAG", default="0.0.0")
#git_hash = os.environ.get("CI_COMMIT_SHORT_SHA", default="xxxxxx")
#version = re.sub("^v", "", git_tag)
#version = version + "+" + git_hash
version = "0.1.0"

setup(
    name="cppcheck-codeclimate",
    version=version,
    license='MIT',
    author="Alex Hogen",
    author_email="code.ahogen@outlook.com",
    description="Convert CppCheck's XML report to a Code Climate JSON file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ahogen/cppcheck-codeclimate",
    # https://docs.python.org/3/distutils/examples.html#pure-python-distribution-by-module
    py_modules=["cppcheck_codeclimate"],
    package_dir = {'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
    entry_points={
        "console_scripts": ["cppcheck-codeclimate=src.cppcheck_codeclimate:main"],
    },
    python_requires=">=3.6",
)
