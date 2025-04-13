#!/bin/bash

python wrfrun/res/generate_init.py -o wrfrun/res/__init__.py

python -m build -s
