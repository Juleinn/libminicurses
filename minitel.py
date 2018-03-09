import serial
import time
from event import Event
from terminal import Terminal


class Minitel(Terminal):
	def __init__(self, port, baudrate=4800):
		super().__init__(80, 24)
		self.stty = serial.Serial(
			port,
			baudrate=baudrate,
			bytesize=7,
			parity=serial.PARITY_EVEN,
			stopbits=serial.STOPBITS_ONE
		)

	def wait_event(self):
		# clear the input buffer from any previous junk data
		self.stty.reset_input_buffer()
		# the input buffer used for multiple-bytes inputs (ex. LF)
		# readall is non-blocking, use read() first
		buff = self.stty.read()
		# add some delay here to let the slow terminal input its strokes
		time.sleep(0.1)
		# append the rest of it if needed
		buff += self.stty.read_all()

		return Event.parse_event(buff)

	def write(self, text):
		self.stty.write(text.encode('utf-8'))

	def clear_screen(self):
		self.write('\033[2J')

	def cursor_home(self):
		self.write('\033[H')

	def reset_screen(self):
		self.clear_screen()
		self.cursor_home()

	def set_cursor_pos(self, x, y):
		self.write('\033[' + str(x) + ';' + str(y) + 'H')

	def down(self):
		self.write('\033[1B')
		self.write('\033[1D')

	def draw_square(self, x, y, w, h, hr='-', vr='|', c='+'):
		self.set_cursor_pos(x, y)
		self.write(c)
		for i in range(w - 2):
			self.write(hr)
		self.write(c)
		self.set_cursor_pos(x, y + 1)
		for i in range(h - 2):
			self.write(vr)
			self.down()
		self.write(c)
		for i in range(w - 2):
			self.write(hr)
		self.set_cursor_pos(x + w - 1, y + 1)
		for i in range(h - 2):
			self.write(vr)
			self.down()
		self.write(c)

	def draw_template(self, x, y, template):
		self.set_cursor_pos(x, y)
		f = open(template)
		substrings = f.read().split('\n')
		for i in range(len(substrings)):
			self.set_cursor_pos(x, y + i)
			self.write(substrings[i])

	def draw_text(self, text, x, y):
		self.set_cursor_pos(x, y)
		self.write(text)

	def text_prompt(self, pos=None, secret=False):
		if pos is not None:
			self.set_cursor_pos(pos[0], pos[1])

		self.stty.reset_input_buffer()
		buff = ""
		value = ""
		while value != '\r':
			value = self.stty.read().decode('utf-8')
			buff = buff + value
			if secret:
				self.write('*')
			else:
				self.write(value)
		return buff
