from setuptools import find_packages, setup  # type: ignore

setup(
    name="stactools-pipelines",
    version="0.0.1",
    python_requires=">=3.9",
    author="Development Seed",
    packages=find_packages(),
    include_package_data=True,
)
