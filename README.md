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
# 1. Start venv
python3 -m venv venv
source venv/bin/activate
# 2. Put you tablatures as text files in tabs directory
# 3. Run this file (and you'll get all the help you need)
./tabs2notes.py --help
```

## Development
```
# 1. Load the venv (you guessed it)
# 2. When you change Python libs
pip freeze > requirements.txt
```

### Testing
Check you don't break stuff
```
python -m unittest
```

### Directory structure
We have following directories to keep things neat:
* src : all the Python modules
* tabs : we look here for tablatures
* tests : pretty obvious
* venv : this project specific Python virtualenv