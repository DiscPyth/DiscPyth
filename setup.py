import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

e_require = {
    "dev": [
        "Sphinx==4.2.0",
        "pycodestyle==2.8.0",
        "pylint==2.11.1",
        "black==21.9b0",
        "flake8==4.0.1",
        "isort==5.9.3",
        "mypy==0.910",
    ]
}

setup(
    name="discpyth",
    version="0.1.0b1",  # semver
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
    packages=find_packages(where="DiscPyth"),
    python_requires=">=3.8",
    install_requires=["aiohttp", "gopyjson"],
    extras_require=e_require,
    project_urls={
        "Source": "https://github.com/DiscPyth/DiscPyth/",
    },
)
