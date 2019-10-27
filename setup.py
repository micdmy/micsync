import setuptools
import subprocess

with open("README.md", "r") as fh:
    readme_file = fh.read()

def get_git_describe():
    command = ["git", "describe", "--abbrev=0"]
    result = subprocess.run(
        args=command, stdout=subprocess.PIPE, text=True).stdout
    return result.strip()


setuptools.setup(
    name="micsync",
    version=get_git_describe(),
    author="micdmy",
    author_email="micdmy2@gmail.com",
    description="Local data synchronization tool based on rsync.",
    long_description=readme_file,
    long_description_content_type="text/markdown",
    url="https://github.com/micdmy",
    packages=setuptools.find_packages(),
    scripts = ["micsync/micsync"],
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: POSIX :: Linux"
    ],
)
