from event import Event
from terminal import Terminal


class WindowEvent(Event):
	" Describes events that may occur to minicurses windows "
	FOCUS = 'FOCUS'
	DEFOCUS = 'DEFOCUS'

	def init(self, eventtype, key=""):
		" Init. the window event "
		" eventtype : describes the type of the event "
		" key : if eventtype = Event.KEYSTROKE_ASCII, the actual keychar "
		super().__init__(eventtype, key)


class Widget():
	" Parent class for all displayable minicurses objects "
	def __init__(self, x, y):
		" x, y : position of the widget relatively to the parent "
		self.x = x
		self.y = y
		self.selected = False

	def handle_event(self, event):
		" Handles event passed by the parent class "
		return None

	def get_matrix(self):
		" returns the drawing matrix for the widget "
		return []

	def set_selected(self, selected):
		" Sets the selection state of the widget "
		self.selected = selected
		pass

	def get_cursor_pos(self, recursive=False):
		" Returns the cursor position as indicated by the widget "
		" relatively to the widget's origin "
		return (self.y, self.x)


class Label(Widget):
	STYLE_DEFAULT = 1 << 0
	STYLE_BOLD = 1 << 1
	STYLE_UNDERLINE = 1 << 2
	STYLE_BLINKING = 1 << 3
	STYLE_INVERTED = 1 << 4

	STYLE_PREFIX_MAP = {
		STYLE_DEFAULT: '\033[0m',
		STYLE_BOLD: '\033[1m',
		STYLE_UNDERLINE: '\033[4m',
		STYLE_BLINKING: '\033[5m',
		STYLE_INVERTED: '\033[7m'
	}

	" Text display on screen "
	def __init__(self, x, y, text, style=STYLE_DEFAULT):
		" x, y : position relatively to parent container "
		" text : the text to display"
		super().__init__(x, y)
		self.text = text
		self.style = style

	def get_matrix(self):
		if self.style != self.STYLE_DEFAULT:
			return [[(c, self.style) for c in self.text]]
		else:
			return [[c for c in self.text]]

	def get_cursor_pos(self, recursive=True):
		return super().get_cursor_pos()


class MultilineLabel(Label):
	GRAVITY_UP = 0
	GRAVITY_DOWN = 1

	def __init__(
		self, x, y, w=None, h=None, gravity=GRAVITY_UP, scroll=0, text=""):
		super().__init__(x, y, text)
		self.w = w
		self.h = h
		self.gravity = gravity
		self.scroll = scroll

	def get_matrix(self):
		lines = []
		for line in self.text.splitlines():
			lines += [line[i:self.w + i] for i in range(0, len(line), self.w)]

		# prevent overscrolling may be disabled later
		self.scroll = len(lines) - self.h if self.scroll \
			> len(lines) - self.h else self.scroll
		self.scroll = self.scroll if self.scroll > 0 else 0

		# cut if too many lines to show
		if self.h:
			if self.gravity == self.GRAVITY_UP:
				lines = lines[self.scroll:self.h + self.scroll]
			else:
				# patch the slice[x:0] != slice[x:] behavior
				if self.scroll == 0:
					lines = lines[-self.h:]
				else:
					lines = lines[-(self.h + self.scroll):-self.scroll]

		# actually write the lines here
		matrix = [[l for l in line.ljust(self.w)] for line in lines]

		return matrix

	def scroll_lines(self, n):
		self.scroll += n
		print("Set scrolling : " + str(self.scroll))


class Button(Label):
	" A clickable label "

	def onClick(self):
		" Run on button click"
		pass

	def handle_event(self, event):
		if event.type == WindowEvent.FOCUS:
			self.onClick()


