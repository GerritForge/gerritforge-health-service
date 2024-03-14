from setuptools import setup

setup(
    name="gymgerrit",
    version="0.0.2",
    install_requires=[
        "gymnasium==0.29.1",
        "gitdb==4.0.11",
        "gitpython==3.1.42",
        "smmap==5.0.1",
    ],
    py_modules=["gymgerrit"],
    author="Marcin Czech",
    author_email="maczech@gmail.com",
)
