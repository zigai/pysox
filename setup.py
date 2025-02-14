""" Setup script for sox. """

import imp

from setuptools import setup

version = imp.load_source("sox.version", "sox/version.py").version

with open("README.md", "r") as fh:
    long_description = fh.read()

if __name__ == "__main__":
    setup(
        name="sox",
        version=version,
        description="Python wrapper around SoX.",
        author="Rachel Bittner",
        author_email="rachel.bittner@nyu.edu",
        url="https://github.com/rabitt/pysox",
        download_url="http://github.com/rabitt/pysox/releases",
        packages=["sox"],
        package_data={"sox": []},
        long_description=long_description,
        long_description_content_type="text/markdown",
        keywords="audio effects SoX",
        license="BSD-3-Clause",
        install_requires=[
            "numpy >= 1.9.0",
            "typing-extensions >=  3.7.4.2 ",
            "stdl>=0.6.1",
        ],
        extras_require={
            "tests": [
                "pytest",
                "pytest-cov",
                "pytest-pep8",
                "pysoundfile >= 0.9.0",
            ],
            "docs": [
                "sphinx==1.2.3",  # autodoc was broken in 1.3.1
                "sphinxcontrib-napoleon",
                "sphinx_rtd_theme",
                "numpydoc",
            ],
        },
    )
