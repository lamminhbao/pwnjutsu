import logging
import time
from pwn import *
import re

# pwntools log level
context.log_level = 'critical'

# ver 1.44
#Miscellaneous utility functions, variables

white_list = [[8, 'rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'rbp', 'rsp', 'rip', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15'],
				  [4, 'eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'ebp', 'esp', 'eip'],
				  [2, 'ax', 'bx', 'cx', 'dx'],
				  [1, 'al', 'bl', 'cl', 'dl',
			 		  'ah', 'bh', 'ch', 'dh']]

segment_reg = ['fs', 'gs', 'cs', 'ss', 'ds', 'es']

## 1.44, special length for Memory class
UNLIMITED_LENGTH = 0x10000
UNKNOWN_LENGTH = 0
DEFAULT_STRLEN = -1

## 1.5, Memory constant
NOT_CONTAIN = 0xf0
FULL_CONTAIN = 0xf1
TAILPART_CONTAIN = 0xf2
HEADPART_CONTAIN = 0xf3

# Instruction constant
CALL_INST = 0xe0
CONDITION_INST = 0xe1
REGULAR_INST = 0xe2

# Debugger constant
STEP_INTO = 0
STEP_OVER = 1

# TList constant
RETURN_THIS = 0xd0
RETURN_ROOT = 0xd1

# TAnalyzer constant
DEFAULT_FILE = 0xc0
CANARY_DETECT = 0xc1
NOT_32BIT_ELF = 0xc2

def is_memory(s):
	if 'gs:' not in s:
		return 'PTR' in s
	return False

def is_address(s):
	return (s[0] == '[' and s[-1] == ']') or is_segment_reg(s.split(':')[0])

def is_segment_reg(s):
	return s in segment_reg

def is_register(s):
	return sum((s in reg)*reg[0] for reg in white_list)

