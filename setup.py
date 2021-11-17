import pathlib

from setuptools import find_packages, setup

from .discpyth import __version__

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

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
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(where="discpyth"),
    python_requires=">=3.8",
    install_requires=["aiohttp", "go_json"],
    extras_require=e_require,
    project_urls={
        "Source": "https://github.com/DiscPyth/DiscPyth/",
    },
)
