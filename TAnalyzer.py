#v1.5
from util import *
from Instruction import *
from Debugger import *
from Memory import *
from Register import *
from Address import *
from TList import *		
from TObject import *
import parser	

class TAnalyzer:
	logger = logging.getLogger('TAnalyzer')

	def __init__(self, target_file_name):
		self.debugger = Debugger(target_file_name)
		self.tlist = TList()
		self.step_flag = STEP_INTO	
		self.default_payload = 'AAAAAAAAAAAAAAAA'
		self.deep_level = 1
		self.tobj_list = []
		self.detected = 0

	def print_dst_src_dict(self, obj):
		tmp_dict = obj.get_dict_dst_src()
		for k in tmp_dict:
			self.logger.debug('%s %s %s %s', '\t', k, "<-----", tmp_dict[k])

	@staticmethod
	def add_list_loop(listoflist):
		tmp = []
		for i in listoflist:
			tmp += i
		return tmp

	def check_n_add_or_remove(self, inst):
		tmp_dict = {}
		for src in inst.get_src():
			taint_src = self.tlist.check(src)
			if taint_src != None:
				self.logger.info('Taint source: %s' % str(taint_src))
				tmp_dict[taint_src] = inst.get_dst(src)
			else:
				self.logger.debug('%s isn\'t in TList' % str(src))

		tmp_taint_dst = self.add_list_loop(tmp_dict.values())
		self.tlist.add(tmp_taint_dst)

		tmp_clean_dst = [obj for obj in inst.get_dst() if obj not in tmp_taint_dst]
		self.tlist.remove(tmp_clean_dst)

		return tmp_dict

	def handle_inst(self, inst):
		# set step_flag -> step into
		self.step_flag = STEP_INTO
		# print
		self.print_dst_src_dict(inst)

		return self.check_n_add_or_remove(inst)

	def handle_call_inst(self, inst):
		f = inst.function
		if f and f.is_known():
			# set step_flag -> step over if know this function
			self.step_flag = STEP_OVER
			# print
			self.print_dst_src_dict(f)

			return self.check_n_add_or_remove(f)

		else:
			# handle call inst
			return self.handle_inst(inst)


	def stop_condition(self, res_from_dbg, inst):
		if 'The program is not being run.' in res_from_dbg:
			return 0

		elif isinstance(inst, Instruction):
			if inst.op == 'ret':
				self.deep_level -= 1

			elif inst.op == 'call' and self.step_flag == STEP_INTO:
				self.deep_level += 1

		return self.deep_level

	def check_tobj(self, tobj, obj):
		if isinstance(tobj.dst, Register) and isinstance(obj, Register):
			if tobj.dst.get_name() == obj.get_name():
				return True
		if isinstance(tobj.dst, Memory) and isinstance(obj, Memory):
			if obj.contains(tobj.dst)[0] != NOT_CONTAIN:
				return True

	def find_tobj_src(self, tobj, tobj_list):
		for iobj in tobj_list:
			if isinstance(tobj.src, Register) and isinstance(iobj.dst, Register):
				if tobj.src.get_name() == iobj.dst.get_name():
					return iobj
			if isinstance(tobj.src, Memory) and isinstance(iobj.dst, Memory):
				if iobj.dst.contains(tobj.src)[0] == FULL_CONTAIN:
					return iobj
		return None

	def taint_chain(self, tobj):
		chain = [tobj]
		next_tobj = tobj
		tmp_list = self.tobj_list[:]
		while next_tobj:
			next_tobj = self.find_tobj_src(next_tobj, tmp_list)
			if next_tobj:
				tmp_list.remove(next_tobj)
				chain.append(next_tobj)

		return chain

	def check_sink(self, taint_dict, inst):
		if taint_dict:
			for isrc in taint_dict:
				for idst in taint_dict[isrc]:
					tmp_tobj = TObject(idst, isrc, inst)
					self.tobj_list.append(tmp_tobj)

					if self.check_tobj(tmp_tobj, eip):
						if self.debugger.elf.canary:
							alert = 'EIP is tainted!\n'
							alert += 'Detect the binary using stack canaries.\n'
							alert += 'Execution flow may not be hijacked.'
						else:
							alert = 'EIP is tainted!\n'
							alert += 'The binary don\'t use stack canaries.\n'
							alert += 'Execution flow can be hijacked.'

						return alert, self.taint_chain(tmp_tobj)

		if inst.get_type() == CALL_INST:
			if inst.function.get_name() == 'printf':
				format_str = Memory(inst.function.get_args(0), DEFAULT_STRLEN)
				taint_src = self.tlist.check(format_str, RETURN_ROOT)
				if taint_src != None:
					tmp_tobj = TObject(format_str, taint_src, inst)
					alert = '1st argument (format string) of printf is tainted!\nFormat string attack can be performed.'
					return alert, self.taint_chain(tmp_tobj)

			elif inst.function.get_name() == 'fopen':
				path = Memory(inst.function.get_args(0), DEFAULT_STRLEN)
				taint_src = self.tlist.check(path, RETURN_ROOT)
				if taint_src != None:
					if path._address_value != taint_src._address_value:
						tmp_tobj = TObject(path, taint_src, inst)
						alert = '1st argument (path) of fopen is tainted!\nArbitrary file can be read.'
						return alert, self.taint_chain(tmp_tobj)
					else:
						pass

		return '', []

	def check_input_file(self):
		alert = ''
		flag = DEFAULT_FILE
		if self.debugger.elf.canary:
			alert += 'Detect the binary using stack canaries.\n'
			alert += 'This tool may not run correctly.\n'
			flag = CANARY_DETECT
		if self.debugger.elf.bits != 32:
			alert += 'Detect %d-bit binary.\n' % (self.debugger.elf.bit)
			alert += 'This tool does not support %d-bit binary.' % (self.debugger.elf.bit)
			flag = NOT_32BIT_ELF
		return flag, alert


	def start(self):
		res_from_dbg = ''
		inst = None
		count = 0

		flag, alert = self.check_input_file()
		if flag == NOT_32BIT_ELF:
			exit(alert)
		elif flag == CANARY_DETECT:
			if parser.cmd_args.force:
				print alert
			else:
				exit(alert)

		try:
			while(self.stop_condition(res_from_dbg, inst)):
				inst = self.debugger.get_current_instruction()
				self.logger.info(inst)
				inst = Instruction(inst)

				inst_type = inst.get_type()

				# new_taint_obj = []
				# taint_src = []
				taint_dict = {}
				if inst_type == CALL_INST:
					# new_taint_obj, taint_src = self.handle_call_inst(inst)
					taint_dict = self.handle_call_inst(inst)
				elif inst_type == CONDITION_INST:
					pass
				else:
					# new_taint_obj, taint_src = self.handle_inst(inst)
					taint_dict = self.handle_inst(inst)

				if self.step_flag == STEP_OVER:
					self.logger.info('Step over')

				## 1.6
				self.logger.debug('Taint_dict: %s', taint_dict)
				check_sink, chain = self.check_sink(taint_dict, inst)
				if check_sink:
					self.detected = 1
					print check_sink
					for i in chain:
						print '\t->', i

				if inst.is_need_input():
					if not parser.cmd_args.input:
						res_from_dbg = self.debugger.step(self.default_payload, self.step_flag)
					else:
						manual_input = raw_input('program need input> ').strip()
						res_from_dbg = self.debugger.step(manual_input, self.step_flag)
				else:
					res_from_dbg = self.debugger.step(None, self.step_flag)

				if parser.cmd_args.output:
					print '[Output when step]', res_from_dbg

				count += 1

			if not self.detected:
				print 'No vulnerability was detected.'

		except Exception as e:
			print e

		return count

def main(path):
	tainter = TAnalyzer(path)

	t = time.time()
	count = tainter.start()
	print 'Number of instruction:', count
	print 'Time consumming:', time.time() - t

if __name__ == '__main__':
	parser.argparser(main)

