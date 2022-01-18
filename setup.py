import setuptools
from os.path import join, dirname

def read(fname):
    with open(join(dirname(__file__), fname)) as f:
        return f.read()

setuptools.setup(
    name="firemap",
    version="0.0.1",
    author="Ruben Remelgado",
    author_email="ruben.remelgado@gmail.com",
    description="Mapping of fire regimes using Google Earth Engine",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/RRemelgado/firemap",
    project_urls={
        "Bug Tracker": "https://github.com/RRemelgado/firemap/issues",
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved :: MIT License'
    ],
    packages=("firemap",),
    install_requires=[
    "progress",
    "earthengine-api",
    "google-api-python-client",
    "pyCrypto",
    "rasterio",
    "numpy",
    "glob2",
    "RLE"]
)
