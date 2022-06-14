# Clickr-py

![Clickr logo](https://github.com/mircea007/clickr/blob/main/img/logo.png?raw=true)

A python corss-platform autoclicker.

## Features

* Toggle key is Caps Lock (because who really uses it?). Caps Lock is also closer to WASD keys so it's easy to reach
* Anti-bot detection (by randomizing intervals between clicks, in the future i will add buterfly/dracgclick mode for even better stealth)
* Works for both right and left click

## Running the precompiled binary

First, download the binary form the releases section then run it like this:

```bash
./clickr --cps 10 # on linux
clickr.exe --cps 10 # on windows
```

## Running with python

### Requirements

You need to install pynput:
```bash
pip install pynput
```

For the Linux version you also need to install xdo:

```bash
pip install python-libxdo
```

### Running

```bash
python main.py --cps 10
```

To close the program press the END key
To toggle autoclicking press the Caps Lock key.

### Building

To compile the script use pyinstaller:
```bash
pip install pyinstaller # do this only one time of couse
pyinstaller --onefile main.py
```

You will find the executable in `./dist/`