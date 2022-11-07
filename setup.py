from typing import List

from setuptools import find_packages, setup  # type: ignore

aws_cdk_version = "1.18.0"
aws_cdk_extras = [
    f"aws_cdk.{aws_cdk_package}=={aws_cdk_version}"
    for aws_cdk_package in [
        "core",
    ]
]

install_requires: List[str] = []

extras_require_test = [
    *aws_cdk_extras,
    "flake8",
    "black",
    "pytest-cov",
    "pytest",
]

extras_require_dev = [
    *extras_require_test,
    "aws-lambda-powertools",
    "boto3",
    "pydantic",
    "pyyaml",
    "docker",
    "isort",
    "mypy",
    "nodeenv",
    "pre-commit",
    "pre-commit-hooks",
    "pyright",
]

extras_require = {
    "test": extras_require_test,
    "dev": extras_require_dev,
}

setup(
    name="aws-asdi-pipelines",
    version="0.0.1",
    python_requires=">=3.9",
    author="Development Seed",
    packages=find_packages(),
    package_data={
        ".": [
            "cdk.json",
        ],
    },
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
)
