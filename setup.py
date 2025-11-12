from setuptools import setup, find_packages

setup(
    name="queuectl",
    version="0.1",
    packages=find_packages(),
    install_requires=["typer", "rich"],
    entry_points={
        "console_scripts":[
            "queuectl=queuectl.cli.main:app"
        ]
    }
)