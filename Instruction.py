# ver 1.44
import re
from Register import Register
from Memory import Memory
from Address import Address
from KnowFunction import KnowFunction
from util import *

class Instruction:
	# parse a string from debugger
	# e.g.
	# 0x804843b <main>:    lea    ecx,[esp+0x4]
	# 0x08048442 <+7>:     push   DWORD PTR [ecx-0x4]
	# 0x08048453 <+24>:    call   0x8048310 <gets@plt>
	# 0x08048477 <+60>:    ret
	@classmethod
	def parse(cls, s):
		tmp_i = s.find(':')
		address = s[:tmp_i].split()[0]
		the_rest = s[tmp_i+1:].strip()
		if ' ' not in the_rest:
			op = the_rest
			the_rest = ''
		else:
			matchObj = re.match(r'(.*)\s\s(.*)', the_rest, re.M|re.I)
			op, the_rest = matchObj.groups()
		if the_rest:
			if ',' in the_rest:
				# have 2 operands
				op1, op2 = the_rest.split(',')
				function = ''
			elif '<' in the_rest:
				# have function
				matchObj = re.match(r'(.*)<(.*)>', the_rest, re.M|re.I)
				op1 = matchObj.group(1).strip()
				op2 = ''
				function = matchObj.group(2)
			else:
				# have 1 operand
				op1 = the_rest
				op2 = ''
				function = ''
		else:
			# have no operands
			op1 = op2 = function = ''

		return address, op.strip(), op1, op2, function

	# recieve a string of operand
	# convert to corresponding object
	# e.g. "eax" -> Register
	# e.g. DWORD PTR [ecx-0x4] -> Memory
	# e.g. 0x8048310 -> int
	@staticmethod
	##v1.42 update Register --> global var.
	def convert_operand_to_object(op):
		if op:
			if is_register(op):
				if op not in globals():
					globals()[op] = Register(op)
				return globals()[op]
			if is_memory(op):
				return Memory(op)
			if is_address(op):
				return Address(op)
			if 'gs:' in op:
				return None
			return int(op, 16)
		else:
			return None
	##

	# recieve string from debugger
	def __init__(self, s):
		self.original_str = s
		try:
			address, op, op1, op2, function = Instruction.parse(s)
		except:
			raise Exception('Instruction parse fail.')
		self.address = int(address, 16)
		self.op = op
		self.op1 = self.convert_operand_to_object(op1)
		self.op2 = self.convert_operand_to_object(op2)
		if function:
			self.function = KnowFunction(function)
		else:
			self.function = None
		##v1.42 update dict
		self.__dict = self.get_dict_dst_src()
		##
	##v1.42 gen dict + get src + get dst	
	#not implement
	def get_dict_dst_src(self):
		##v1.42
		#res[dst] = src
		res = {}
		
		#dst = op1
		#src = op2
		list1 = ['mov', 'lea']
		
		#dst = op1
		#src = op1, op2
		list2 = ['add', 'adc', 'sub', 'sbb', 'mul', 'imul', 'div', 'idiv'
				,'and', 'xor', 'or', 'xor'
				,'rol', 'ror', 'sal', 'sar', 'shl', 'shld', 'shr', 'shrd', 'rcl', 'rcr']

		#1 operand inst.
		#dst = op1
		#src = op1, 1.
		list3 = ['dec', 'inc']
	
		#1 operand inst.
		#dst = src = op1
		list4 = ['neg', 'not']
	
		#do nothing
		list5 = ['cmp', 'test', 'nop']
	
		#special inst.
		#not implement
		list6 = ['call', 'int']

		if self.op in list1 + list2:
			# list1 and list2 are lists of two-operand instruction
			# if any operands are None, that inst has something wrong.
			if self.op1 == None or self.op2 == None:
				return res

		if self.op in list6 + list5:
			#print "Not implement yet"
			return res



		#some complicate functions
		if   self.op == 'push':
			#mov dword ptr [esp-4], eax
    		#sub esp, 4
			res[Memory("DWORD PTR [esp-4]")] = self.op1
			res[esp] = set([esp, 4])
		elif self.op == 'pop':
			#mov X, DWORD PTR [esp]
			#add esp, 4
			res[self.op1] = Memory("DWORD PTR [esp]")
			res[esp] = set([esp, 4])
		elif self.op == 'leave':
			#lea esp, [ebp-4]
			#mov ebp, dword ptr [ebp]
			res[esp] = Address('ebp - 4')
			res[ebp] = Memory('DWORD PTR [ebp]')
		elif self.op == 'ret':
			#pop eip
			res[eip] = Memory("DWORD PTR [esp]")
			res[esp] = set([esp, 4])
		elif self.op == 'xchg':
			res[self.op1] = self.op2
			res[self.op2] = self.op1
		#some category of functions
		elif self.op in list1:
			res[self.op1] = self.op2
		elif self.op in list2:
			res[self.op1] = set([self.op1, self.op2])
		elif self.op in list3:
			res[self.op1] = set([self.op1, 1])
		elif self.op in list3:
			res[self.op1] = self.op1
		else:
			# raw_input("Inst. not implement yet.... need to improve >")
			pass
		return res
		##

	#eax
	#set(eax, ebx)
	def get_src(self, dst = 'all'):
		if dst =='all':
			return self.__dict.values()
		if dst not in self.__dict:
			return None
		return res[dst]

	#eax
	#set(eax, ebx)
	def get_dst(self, src = 'all'):
		if src == 'all':
			return self.__dict.keys()
		tmp = []
		for i in self.__dict:
			if self.__dict[i] == src:
				tmp.append(i)
		
		## 1.5
		return tmp

	## 1.44
	def is_need_input(self):
		if self.function:
			return self.function.is_need_input()
		return False

	def __str__(self):
		result = '0x%x:\t%s\t' % (self.address, self.op)
		if self.op2 != None:
			try:
				return result + str(self.op1) + ', ' + hex(self.op2)
			except:
				return result + str(self.op1) + ', ' + str(self.op2)
		elif self.op1 != None:
			if self.function:
				try:
					return result + hex(self.op1) + '\t\t<%s>' % (self.function)
				except:
					return result + str(self.op1) + '\t\t<%s>' % (self.function)
			else:
				try:
					return result + hex(self.op1)
				except:
					return result + str(self.op1)
		else:
			return result

	## 1.5
	def get_type(self):
		call = ['call']
		condition = ['test', 'cmp']

		if self.op in call:
			return CALL_INST
		elif self.op in condition:
			return CONDITION_INST
		return REGULAR_INST

##1.44
# for ret inst run properly
esp = Register('esp')
ebp = Register('ebp')
eip = Register('eip')

def test():
	from Debugger import Debugger
	import time

	debugger = Debugger('test-case/case01')
	t = time.time()

	for j in range(23):
		current_instruction = debugger.get_current_instruction()
		print current_instruction
		i = Instruction(current_instruction)
		#print '='*80
		tmp = i.get_dict_dst_src()
		for k in tmp:
			print '\t',k, "<-----", tmp[k] 

		## 1.44
		f = i.function
		if f:
			tmp = f.get_dict_dst_src()
			for k in tmp:
				print '\t',k, "<-----", tmp[k] 

		## 1.44
		if i.is_need_input():
			debugger.step("aaaa")
		else:
			debugger.step()
	print time.time() - t


if __name__ == '__main__':
	test()

