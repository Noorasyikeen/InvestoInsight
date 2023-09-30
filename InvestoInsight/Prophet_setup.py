from setuptools import setup, find_packages

setup(
    name="InvestoInsight-prophet-package",
    version="1.1.1",
    description="Prophet Model Package",
    author="Huiye, Noorasyikeen, Zoey, Kendrick",
    packages=find_packages(),
    install_requires=[
        "prophet"
    ],
)
