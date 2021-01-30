import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "zwiz",
    version = "0.0.1",
    author = "Per Olav Svendsen",
    author_email = "perolav@outlook.com",
    description = "A basic visualiser for Z-wave network in HS3",
    license = "MIT",
    keywords = "homeseer z-wave",
    packages=['zwiz', 'tests'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: MIT License",
    ],
    install_requires=[
        "pandas",
        "requests",
        "BeautifulSoup4",
        "html5lib"]
)