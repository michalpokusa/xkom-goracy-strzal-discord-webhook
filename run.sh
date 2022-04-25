# Export from specified .env file lines that do not have '#' inside
export $(cat $1 | grep -v '#'| xargs)

# Run the program
python3 program.py
