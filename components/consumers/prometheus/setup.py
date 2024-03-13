from setuptools import setup


setup(
    name="gerritscraper",
    version="0.0.1",
    install_requires=[
        "prometheus-client==0.20.0",
        "schedule==1.2.0",
        "requests==2.31.0",
    ],
    py_modules=["gerritscraper"],
)
