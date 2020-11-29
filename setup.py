import setuptools

with open("README.rst", 'r') as fh:
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
        install_requires=[
            "gitpython",
            "pandas"
        ],
        tests_require=[
            'pytest',
        ],
        extras_require={
            'dev': [
                "sphinx",
            ],
        },
        test_suite='pytest',
        scripts=['bin/meticulous'],
        )
