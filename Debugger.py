## ver 1.44
from util import *

class Debugger(object):
	##v1.41 avaible for both gdb default and gdb-peda
	__prompt1 = "(gdb) "
	__prompt2 = '\x01\x1b[;31m\x02gdb-peda$ \x01\x1b[0m\x02'	

	#start gdb process
	p = process('gdb')
	__tmp = ''
	while 1:
		if __prompt1 in __tmp:
			__prompt = __prompt1
			break
		elif __prompt2 in __tmp:
			__prompt = __prompt2
			break
		else:
			__tmp += p.recv(1024)
	p.sendline()
	##

	#recieve a string
	#e.g. /home/ubuntu/Desktop/bof
	def __init__(self, target):
		#set file for debugger
		self.__file = target
		#get gdb ready
		self.p.recvuntil(self.__prompt)
		# recently add this code
		self.setup()
		self.run()

	def load_file(self):
		#try to load file into gdb
		res = self.execute("file " + self.__file)
		if "done" in res:
			return True
		return False

	def get_function_address(self, function):
		#try to get address of a function using pwntool
		try:
			return self.elf.symbols[function]
		except KeyError:
			pass

	#recieve a string or number
	#e.g. "1234", "0x1234", 1234, 0x1234
	def set_breakpoint(self, breakpoint):
		return self.execute('b* ' + str(breakpoint))

	#do something like load file, check elf, check aslr, set breakpoint
	def setup(self):
		#if cannot load file then exit
		if not self.load_file():
			print "[Debugger] Failed to set up debugger"
			exit(0)
		#get some basic infomation with elf module
		try:
			self.elf = ELF(self.__file)
		except:
			print '[Debugger] Failed to load file elf'
			exit(0)

		f = open('/proc/sys/kernel/randomize_va_space', 'r')
		if f.read().strip() != '0':
			print '[Debugger] Kernel\'s ASLR need turn off'
			f.close()
			exit(0)

		f.close()

		#let gdb use kernel's ASLR, which is disabled.
		self.execute('set disable-randomization off')

		##v1.41 use intel disassembly style
		self.execute('set disassembly-flavor intel')
		self.execute('set pagination off')
		##


		#set breakpoint at main
		self.execute('b* main')

	def run(self, input_file = None):
		if not input_file:
			return self.execute('run')
		return self.execute('run < ' + input_file)

	def get_current_instruction(self):
		# reduce "=> "
		return self.execute('x/i $eip')[3:].strip()

	def step(self, payload = None, flag = STEP_OVER):
		#flag = 1 is step over
		#flag = 0 is step in
		if flag == STEP_OVER:
			return self.execute('ni', payload)
		return self.execute('si', payload)

	def check(self, dbg_output):
		if 'Program received signal' in dbg_output:
			raise Exception(dbg_output)

	##v1.41 change Debugger.p into self.p
	def execute(self, command, payload = None):
		#send command to gdb
		self.p.sendline(command)
		#if need input (gets/read/...) then send payload
		if payload:
			self.p.sendline(payload)
		#recv result from gdb
		res = self.p.recvuntil(self.__prompt)
		res = res[:res.find(self.__prompt)]
		self.check(res)
		return res

	##

	#recieve a register name
	def get_register_value(self, name):
		##v1.41 return hex value, compatable with gdb default
		res = self.execute('p /x $%s' % name)
		##
		return int(res.split('0x')[1].split(' ')[0], 16)

	@staticmethod
	def gdbstring_to_memory(s):
		tmp = s[s.find(':\t')+2:]
		tmp = re.sub(r'\n.*:', '', tmp)
		tmp = tmp.replace('\t','')
		tmp = tmp.replace('\n','')
		tmp = tmp.replace('0x','')
		return tmp.decode('hex')

	def get_memory_value(self, address, size):
		res = self.execute('x/%dbx %d' % (size, address))
		return self.gdbstring_to_memory(res)

	## v1.44, new method
	@staticmethod
	def calculate_length(s1, s2):
		n1 = int(s1.split(':')[0], 16)
		n2 = int(s2.split(':')[0], 16)
		return n2-n1-1

	def get_string(self, address):
		res1 = self.execute('x/s %d' % (address))
		res2 = self.execute('')
		tmp_len = self.calculate_length(res1, res2)
		# print '[Debugger]', address, tmp_len
		return self.get_memory_value(address, tmp_len), tmp_len


def test():
	debug = Debugger('../test-case/case01')
	print hex(debug.get_function_address('main'))
	print debug.get_current_instruction()
	debug.step(flag = 0)
	print debug.get_current_instruction()
	debug.step()
	print debug.get_current_instruction()
	print hex(debug.get_register_value('ebx'))
	print debug.get_memory_value(debug.get_register_value('ebx'), 4)
	print "test ok!!!"

if __name__ == '__main__':
	test()
#test()
##