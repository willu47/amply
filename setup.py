from setuptools import setup, find_packages

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open("AUTHORS", "r") as fh:
    authors = []
    text_authors = fh.readlines()
    for author in text_authors:
        authors.append(author.split("<")[0].strip())

setup(
    name="amply",
    packages=find_packages("src"),
    license='Eclipse Public License 1.0 (EPL-1.0)',
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["docutils>=0.3", "pyparsing"],
    package_dir={"": "src"},
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "": ["*.txt", "*.rst"],
    },

    # metadata to display on PyPI
    author=",".join(authors),
    author_email="wusher@kth.se",
    description="Amply allows you to load and manipulate AMPL/GLPK data as Python data structures",
    long_description_content_type="text/x-rst",
    long_description=long_description,
    keywords="ampl gmpl",
    url="http://github.com/willu47/amply",   # project home page, if any
    project_urls={
        "Bug Tracker": "http://github.com/willu47/amply/issues",
        "Documentation": "http://github.com/willu47/amply/README.rst",
        "Source Code": "http://github.com/willu47/amply",
    },
    classifiers=[
        "License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)"
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
)
