from setuptools import setup, find_packages

setup(
    name="wizard_dal",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # List your package dependencies here,
        # for example, SQLAlchemy, pyodbc, etc.
        "SQLAlchemy",
        "pyodbc",
    ],
)