class AsciiArt(Widget):
	" Static Ascii Art image to be displayed "
	" useful for templates or logos"

	def __init__(self, x, y, asciifile, w=None, h=None):
		super().__init__(x, y)
		self.matrix = []
		with open(asciifile, 'r') as asciiBytes:
			for line in asciiBytes:
				self.matrix.append(list(line.replace('\n', '')))

		maxLen = max([len(line) for line in self.matrix])
		# pad every other line
		for line in self.matrix:
			line += ' ' * (maxLen - len(line))

		# transpose matrix
		# self.matrix = [e for e in zip(*self.matrix)]

		self.w = maxLen
		self.h = len(self.matrix[0])

	def get_matrix(self):
		return self.matrix


class Textbox(Label):
	" Editable text display "
	def __init__(self, x, y, text="", secret=False, maxw=None):
		super().__init__(x, y, text)
		self.secret = secret
		self.maxw = maxw

	def handle_event(self, event):
		if event.type == Event.KEYSTROKE_ASCII:
			self.text += event.key
		elif event.type == Event.KEYSTROKE_BS:
			self.text = self.text[:len(self.text) - 1]

	def get_matrix(self):
		if not self.secret:
			matrix = super().get_matrix()
		else:
			matrix = [['*' for c in self.text]]
		if self.maxw:
			return [matrix[0][len(matrix) - self.maxw:]]
		else:
			return matrix

	def set_text(self, text):
		" Set the text on the run "
		self.text = text

	def get_cursor_pos(self, recursive=True):
		if self.maxw and len(self.text) > self.maxw:
			return (self.y + self.maxw, self.x)
		else:
			return (self.y + len(self.text), self.x)


class Window(Widget):
	" Container with possible border drawing "
	def __init__(
		self, x, y, w, h, drawBorder=True,
		corner='+', vchar='|', hchar='-'):
		" x, y : position relatively to parent container "
		" w, h : size "
		" drawBorder : draw the border if set to True "
		" corner, vchar, hchar : border drawing ascii chars "
		super().__init__(x, y)
		self.w = w
		self.h = h
		self.children = []
		self.passive_children = []
		self.active = 0
		self.corner = corner
		self.vchar = vchar
		self.hchar = hchar
		self.drawBorder = drawBorder

	def handle_event(self, event):
		" Handle events passed by parent container "
		# discard empty 'None' events
		if event:
			if self.selected:
				if event.type == Event.KEYSTROKE_CR:
					if len(self.children) > 0:
						self.handle_event(
							self.children[self.active].handle_event(WindowEvent(WindowEvent.FOCUS)))
					return None
				elif event.type == Event.KEYSTROKE_ESC:
					self.selected = False
					return WindowEvent(WindowEvent.FOCUS)
				elif event.type == Event.KEYSTROKE_DOWN:
					self.select_children(self.active + 1)
					return None
				elif event.type == Event.KEYSTROKE_TAB:
					self.select_children(self.active + 1)
					return None
				elif event.type == Event.KEYSTROKE_UP:
					self.select_children(self.active - 1)
					return None

			if event.type == WindowEvent.FOCUS:
				self.selected = True
				return WindowEvent(WindowEvent.DEFOCUS)
			elif event.type == WindowEvent.DEFOCUS:
				self.selected = False
				return WindowEvent(WindowEvent.DEFOCUS)
			elif len(self.children) > 0:
				return self.handle_event(self.children[self.active].handle_event(event))
		else:
			return None

	def forward_event(self, event):
		if len(self.children) > 0:
			self.children[self.active].handle_event(event)

	def select_children(self, childrenId):
		if len(self.children) > 0:
			self.active = childrenId % len(self.children)

	def get_matrix(self):
		# generate a new matrix here
		matrix = [[' ' for w in range(self.w)] for h in range(self.h)]

		# add the border if needed
		if self.drawBorder:
			for i in range(self.w):
				matrix[0][i] = '-'
				matrix[self.h - 1][i] = '-'
			for i in range(self.h):
				matrix[i][0] = '|'
				matrix[i][self.w - 1] = '|'
			matrix[0][0] = '+'
			matrix[0][self.w - 1] = '+'
			matrix[self.h - 1][self.w - 1] = '+'
			matrix[self.h - 1][0] = '+'

		# merge children matrices down here
		for child in self.children:
			Window.merge_matrices(matrix, child.get_matrix(), child.x, child.y)
		for child in self.passive_children:
			Window.merge_matrices(matrix, child.get_matrix(), child.x, child.y)

		return matrix

	def add(self, child):
		self.children.append(child)

	def add_passive(self, pchild):
		self.passive_children.append(pchild)

	def merge_matrices(m1, m2, x, y):
		" Merge m2 on m1 at position x, y "
		for i in range(min(len(m2), len(m1) - x)):
			for j in range(min(len(m2[i]), len(m1[i]) - y)):
				m1[i + x][j + y] = m2[i][j]

	def get_cursor_pos(self, recursive=True):
		if len(self.children) > 0 and recursive:
			if self.selected:
				cpos = self.children[self.active].get_cursor_pos(False)
			else:
				cpos = self.children[self.active].get_cursor_pos()
			return tuple(map(lambda x, y: x + y, cpos, (self.y, self.x)))
		else:
			return (self.y, self.x)


