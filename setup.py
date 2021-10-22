import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="DiscPyth",
    version="0.1.0+planning-stage",  # semver
    description="DiscPyth is an unofficial wrapper in python for the official Discord API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DiscPyth/DiscPyth",
    author="arHSM",
    author_email="hanseungmin.ar@gmail.com",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=find_packages(where="DiscPyth"),
    python_requires=">=3.8",
    install_requires=["aiohttp"],
    project_urls={
        "Source": "https://github.com/DiscPyth/DiscPyth/",
    },
)
