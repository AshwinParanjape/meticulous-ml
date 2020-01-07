import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name = "meticulous",
        version = "0.0.1",
        author = "Ashwin Paranjape",
        author_email = "ashwing.2005@gmail.com",
        description = "A package to track the code used to run experiments and compare different experimental runs",
        long_description = long_description,
        url = "https://github.com/AshwinParanjape/meticulous",
        packages = setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        )
