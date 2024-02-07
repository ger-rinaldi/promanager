from setuptools import setup

setup(
    name="db_cli",
    version="0.1.0",
    py_modules=["app"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "db-cli = db_cli:db_setup",
        ],
    },
)

# The magic is in the entry_points parameter.
# Below console_scripts, each line identifies one console script.
# The first part before the equals sign (=) is the name of the script
# that should be generated, the second part is the import
# path followed by a colon (:) with the Click command.

# That’s it.
