from terminal import Terminal
import getch
from event import Event


class Emulator(Terminal):
	" VT100-series terminal functions wrapper (emulated terminal) "
	# log LOGLEN lines
	LOGLEN = 10

	def __init__(self):
		super().__init__(80, 24)
		self.log = []

	def write(self, text):
		print(text, end='', flush=True)

	def wait_event(self):
		" Wait events based on getch "
		buff = getch.getch()
		if buff == '\033':
			# two other strokes comming
			buff += getch.getch()
			buff += getch.getch()

			# patch esc button (must input 3 escapes)
			if buff[2] == '\033':
				buff = '\033'

		# patch modern unix carriage return (instead of LF)
		if buff == '\n':
			buff = '\r'

		# patch backspace codes differences from \x7f to \x08
		if buff == '\x7f':
			buff = '\x08'

		return Event.parse_event(buff.encode('utf-8'))

	def print(self, text):
		self.log.append(text)
		if len(self.log) > Emulator.LOGLEN:
			self.log = self.log[(len(self.log) - Emulator.LOGLEN):]

	def reset_screen(self):
		super().reset_screen()
		self.set_cursor_pos(26, 0)
		for item in self.log:
			print(item)


class BorderedEmulator(Emulator):
	" Same as Emulator except with an outline around the drawing area "
	def __init__(self):
		super().__init__()
		self.draw_border()

	def set_cursor_pos(self, vert, hor):
		super().set_cursor_pos(vert + 1, hor + 1)

	def cursor_home(self):
		self.set_cursor_pos(2, 2)

	def reset_screen(self):
		super().reset_screen()
		self.draw_border()

	def draw_border(self):
		self.set_cursor_pos(0, 0)
		self.write('╔')
		for i in range(self.w - 1):
			self.write('═')
		self.write('╗')
		for i in range(self.h):
			self.set_cursor_pos(i + 1, 0)
			self.write('║')
			self.set_cursor_pos(i + 1, self.w)
			self.write('║')
		self.set_cursor_pos(self.h + 1, 0)
		self.write('╚')
		for i in range(self.w - 1):
			self.write('═')
		self.write('╝')
