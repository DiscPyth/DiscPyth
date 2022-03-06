import argparse
import pathlib
import re
from typing import Literal

parser = argparse.ArgumentParser(
    description="Bump version of the package",
)
parser.add_argument(
    "--level",
    "-l",
    type=str,
    choices=["major", "minor", "patch", "pre", "post", "dev"],
    default="patch",
    help="The level to bump",
    required=False,
)
parser.add_argument(
    "--pre",
    "-p",
    type=str,
    choices=["a", "b", "rc"],
    default="a",
    help="The pre-release identifier",
    required=False,
)

args = parser.parse_args()

HERE = pathlib.Path(__file__).parent.resolve()

PEP440_REGEX = re.compile(
    r"(?P<major>\d{1,})\.(?P<minor>\d{1,})\.(?P<patch>\d{1,})"
    r"(?P<pre_release>(?:a|b|rc)\d*)?(?:(?P<post_release>\.post\d{1,})|"
    r"(?P<dev_release>\.dev\d{1,}))?"
)

VERSION_REGEX = re.compile(r'__version__ = "(.*)"')

with open(HERE / "discpyth/constants.py", "r") as f:
    ver_match = VERSION_REGEX.search(f.read())
    LOCATION = ver_match.span()
    CURRENT_VERSION = ver_match.group(1)


class Version:
    version: str
    major: str
    minor: str
    patch: str
    pre_release: str
    post_release: str
    dev_release: str

    def __init__(self, version: str = CURRENT_VERSION) -> None:
        self.version = version
        # Will never throw a NoneType error dute to initial conditions
        # unless modified by a 3rd party
        (
            self.major,
            self.minor,
            self.patch,
            self.pre_release,
            self.post_release,
            self.dev_release,
        ) = (
            PEP440_REGEX.match(version).groupdict().values()
        )
        self.major = int(self.major)
        self.minor = int(self.minor)
        self.patch = int(self.patch)

    def increment(
        self,
        level: Literal[
            "major", "minor", "patch", "pre_release", "post_release", "dev_release"
        ],
        pre_release: Literal["a", "b", "rc"] = "a",
    ) -> str:
        if level not in {
            "major",
            "minor",
            "patch",
            "pre_release",
            "post_release",
            "dev_release",
        }:
            raise ValueError(f"Invalid level: {level}")

        match level:
            case "major":
                self.major += 1
                self.minor = 0
                self.patch = 0
            case "minor":
                self.minor += 1
                self.patch = 0
            case "patch":
                self.patch += 1
            case "pre_release":
                if self.pre_release is not None:
                    if self.pre_release[-1].isdigit():
                        self.pre_release = (
                            f"{pre_release}{int(self.pre_release[-1]) + 1}"
                        )
                    else:
                        self.pre_release = f"{pre_release}1"
                else:
                    self.pre_release = f"{pre_release}"
            case "post_release":
                if self.post_release is not None:
                    self.post_release = f".post{int(self.post_release[-1]) + 1}"
                else:
                    self.post_release = f".post1"
            case "dev_release":
                if self.dev_release is not None:
                    self.dev_release = f".dev{int(self.dev_release[-1]) + 1}"
                else:
                    self.dev_release = f".dev1"

        return self.construct()

    def construct(self) -> str:
        return (
            f"{self.major}.{self.minor}.{self.patch}"
            f"{self.pre_release if self.pre_release is not None else ''}"
            f"{self.post_release if self.post_release is not None else ''}"
            f"{self.dev_release if self.dev_release is not None else ''}"
        )


if __name__ == "__main__":
    print(f"Bumping '{args.level}' level w/ pre-release as '{args.pre}'!")
    version = Version()
    bumped_version = version.increment(args.level, args.pre)
    with open(HERE / "discpyth/constants.py", "r+") as f:
        init = f.read()
        init = (
            init[: LOCATION[0]]
            + f'__version__ = "{bumped_version}"'
            + init[LOCATION[1] :]
        )
        f.seek(0)
        f.write(init)
        f.truncate()

    with open(HERE / "pyproject.toml", "r+") as f:
        content = f.read()
        content = content.replace(
            f'version = "{CURRENT_VERSION}"',
            f'version = "{bumped_version}"',
            1,
        )
        f.seek(0)
        f.write(content)
        f.truncate()

    print(f"Updated version to '{bumped_version}'")
