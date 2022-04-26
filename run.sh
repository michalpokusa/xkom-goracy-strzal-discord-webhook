#! /bin/bash

# Changing the working directory
cd $(dirname $0)

# Generating file to source from .env file
sed '/^\w/ s/^/export /' $1 > $1.export

# Sourcing the generated file
source $1.export

# Activating Python venv
source .venv/bin/activate

# Running the program
python3 program.py > output.log
