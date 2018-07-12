from Register import Register
from Memory import Memory, USER_INPUT, STD_OUTPUT
from Address import Address
from util import *
import bisect

class TList:
	logger = logging.getLogger('TList')

	def __init__(self):
		self.reg_list = []
		self.addr_list = []
		# mem_list is a sorted list
		self.mem_list = []
		self.special_list = [USER_INPUT]

	def check_reg_in_list(self, reg):
		# just check name
		# need optimize to have more accurately checking
		for ireg in self.reg_list:
			if reg.get_name() == ireg.get_name():
				return reg
		return None

	def check_special_in_list(self, spec):
		for ispec in self.special_list:
			if ispec == spec:
				return ispec
		return None

	def check_mem_in_list(self, mem, return_flag = RETURN_THIS):
		# need implement part contain
		for imem in self.mem_list:
			flag_contain, start, end = imem.contains(mem)
			if flag_contain != NOT_CONTAIN:
				if return_flag == RETURN_ROOT:
					return imem
				else:
					return mem
		return None

	def check(self, obj, return_flag = RETURN_THIS):
		if isinstance(obj, Register):
			return self.check_reg_in_list(obj)

		elif isinstance(obj, Address):
			for ireg in obj._base_regs:
				return self.check(ireg, return_flag)

		elif isinstance(obj, Memory):
			if obj.is_special_mem():
				return self.check_special_in_list(obj)

			else:
				tmp_addr = self.check(obj._address, return_flag)
				if tmp_addr != None:
					# this is not simple that controling the address means
					# controling the memory. Must have some conditions to return True.
					# The conditions are:
					# 	- We must have write permission to some address that we know.
					#	- The address that we have write permission must in 
					# the address's range we control of the memory.
					# 
					# This implement is not enough
					return tmp_addr
				else:
					return self.check_mem_in_list(obj, return_flag)
		else:
			try:
				tmp_obj = list(obj)
				tmp_ret = []
				for i in tmp_obj:
					tmp_chk = self.check(i)
					if tmp_chk != None:
						tmp_ret += [tmp_chk]

				if len(tmp_ret) >= 1:
					if len(tmp_ret) == 1:
						return tmp_ret[0]
					else:
						return tmp_ret

			except:
				pass

		return None

	def add(self, obj):
		if not obj:
			return None

		if isinstance(obj, list):
			for i in obj:
				# if self.check(i) == None:
				# 	if isinstance(i, Register):
				# 		self.reg_list.append(i)
				# 	elif isinstance(i, Memory) and not i.is_special_mem():
				# 		self.mem_list.append(i)
				self.add(i)

		else:
			tmp_check = self.check(obj)
			if tmp_check == None:
				self.logger.info('Adding: %s' % str(obj))
				if isinstance(obj, Register):
					self.reg_list.append(obj)
				elif isinstance(obj, Memory) and not obj.is_special_mem():
					self.mem_list.append(obj)
				self.logger.info(self)
			elif tmp_check:
				self.logger.info('%s is already in TList' % str(obj))

		return obj

	def remove_reg(self, obj):
		for ireg in self.reg_list:
			if ireg.get_name() == obj.get_name():
				self.reg_list.remove(ireg)
				return True
		return False

	def remove_mem(self, obj):
		for imem in self.mem_list:
			if imem.remove(obj):
				if imem.is_empty():
					self.mem_list.remove(imem)
				return True
		return False

	def remove(self, obj):
		tmp_obj = self.check(obj)
		if tmp_obj == None:
			return None

		if isinstance(obj, list):
			for i in obj:
				self.remove(i)
		else:
			self.logger.info('Removing: %s' % str(obj))
			if isinstance(obj, Register):
				self.remove_reg(obj)
			elif isinstance(obj, Memory):
				self.remove_mem(obj)
			self.logger.info(self)

		return obj

	def __str__(self):
		# res = '\033[0;31;40m' + '-'*32 + 'TList>' + '-'*32 + '\033[0m'
		res = '\033[0;31;40mCurrent TList\033[0m'
		if self.reg_list:
			res += '\n\treg_list: '
			for ireg in self.reg_list:
				res += '\n\t\t\t' + str(ireg)
		if self.mem_list:
			res += '\n\tmem_list: '
			for imem in self.mem_list:
				res += '\n\t\t\t' + str(imem)

		# res += '\n\033[0;31;40m' + '-'*32 + '------' + '-'*32 + '\033[0m'
		return res

# def test():
	

# if __name__ == '__main__':
# 	test()