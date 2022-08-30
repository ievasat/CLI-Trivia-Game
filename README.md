# CLI-Trivia-with-curses
Command line trivia quiz game with curses module.

Under the hood, this program consumes [Open Trivia Database](https://opentdb.com/) API.

When run for the first time, it creates sqlite3 database to keep track of stats.

## Installation

- First, clone the repository using command:

```
git clone https://github.com/ievasat/CLI-Trivia-with-curses.git
```

- Access project folder:

```
cd CLI-Currency-Converter
```

- Using a virtual environment is recommended. Run following commands if you wish to use one:

```
pip install virtualenv
virtualenv venv
source venv/bin/activate --> for Mac
venv\Scripts\activate --> for Windows
```

- Install project dependencies:

```
pip install -r requirements.txt
```

- Start the program:

```
python main.py
```

