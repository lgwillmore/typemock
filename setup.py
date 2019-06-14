import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="typemock",
    version="0.3.3",
    author="Laurence Willmore",
    description="Type safe mocking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lgwillmore/type-mock",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
