# 1p-tool

DEPRECATED: Useful reference for pyonepassword, basic templating, poetry and Click lib usage.
I won't offer support on this codebase, but please feel free to copy and use whatever code you feel is useful.

## About
This is a cli helper script for 1password. It can create an ssh session with a specified PEM file stored in 1password. Useful if you have lots of SSH keys.
This script also allows for replacing placeholders in config files with values stored in 1password. This is particularly useful for CI/CD pipelines.
Please keep in mind that [1password has a CI/CD integration](https://developer.1password.com/docs/ci-cd/), and this tool should only be used if you have A LOT of different credentials to put into config files, or you're using a windows runner which 1password's integrations doesn't support.

## Installation
~~This script relies on a slightly modified version of pyonepassword. To install it, run the following command.~~
~~`python -m pip install 'pyonepassword @ git+https://github.com/Rom3dius/pyonepassword.git@main'`~~
My changes to pyonepassword have been merged!

This projects contains a setup.py file. If you'd like to install globally simply run `pip install .` in the project directory.

### Shell Completion
If you installed the tool globally, see [this link](https://click.palletsprojects.com/en/8.1.x/shell-completion/) for command completion.
