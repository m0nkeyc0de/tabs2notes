# Guitar tabs to notes
Convert a guitar tablature in text format to notes names

## Bootstrap
A Python3 virtualenv is needed to run the project.
```
# Go into the project root dir
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Usage
```
# Start venv
python3 -m venv venv
source venv/bin/activate
# Run this file (and you'll get help)
./tabs2notes.py
```

## Development
```
# 1. Load the venv (you guessed it)
# 2. When you change Python libs
pip freeze > requirements.txt
```