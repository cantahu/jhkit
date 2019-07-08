#! /usr/bin/env python3
import setuptools

with open('README.md','r') as fh:
    long_description = fh.read()

setuptools.setup(
    name="jhkit",
    version="1.0.8",
    author="J.Hu",
    author_email="joestarhu@163.com",
    description="make your life better",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cantahu.github.io",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
