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

### Custom controls
It is possible to create custom controls by inheriting any class provided by the library.  
The following example shows how to create a custom window :
```python
import minicurses
from minicurses import Window
import emulator

class MyTitledWindow(Window):
	def __init__(self, x, y, w, h, title=""):
		super().__init__(x, y, w, h)
		self.title_label = minicurses.Label(0, 1, title)
		self.add(self.title_label)

terminal = emulator.BorderedEmulator()
rw = minicurses.RootWindow(terminal)
tw1 = MyTitledWindow(3, 3, 30, 5, "Titled Window 1")
tw2 = MyTitledWindow(10, 3, 30, 5, "Titled Window 2")
rw.add(tw1)
rw.add(tw2)
rw.run()
```

Which gives the following result :
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                                                                               ║
║                                                                               ║
║   +Titled Window 1-------------+                                              ║
║   |                            |                                              ║
║   |                            |                                              ║
║   |                            |                                              ║
║   +----------------------------+                                              ║
║                                                                               ║
║                                                                               ║
║   +Titled Window 2-------------+                                              ║
║   |                            |                                              ║
║   |                            |                                              ║
║   |                            |                                              ║
║   +----------------------------+                                              ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

## Events
Widgets (Windows, Label, ...) may handle a set of events or forward them down to its active child.  
The above example show the default handling of events : with the Up/Down arrows, you may change the active child of the Root Window (Notice the cursor position change).  
If you hit enter, the active child of the root window (one of the titled windows) will be selected, it will have focus and handle events. The parent (root) window will forward events down to it.

#### Event structure
The minicurses.WindowEvent class describes any event that may be handled by the widgets. It consists in a *type* field that describes the event type and a *key* field, which is the key pressed in case of an ascii keystroke event.

#### Event handling
*Widget.handle_event(event)* is  in charge of handling the event forwarded by the parent widget.
Default windows forward events down to the active child.
If the window is selected, the Up/Down key select the active child in the window.  
Hitting enter gets the selected window to send a 'FOCUS' event to its active child, which may then accept or deny focus.
Return values of *handle_event* are important as they allows children widgets to send events back to their parent widget (DEFOCUS, ...).

#### Custom event handling
You may add create your own behavior upon event triggering for a given control. Simply override the *handle_event* method. For instance, with the previous example :

```python
...
from minicurses import Window, WindowEvent
...
class MyTitledWindow(Window):
	def __init__(self, x, y, w, h, title=""):
		super().__init__(x, y, w, h)
		self.title_label = minicurses.Label(0, 1, title)
		self.add(self.title_label)

	def handle_event(self, event):
		if event and event.type == WindowEvent.FOCUS:
			self.title_label.text = "Window has been selected"
		return super().handle_event(event)
```

If you hit enter, the root window will send a focus event to the child window, which will change its title, then have the default behavior (accept focus).  
Note that events can be *None*, which is why *if event* is required

#### Passive children
You may have noticed that by hitting enter twice, the subwindow will select its title as selected widget.
This can be an issue because such labels may not be meant be selected, which is why children can be added as passive to a window using *Window.add_passive(child)*. This allows to have children displayed without being processed in the event handling.
