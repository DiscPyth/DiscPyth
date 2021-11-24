import pathlib
import re

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

verre = re.compile(r"\"(.+)\"")

with (here / "discpyth/__init__.py") as init:
    verline = init.readlines()[1]

__version__ = verre.findall(verline)[0]

e_require = {
    "dev": [
        "Sphinx",   
        "pylint",
        "black",
        "flake8",
        "isort",
        "mypy",
    ]
}

setup(
    name="discpyth",
    version=__version__,  # semver
    description="DiscPyth is an unofficial wrapper in python for the official Discord API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DiscPyth/DiscPyth",
    author="arHSM",
    author_email="hanseungmin.ar@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        "License :: OSI Approved :: MIT License",
    ],
    packages=find_packages(where="discpyth"),
    python_requires=">=3.8",
    install_requires=["aiohttp", "go_json"],
    extras_require=e_require,
    project_urls={
        "Source": "https://github.com/DiscPyth/DiscPyth/",
        "Documentation": "https://discpyth.github.io/pages/dpth",
    },
    package_data={
        "discpyth": ["py.typed"],
    },
)
