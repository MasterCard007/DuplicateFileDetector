from setuptools import setup, find_packages

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="duplicate-file-detector",
    version="0.0.9",
    author="MasterCard007",
    author_email="",
    description="A Python tool to detect duplicate files in folders and subfolders.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MasterCard007/DuplicateFileDetector/", 
    packages=find_packages(),
    py_modules=["DuplicateFileDetector"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "tqdm",
    ],
)
