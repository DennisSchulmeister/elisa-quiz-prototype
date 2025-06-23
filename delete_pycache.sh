#! /bin/sh
find -name .pytest_cache -exec rm -rf {} \;
find -name __pycache__ -exec rm -rf {} \;