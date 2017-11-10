import codecs
import os
import re

from setuptools import setup, find_packages

###############################################################################

NAME = 'pathsjson'

PACKAGES = find_packages(where=".")

META_PATH = os.path.join("pathsjson", "__init__.py")

KEYWORDS = ["data analysis", "data science", "elt"]

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "Intended Audience :: Developers",
               "Topic :: Scientific/Engineering :: Information Analysis",
               "License :: OSI Approved :: MIT License",
               "Programming Language :: Python :: 2.7",
               "Programming Language :: Python :: 3",
               "Programming Language :: Python :: 3.2",
               "Programming Language :: Python :: 3.3",
               "Programming Language :: Python :: 3.4",
               "Programming Language :: Python :: 3.5",
               "Programming Language :: Python :: 3.6",
               "Topic :: Software Development :: Build Tools",
               "Topic :: Software Development :: Code Generators",
               "Topic :: System :: Filesystems",
               "Topic :: Utilities"]

INSTALL_REQUIRES = ['appdirs', 'jsonschema']

##############################################################################

SELF_DIR = os.path.abspath(os.path.dirname(__file__))


def read_file_safely(*path_parts):
    with codecs.open(os.path.join(SELF_DIR, *path_parts), "rb", "utf-8") as f:
        return f.read()


META_FILE = read_file_safely(META_PATH)

META_VARS_RE = re.compile(r"^__([_a-zA-Z0-9]+)__ = ['\"]([^'\"]*)['\"]", re.M)

META_VARS = dict(META_VARS_RE.findall(META_FILE))

###############################################################################

if __name__ == "__main__":
    setup(
        name=NAME,
        description=META_VARS["description"],
        license=META_VARS["license"],
        url=META_VARS["uri"],
        version=META_VARS["version"],
        author=META_VARS["author"],
        author_email=META_VARS["email"],
        maintainer=META_VARS["author"],
        maintainer_email=META_VARS["email"],
        keywords=KEYWORDS,
        long_description=read_file_safely("README.rst"),
        packages=PACKAGES,
        package_dir={"pathsjson": "pathsjson"},
        package_data={"pathsjson": ["pathsjson/*.json"]},
        entry_points={'console_scripts': ['pathsjson = pathsjson.cli:main']},
        include_package_data=True,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
    )
