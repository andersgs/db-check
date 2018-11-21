'''
Setup script for db_check.
'''
import pathlib
from setuptools import setup
from setuptools import find_packages

from db_check import __VERSION__ as version_string

readme_path = pathlib.Path(__file__).parent / "README.md"

README = readme_path.read_text()

# This call to setup() does all the work
setup(
    name="db_check",
    version=version_string,
    description="Sanity check your FASTA DB before release.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/andersgs/db_check",
    author="Anders Gonçalves da Silva",
    author_email="andersgs@gmail.com",
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["click", "pandas", "sh",
                      "tabulate>=0.8.2", "markdown_strings"],
    entry_points={
        "console_scripts": [
            "db-check=db_check.__main__:run_db_check",
        ]
    },
)
