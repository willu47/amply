from setuptools import setup, find_packages
setup(
    name="Amply",
    version="0.1",
    packages=find_packages("src"),

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["docutils>=0.3"],
    package_dir={"": "src"},
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
        # And include any *.msg files found in the "hello" package, too:
        "hello": ["*.msg"],
    },

    # metadata to display on PyPI
    author="Q. Lim, W. Usher",
    author_email="wusher@kth.se",
    description="Amply allows you to load and manipulate AMPL data as Python data structures",
    keywords="ampl gmpl",
    url="http://github.com/coin-or/amply",   # project home page, if any
    project_urls={
        "Bug Tracker": "http://github.com/coin-or/amply/issues",
        "Documentation": "http://github.com/coin-or/amply/README.rst",
        "Source Code": "http://github.com/coin-or/amply",
    },
    classifiers=[
        "License :: OSI Approved :: Python Software Foundation License"
    ]

    # could also include long_description, download_url, etc.
)