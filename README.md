# libminicurses
Minitels are French terminals from the 80's, that supported ascii mode over serial link ([more](https://fr.wikipedia.org/wiki/Minitel)). This library, though, should be usable aswell for VT100 series terminals.    
libminicurses means to provide an easy way of ascii-rendering to the terminal, aswell as keyboard event handling.

## Getting started
### Concepts
This library is meant to provide easy ascii drawing and keyboard input handling in a terminal, especially for the Minitel.  
Because the physical terminal can be painfully slow to refresh (4800 bauds max.), an emulator is provided for fast debugging, which renders directly to the modern terminal emulator.  

Abstraction for the emulator is provided by the classes
* Minitel (minitel.py)
* Emulator/BorderedEmulator (emulator.py)

Minitel is especially configured for the communication standards of the minitel, which should of course be adapted depending on the serial link settings.

### Minimal code
The following code renders a Hello Word on the screen
```python
import minicurses
import emulator

# terminal on which to draw (abstraction layer)
terminal = emulator.BorderedEmulator()

# Root window for the minicurses
rw = minicurses.RootWindow(terminal)
# add a hello world label to it, as position (vertical, horizontal) = (1, 5)
hello_label = minicurses.Label(1, 5, "Hello World")
rw.add(hello_label)
# run the window (press 'Esc' 3 times to exit)
rw.run()
```

Let's analyze :  
* *terminal* is a class wrapping emulated VT100 terminal handling functions such as cursor positioning, ...
* *rw* describes the root window of the minicurses. It acts just like any other window, except it's in charge of rendering to the given terminal  
* *rw.run()* starts the root window's main loop, which by default ends with 'Esc' (must be pressed 3 times in emulator)

### Windows
Windows are the default container provided by the library. They handle a set of children, which can be windows as well, or labels, textboxes, buttons.

###### borders
To make it easier, windows have a native border drawing function, that can be enabled/disabled with the *drawBorder* parameter in the window constructor.  
Note : *drawBorder* is activated by default, except for root windows

###### children
After a window is created, as many children as needed may be added with *Window.add(children)*. Windows then handle the children and forward events down until event is processed

Example :
```python
# create a sub window at position (3,3) of size (20,5)
subw = minicurses.Window(3, 3, 20, 5)
# add a hello world label to it, at position (vertical, horizontal) = (1, 5)
hello_label = minicurses.Label(1, 5, "Hello World")
subw.add(hello_label)
rw.add(subw)
# run the root window
rw.run()
```
As many windows as needed may be nested, too high nesting is not recommended though because it wouldn't be straighforward to understand for the user on a 80x24 characters display.
