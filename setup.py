import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cs1",
    version="0.1",
    author="Matt Lang",
    author_email="langm@rhodes.edu",
    description="Package for cs1 at Rhodes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mattlang/cs1-libraries",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
