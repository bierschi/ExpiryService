from setuptools import setup, find_packages

from ExpiryService import __version__, __author__, __email__, __license__, __title__

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open("README.md", encoding='utf-8') as f:
    readme = f.read()

with open("CHANGELOG.rst") as f:
    changelog = f.read()


setup(
    name=__title__,
    version=__version__,
    description="ExpiryService",
    long_description=readme,
    long_description_content_type='text/markdown',
    license=__license__,
    author=__author__,
    author_email=__email__,
    url="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
    python_requires=">=3",
    keywords=["expiryservice", "expire", "service", "notification", "AldiTalk", "Netzclub"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    entry_points={
        "console_scripts": [
            'ExpiryService = ExpiryService.expiryservice:main'
        ],
    },
    zip_safe=False,
)
