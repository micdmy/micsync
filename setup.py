import setuptools
import subprocess
from micsync.version import __version__
from micsync.version import _program_name

with open("README.md", "r") as fh:
    readme_file = fh.read()

setuptools.setup(
    name = _program_name,
    version = __version__,
    author = "micdmy",
    author_email = "micdmy2@gmail.com",
    description = "Local data synchronization tool based on rsync.",
    long_description = readme_file,
    long_description_content_type = "text/markdown",
    url = "https://github.com/micdmy/micsync/",
    packages = setuptools.find_packages(),
    scripts = ["micsync/micsync"],
    python_requires = ">=3.7",
    setup_requires = [
        "wheel",
        "twine"
    ],
    license = "GPLv3",
    classifiers = [
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux"
    ],
)
