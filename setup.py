from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="html-to-dash",
    version='0.2.1',
    author="PierXuY",
    description="Convert HTML to dash format.",
    url="https://github.com/PierXuY/html-to-dash",
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['dash', 'black', 'lxml', 'dash-svg', 'cssutils'],
    keywords=['html', 'dash'],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
