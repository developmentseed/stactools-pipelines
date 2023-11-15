from typing import List

from setuptools import find_packages, setup  # type: ignore

aws_cdk_extras = [
    "aws-cdk-lib==2.45.0",
    "aws-cdk.aws-lambda-python-alpha==2.45.0a0",
    "constructs>=10.0.0",
]

install_requires: List[str] = []

extras_require_test = [
    "flake8",
    "black",
    "pytest-cov",
    "pytest",
]

extras_require_dev = [
    *extras_require_test,
    *aws_cdk_extras,
    "aws-lambda-powertools",
    "boto3",
    "pydantic",
    "pydantic-settings" "pyyaml",
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
    name="stactools-pipelines",
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
