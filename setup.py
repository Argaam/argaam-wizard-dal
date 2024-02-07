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
    include_package_data=True,
    author="Abdul Akbar Khan",
    author_email="akbar.khan@argaam.com",
    description="Data Access Layer for Argaam Wizard",
    url="https://github.com/Argaam/argaam-wizard-dal",
)