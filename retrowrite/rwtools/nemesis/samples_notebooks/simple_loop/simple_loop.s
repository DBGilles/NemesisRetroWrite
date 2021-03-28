.section .rodata
.align 4
.type	_IO_stdin_used_2000,@object
.globl _IO_stdin_used_2000
_IO_stdin_used_2000: # 2000 -- 2004
.LC2000:
	.byte 0x1
.LC2001:
	.byte 0x0
.LC2002:
	.byte 0x2
.LC2003:
	.byte 0x0

.section .data
.align 8
.LC4000:
	.byte 0x0
.LC4001:
	.byte 0x0
.LC4002:
	.byte 0x0
.LC4003:
	.byte 0x0
.LC4004:
	.byte 0x0
.LC4005:
	.byte 0x0
.LC4006:
	.byte 0x0
.LC4007:
	.byte 0x0
.LC4008:
	.quad .LC4008
.section .bss
.align 1
.type	completed.8060_4010,@object
.globl completed.8060_4010
completed.8060_4010: # 4010 -- 4011
.LC4010:
	.byte 0x0
.LC4011:
	.byte 0x0
.LC4012:
	.byte 0x0
.LC4013:
	.byte 0x0
.LC4014:
	.byte 0x0
.LC4015:
	.byte 0x0
.LC4016:
	.byte 0x0
.LC4017:
	.byte 0x0
.section .text
.align 16
	.text
.globl main
.type main, @function
main:
.L1129:
.LC1129:
	endbr64 
.LC112d:
	pushq %rbp
.LC112e:
	movq %rsp, %rbp
.LC1131:
	movl $1, -8(%rbp)
.LC1138:
	movl $0, -4(%rbp)
.LC113f:
	jmp .L1149
.L1141:
.LC1141:
	addl $1, -8(%rbp)
.LC1145:
	addl $1, -4(%rbp)
.L1149:
.LC1149:
	cmpl $9, -4(%rbp)
.LC114d:
	jle .L1141
.LC114f:
	movl -8(%rbp), %eax
.LC1152:
	popq %rbp
.LC1153:
	retq 
.size main,.-main
