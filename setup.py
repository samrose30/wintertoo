import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wintertoo",
    version="0.0.1",
    author="Danielle Frostig, Viraj Karambelkar, Robert Stein",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/winter-telescope/wintertoo",
    keywords="astronomy image WINTER",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8',
    install_requires=[
        "astropy",
        "astroquery",
        "docker",
        "pandas",
        "psycopg2-binary",
        "jupyter",
        "matplotlib",
        "numpy",
        "pandas",
        "wtforms",
        "sqlalchemy",
        "astroplan",
        "email_validator",
        "pytz"
    ],
    # package_data={'app': ['static/config/*.json']}
)
