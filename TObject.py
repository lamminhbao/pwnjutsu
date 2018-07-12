class TObject:
	def __init__(self, dst, src, inst):
		self.dst = dst
		self.src = src
		self.inst = inst

	def __repr__(self):
		res = str(self.dst)
		res += " is tainted by " + str(self.src)
		res += " at\n\t\t" + str(self.inst.original_str)
		return res
