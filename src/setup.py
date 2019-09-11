import setuptools

with open("README.md", "r") as fh:
    readme_file = fh.read()

setuptools.setup(
    name="micsync-micdmy",
    version="0.0.1",
    author="micdmy",
    author_email="micdmy2@gmail.com",
    description="Local data synchronization tool based on rsync.",
    long_description=readme_file,
    long_description_content_type="text/markdown",
    url="https://github.com/micdmy",
    packages=setuptools.find_packages(),
    python_requires=">=3",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: POSIX :: Linux"
    ],
)