class RootWindow(Window):
	def __init__(self, terminal, drawBorder=False):
		global print
		super().__init__(0, 0, 80, 24, drawBorder)
		self.terminal = terminal
		self.set_selected(True)
		print = self.terminal.print
		self.selected = True
		self.running = True
		self.matrix = [[' ' for e in range(self.w)] for j in range(self.h)]
		self.retVal = None

	def run(self):
		self.terminal.reset_screen()
		while self.running:
			self.run_loop()
		return self.retVal

	def quit(self, retVal=None):
		self.retVal = retVal
		self.running = False

	def run_loop(self):
		self.render()
		# replace cursor at right position
		cpos = self.get_cursor_pos()
		self.terminal.set_cursor_pos(cpos[1] + 1, cpos[0] + 1)
		# Wait for event
		event = self.terminal.wait_event()
		self.handle_event(event)

	def handle_event(self, event):
		if event and event.type == Event.KEYSTROKE_ESC and self.selected:
			self.running = False
			return
		else:
			return super().handle_event(event)

	def get_diff_matrix(self, oldMatrix):
		for i in range(self.h):
			for j in range(self.w):
				if oldMatrix[i][j] != self.matrix[i][j]:
					oldMatrix[i][j] = '!'
				else:
					oldMatrix[i][j] = ' '
		return oldMatrix

	def render(self):
		# actually do the matrix rendering here
		# check for update matrix here
		# deepcopy the matrix
		oldMatrix = [e for e in self.matrix]
		self.matrix = self.get_matrix()
		diffMatrix = self.get_diff_matrix(oldMatrix)

		mode = Terminal.STYLE_DEFAULT
		self.terminal.write(Terminal.DEFAULT)

		for i in range(self.h):
			for j in range(self.w):
				if diffMatrix[i][j] == '!':
					if j == 0 or (j > 0 and diffMatrix[i][j - 1] != '!'):
						self.terminal.set_cursor_pos(i + 1, j + 1)

					if type(self.matrix[i][j]) == tuple and self.matrix[i][j][1] != mode:
						self.terminal.write(Terminal.DEFAULT)
						st = self.matrix[i][j][1]
						for e in range(5):
							if st & (1 << e) != 0:
								self.terminal.write(Terminal.STYLE_PREFIX_MAP[st & (1 << e)])
						mode = st
					elif type(self.matrix[i][j]) == str and mode != Terminal.STYLE_DEFAULT:
						mode = Terminal.STYLE_DEFAULT
						self.terminal.write(Terminal.DEFAULT)

					if type(self.matrix[i][j]) == tuple:
						self.terminal.write(self.matrix[i][j][0])
					else:
						self.terminal.write(self.matrix[i][j])
