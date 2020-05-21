import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EpicShelter", # Replace with your own username
    version="0.0.1",
    author="mih01",
    author_email="author@example.com",
    description="The first iteration for epic shelter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mihai011/EpicShelter",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)