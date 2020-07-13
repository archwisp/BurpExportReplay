import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="burpexportreplay", 
    version="0.0.1",
    author="archwisp",
    author_email="archwisp@gmail.com",
    description="Load, modify, and re-send saved items from Burp Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/archwisp/BurpExportReplay",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
