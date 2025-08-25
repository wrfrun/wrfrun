#!/bin/bash

$PYTHON "$SRC_DIR"/wrfrun/res/generate_init.py -o "$SRC_DIR"/wrfrun/res/__init__.py

pip install "$SRC_DIR" -v
