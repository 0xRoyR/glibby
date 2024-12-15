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
        # Development Status
        "Development Status :: 4 - Beta",  # Replace with 5 - Production/Stable if ready for production

        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Information Technology",

        # Topic
        "Topic :: Security",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Topic :: Internet :: WWW/HTTP",

        # License
        "License :: OSI Approved :: MIT License",  # Replace if using a different license

        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",

        # Operating System
        "Operating System :: OS Independent",

        # Natural Language
        "Natural Language :: English",
    ],
    install_requires=['certifi>=2024.8.30', 'charset-normalizer>=3.4.0', 'idna>=3.10', 'requests>=2.32.3', 'urllib3>=2.2.3'],
    python_requires=">=3.6"
)