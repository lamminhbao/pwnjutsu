# ver 1.44
from Register import Register
from Debugger import Debugger
from util import *

class Address(Debugger):

	@staticmethod	
	#note that this function get output of debugger as input
	#so we can assume that there are no malicious input for this function
	def parse(s):
		return s.split(':')[-1].strip('[]')
		
	# 1. Address(string)
	# 	e.g. [ecx-0x4]
	# 	e.g. 0x804a01c
	# 	e.g. [ebx+4*esi]
	# 2. Address(int)
	# 3. Address(TaintObject) -> discard
	def __init__(self, *args, **kwargs):
		args_len = len(args)

		if args_len == 1:
			if isinstance(args[0], str):

				self.__string = self.parse(args[0])
				if not self.__string:
					raise ValueError('[Address] invalid string: %s' % (args[0]))

				# list of registers this address depends on.
				# e.g. "ecx-0x4" -> [Register(ecx)]
				# e.g. "ebx+4*esi" -> [Register(ebx), Register(esi)]
				# e.g. "0x804a01c" -> []
				self._base_regs = self.get_base_registers()
				self._value = self.get_runtime_value()

			# elif isinstance(args[0], int):
			# 	self.__string = hex(args[0])
			# 	super(Address, self).__init__(	\
			# 							base = None, \
			# 							value = args[0])

			# elif isinstance(args[0], TaintObject):
			# 	self.__string = str(args[0])
			# 	super(Address, self).__init__(\
			# 							base = args[0], \
			# 							value = args[0].get_value())

		else:
			raise ValueError('[Address] invalid args ' + str(args))


	# immediate -> 1
	# else -> 0
	def get_type(self):
		try:
			self._value = int(self.__string, 16)
			return True
		except:
			return False

	def get_base_registers(self):
		base_registers = []
		if not self.get_type():
			# not immediate type
			tmp_string = self.__string
			# "+" "-" "*" -> "." 
			tmp_string = tmp_string.replace('+', '.').replace('-','.').replace('*','.')
	
			for i in tmp_string.split('.'):
				##v1.42 data should be striped to avoid space
				i = i.strip()
				##
				if is_register(i):
					base_registers += [Register(i)]
		return base_registers

	def get_runtime_value(self):
		if self.get_type():
			return int(self.__string, 16)
		tmp_string = self.__string
		for reg in self._base_regs:
			tmp_string = tmp_string.replace(reg.get_name(), "$"+reg.get_name())
		res = super(Address, self).execute('print /x' + tmp_string)
		return int(res.split('0x')[1].split(' ')[0], 16)

	def get_value(self):
		return self._value

	def __str__(self):
		tmp = '\033[0;33;40m'
		if self.get_type():
			# immediate type
			tmp += '(*) 0x%x' % (self._value)
		else:
			# have registers
			tmp += '(*) %s A[0x%x]' % (self.__string, self._value)
			# if self._base_regs:
			# 	tmp += super(Address, self).__str__()
		tmp += '\033[0m'
		return tmp

	## 1.44, support print in list
	def __repr__(self):
		return self.__str__()


def test():
	debug = Debugger('../test-case/case01')
	eax = Register('eax')
	ebx = Register('ebx')
	a = Address('[123 + eax*3 + ebx]')
	print a

if __name__ == '__main__':
	test()
