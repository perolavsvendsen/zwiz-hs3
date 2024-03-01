import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "zwiz-hs3",
    version = "0.1.0",
    author = "Per Olav Svendsen",
    author_email = "perolav@outlook.com",
    url = "https://github.com/perolavsvendsen/zwiz-hs3",
    download_url = "https://github.com/perolavsvendsen/zwiz-hs3/archive/v0.1.0.tar.gz",
    description = "A basic visualiser for Z-wave network in HS3",
    license = "MIT",
    keywords = "homeseer z-wave",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Topic :: Utilities",
        "License :: MIT License",
    ],
    packages = ['zwiz'],
    install_requires=[
        "pandas==1.2.1",
        "dash==1.19.0",
        "dash-core-components==1.15.0",
        "dash-html-components==2.0.0",
        "requests==2.31.0",
        "beautifulsoup4==4.9.3",
        "html5lib==1.1",
        "visdcc==0.0.40",
        ],
    tests_requires=[
        "pytest>=6.2.2"
        ]
)
