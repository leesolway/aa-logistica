from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aa-logistica",
    version="0.1.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leesolway/aa-logistica",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Environment :: Web Environment",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "django>=3.2,<5.0",
        "allianceauth>=3.0.0",
        "allianceauth-app-utils>=1.0.0",
        "django-eveonline-sde>=0.0.1b2",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
            "black",
            "flake8",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="allianceauth eve online logistics",
)
