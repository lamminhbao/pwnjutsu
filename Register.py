# ver 1.44
from Debugger import Debugger
from util import white_list

class Register(Debugger):

	# Register('eax')
	# e.g. 'eax'
	def __init__(self, register_name):
		size = self.calc_size(register_name)

		# if size = 0, the register is invalid
		if not size:
			raise ValueError('Invalid register: %s' % (register_name))

		# register's attributes
		self.__size = size
		self.__name = register_name
		# prevent from overflowing
		self.__max_value = 256 ** self.__size

		##1.43
		# removed self.__value

	@staticmethod
	#get size of a register
	def calc_size(s):
		# white list of registers
		return sum((s in reg)*reg[0] for reg in white_list)

	def get_size(self):
		return self.__size

	def get_value(self):
		return self.get_runtime_value()

	def get_name(self):
		return self.__name

	#hook to debugger and get value
	def get_runtime_value(self):
		try:
			return super(Register, self).get_register_value(self.__name)
		except Exception as e:
			print e
			exit(-1)

	def __str__(self):
		# green
		tmp = '\033[0;32;40m'
		tmp += '%s R[0x%x]' % (self.__name, self.get_runtime_value())
		tmp += '\033[0m'
		return tmp

	## 1.44, support print in list
	def __repr__(self):
		return self.__str__()

	#operator override
	## 1.43, update operator
	def __add__(self, other):
		return (self.get_runtime_value() + other) % self.__max_value

	def __radd__(self, other):
		return (self.get_runtime_value() + other) % self.__max_value

	def __sub__(self, other):
		return (self.get_runtime_value() - other) % self.__max_value

	def __rsub__(self, other):
		return (other - self.get_runtime_value()) % self.__max_value
	
	def __mul__(self, other):
		return (self.get_runtime_value() * other) % self.__max_value

	def __rmul__(self, other):
		return (self.get_runtime_value() * other) % self.__max_value

	##1.43
	def __int__(self):
		return self.get_runtime_value()

def test():
	## this test is out of date
	debug = Debugger('../test-case/case01')
	print 1, debug._Debugger__prompt
	eip = Register('eip')
	eax = Register('eax')
	a = eax
	b = set(tuple(eax))

	print "==>", a
	print "==>", b
	#rbx = Register('rbx')
	ah  = Register('ah')
	bl  = Register('bl')
	ax  = Register('ax')
	#axy = Register('axy')
	print eip
	print "size:", eip.get_size()
	print "value:", hex(eip.get_value())
	debug.step()
	print "value:", hex(eip.get_value())
	print "runtime value:", hex(eip.get_runtime_value())
	print hex(1 + eip - 3*ax*2)
	print "test ok!!!"

if __name__ == '__main__':
	test()