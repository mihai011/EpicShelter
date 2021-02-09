import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="epicshelter", 
    version="0.0.3",
    author="mih01",
    author_email="mihaimihai011@gmail.com",
    description="The first iteration for epic shelter from setup.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mihai011/EpicShelter",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)