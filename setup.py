import glob
from setuptools import setup, find_packages

setup(
    name="glibby",
    version="1.0.0",
    description="A tool written in to automate Azure attack paths.",
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    author="Roy Rahamim (0xRoyR)",
    author_email="royraham1@gmail.com",
    url="https://github.com/0xRoyR/Glibby",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    
    package_data={
        'glibby': ['glibby/Templates/*']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Azure",
        "Azure Active Directory",
        "Entra ID"
    ],
    install_requires=['certifi>=2024.8.30', 'charset-normalizer>=3.4.0', 'idna>=3.10', 'requests>=2.32.3', 'urllib3>=2.2.3'],
    python_requires=">=3.6"
)