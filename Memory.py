# ver 1.44
from Address import Address
from Debugger import Debugger
## 1.44
from util import *
from pwn import u32, u64

class Memory(Debugger):

	mapping_length = {
	'QWORD': 8,
	'DWORD': 4,
	'WORD': 2,
	'BYTE': 1
	}

	# e.g. DWORD PTR [ecx-0x4]		-> ([ecx-0x4], 4)
	# e.g. DWORD PTR ds:0x804a01c	-> (ds:0x804a01c, 4)
	# e.g. DWORD PTR [ebx+4*esi]	-> ([ebx+4*esi], 4)
	@staticmethod
	def parse(s):
		length_type, the_rest = s.split(' PTR ')
		length = Memory.mapping_length[length_type]
		address = the_rest
		return address, length

	# 1. Memory(string)
	# e.g. DWORD PTR [ecx-0x4]
	# e.g. DWORD PTR ds:0x804a01c
	# 2. Memory(Address, int)
	# 3. Memory(int, int)
	# 4. Memory(0) -> USER_INPUT
	# 4. Memory(1) -> STD_OUTPUT

	## 1.44
	# - add case 4th, 5th above.
	# - self._size -> self.length
	def __init__(self, *args, **kwargs):
		args_len = len(args)
		self._is_special_mem = 0

		if args[0] == 0:
			## 1.44, USER_INPUT
			self._address = None
			self._address_value = 0
			self._length = UNLIMITED_LENGTH 
			self._value = '0'
			self._is_special_mem = 1

		elif args[0] == 1:
			## 1.5
			## STD_OUTPUT
			self._address = None
			self._address_value = 0
			self._length = UNLIMITED_LENGTH
			self._value = '1'
			self._is_special_mem = 2

		elif args_len:
			length = UNKNOWN_LENGTH
			if isinstance(args[0], str):
				address_string, length = self.parse(args[0])
				address = Address(address_string)
			elif isinstance(args[0], Address) or isinstance(args[0], Memory):
				address = args[0]
			elif isinstance(args[0], int):
				address = Address(args[0])

			if args_len == 2:
				length = args[1]
	
			self._address = address
			## 1.5
			self._address_value = self._address.get_value()
			# print "==>", address
			self._length = length
			self._value = self.get_runtime_value()

		else:
			raise ValueError('[Memory] invalid args ' + str(args))

	def is_special_mem(self):
		return self._is_special_mem

	## 1.44, '== 4' -> '<= 4', jlust
	def get_value(self):
		if len(self._value) <= 4 and not self.is_special_mem():
			return u32(self._value.ljust(4,'\x00'))
		else:
			return self._value

	## 1.44, dont get value for unknown/unlimited length
	def get_runtime_value(self):
		if self._length == DEFAULT_STRLEN:
			## 1.5
			tmp_str, self._length = super(Memory, self).get_string(self._address_value)
			return tmp_str
		elif self._length not in [UNLIMITED_LENGTH, UNKNOWN_LENGTH]:
			## 1.5
			return super(Memory, self).get_memory_value(self._address_value, self._length)
		return ''

	def get_length(self):
		return self._length

	## 1.44, more beautiful =))
	def __str__(self):
		tmp_value = self.get_value()
		if self._address:
			# blue
			tmp = '\033[0;34;40m'
			if tmp_value not in ['0', '1', '']:\
				# int mem
				if isinstance(tmp_value, int):
					tmp += 'M[addr=0x%x, len=%d, 0x%x]' % (self._address_value, self._length, tmp_value)
				# string mem
				# normal mem
				else:
					if len(tmp_value) > 8:
						tmp += 'M[addr=0x%x, len=%d, %s...%s]' % \
							(self._address_value, self._length, repr(tmp_value[:4]), repr(tmp_value[-4:]))
					else:
						tmp += 'M[addr=0x%x, len=%d, %s]' % \
							(self._address_value, self._length, repr(tmp_value))

			else:
				#special mem
				if self._length == UNLIMITED_LENGTH:
					tmp += 'M[addr=0x%x, UNLIMITED_LENGTH]' % (self._address_value)
				elif self._length == UNKNOWN_LENGTH:
					tmp += 'M[addr=0x%x, UNKNOWN_LENGTH]' % (self._address_value)
		else:
			# red
			tmp = '\033[0;31;40m'
			if tmp_value == '0':
				tmp += 'USER_INPUT'
			elif tmp_value == '1':
				tmp += 'STD_OUTPUT'				

		tmp += '\033[0m'
		return tmp

	## 1.44, support print in list
	def __repr__(self):
		return self.__str__()

	## 1.5
	def __cmp__(self, other):
		return cmp(self._address_value, other)

	def __rcmp__(self, other):
		return cmp(other, self._address_value)

	## 1.5
	def contains(self, other):
		if isinstance(other, Memory) and not self.is_special_mem():
			sstart = self._address_value
			send = self._address_value + self._length
			ostart = other._address_value
			oend = other._address_value + other._length

			# print '[Memory]'
			# print sstart, send
			# print ostart, oend

			if sstart <= ostart and ostart < send:
				if oend <= send:
					return (FULL_CONTAIN, ostart, oend)
				else:
					return (TAILPART_CONTAIN, ostart, send)
			elif ostart < sstart:
				if sstart < oend and oend < send:
					return (HEADPART_CONTAIN, sstart, oend)
		return (NOT_CONTAIN, 0, 0)

	def remove(self, other):
		if isinstance(other, Memory):
			flag, start, end = self.contains(other)
			if flag != NOT_CONTAIN:
				pass
				return True

		return False


	def is_empty(self):
		if self._address != None and self._length == 0:
			return True
		return False

	def __eq__(self, other):
		if isinstance(other, Memory):
			if self.is_special_mem() == other.is_special_mem():
				if self.is_special_mem() == 0:
					return (self._address_value == other._address_value and \
						self._length == other._length)
				else:
					return True
		else:
			return self.get_value() == other

## 1.44 global value
USER_INPUT = Memory(0)
STD_OUTPUT = Memory(1)
