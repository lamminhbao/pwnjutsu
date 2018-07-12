# v1.44
from Debugger import *
from Register import *
from Memory import *
from Address import *
from util import *

## 1.44 Function -> KnowFuntion =))
class KnowFunction:

	# for defining know_function dictionary.
	class arg:
		def __init__(self, type, name):
			self.type = type
			self.name = name

	class f_syntax:
		def __init__(self, return_type, *args):
			self.return_type = return_type
			self.args = list(args)

	# element structure
	# 	functione_name: [return_type, arg0, arg1, ...]
	know_function = {
		# char *gets(char *s)
		'gets': f_syntax('char *', arg('char *', 's'))
		# ,'ssize_t read(int fildes, void *buf, size_t nbytes)'
		,'printf': f_syntax('int', arg('const char *', 'format'))
		,'read': f_syntax('ssize_t', arg('int', 'fd'), arg('void *', 'buf'), arg('ssize_t', 'count'))
		,'malloc': f_syntax('void *', arg('int', 'size'))
		,'strcpy': f_syntax('void *', arg('char *', 'dst'), arg('char *', 'src'))
		,'fopen': f_syntax('FILE *', arg('char *', 'path'), arg('char *', 'mode'))
		,'fclose': f_syntax('int', arg('FILE *', 'stream'))
		,'atoi': f_syntax('int', arg('char *', 'nptr'))
		,'puts': f_syntax('int', arg('const char *', 's'))
		, 'setvbuf': f_syntax('void', arg('FILE *', 'steam'))
		, 'fread': f_syntax('void', arg('void *', 'ptr'), arg('size_t', 'size'), arg('size_t', 'nmemb'), arg('FILE *', 'stream'))
	}

	@staticmethod
	# e.g. "gets@plt" -> "gets"
	def parse(s):
		return s.split('@')[0]

	@staticmethod
	def convert_arg_to_object(index):
		stack_address = Address('[esp+%d]' % (index*4))
		memory = Memory(stack_address, 4)
		return memory			

	def __init__(self, name):
		self.__name = self.parse(name)
		# list of arguments
		self.__args = []
		if self.__name in self.know_function.keys():
			self.__return_type = self.know_function[self.__name].return_type
			index = 0
			for i in self.know_function[self.__name].args:
				self.__args += [self.convert_arg_to_object(index)]
				index += 1

		self.__dict = self.get_dict_dst_src()

	def __nonzero__(self):
		return bool(self.__name)

	def __str__(self):
		s = '%s %s(' % (self.__return_type, self.__name)
		for i in self.__args[:-1]:
			s += hex(i.get_value()) + ', '
		return s + hex(self.__args[-1].get_value()) + ')'

	## 1.44
	def get_dict_dst_src(self):
		res = {}
		if self.__name == 'gets':
			res[Memory(self.__args[0], UNLIMITED_LENGTH)] = USER_INPUT

		## implement for fun =))
		# elif self.__name == 'printf':
		# 	res[STD_OUTPUT] = Memory(self.__args[0], DEFAULT_STRLEN)

		elif self.__name == 'read':
			if self.__args[0].get_value() == 0:
				#fd = 0 -> stdin
				res[Memory(self.__args[1], self.__args[2].get_value())] = USER_INPUT

		elif self.__name == 'atoi':
			if 'eax' not in globals():
				globals()['eax'] = Register('eax')

			res[eax] = Memory(self.__args[0], DEFAULT_STRLEN)

		return res

	def get_src(self, dst = 'all'):
		if dst =='all':
			return self.__dict.values()
		if dst not in self.__dict:
			return None
		return res[dst]

	def get_dst(self, src = 'all'):
		if src =='all':
			return self.__dict.keys()
		tmp = []
		for i in self.__dict:
			if self.__dict[i] == src:
				tmp.append(i)

		## 1.5
		return tmp

	def is_known(self):
		return bool(self.__name in self.know_function)

	## 1.44
	def is_need_input(self):
		if USER_INPUT in self.__dict.values():
			return True
		return False

	## 1.6
	def get_name(self):
		return self.__name

	def get_args(self, index = -1):
		if index >=0 and index < len(self.__args):
			return self.__args[index]
		else:
			return self.__args
