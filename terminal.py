from event import Event


class Terminal:
	" VT100 series terminal functions wrapper "
	def __init__(self, w, h):
		self.w = w
		self.h = h

	def set_cursor_pos(self, vert, hor):
		" Set the cursor position "
		" Top-Left position : 1;1 "
		" Note : vertical position first, then horizontal "
		self.write('\033[' + str(vert) + ';' + str(hor) + 'H')

	def clear_screen(self):
		" Resets the screen with the appropriate escape code "
		self.write('\033[2J')

	def cursor_home(self):
		" Resets the cursor position to the top-left "
		self.write('\033[H')

	def reset_screen(self):
		" Reset the screen. (clear+cursor_home)"
		self.clear_screen()
		self.cursor_home()

	def write(self, text):
		" Output the given text on the screen at given position "
		pass

	def wait_event(self):
		" Wait for an event (keystroke) comming from the terminal"
		return Event(Event.KEYSTROKE_UNKNOWN)

	# some text style modifier escape codes
	DEFAULT = '\033[0m'
	BOLD = '\033[1m'
	ITALIC = '\033[3m'
	UNDERLINE = '\033[4m'
	BLINKING = '\033[5m'
	INVERTED = '\033[7m'

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

	def set_style_attribute(self, style_attribute=DEFAULT, state=False):
		" Sets the given style attribute for future writes "
		pass

	def print(self, text):
		print(text)
