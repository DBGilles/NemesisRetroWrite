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
.LC4018:
	.byte 0x0
.LC4019:
	.byte 0x0
.LC401a:
	.byte 0x0
.LC401b:
	.byte 0x0
.LC401c:
	.byte 0x0
.LC401d:
	.byte 0x0
.LC401e:
	.byte 0x0
.LC401f:
	.byte 0x0
.LC4020:
	.quad .LC4020
.section .bss
.align 1
.type	completed.8060_4028,@object
.globl completed.8060_4028
completed.8060_4028: # 4028 -- 4029
.LC4028:
	.byte 0x0
.LC4029:
	.byte 0x0
.LC402a:
	.byte 0x0
.LC402b:
	.byte 0x0
.LC402c:
	.byte 0x0
.LC402d:
	.byte 0x0
.LC402e:
	.byte 0x0
.LC402f:
	.byte 0x0
.section .text
.align 16
	.text
.globl main
.type main, @function
main:
.L1130:
.LC1130:
	pushq %rbp
.LC1131:
	movq %rsp, %rbp
.LC1134:
	movl $0, -4(%rbp)
.LC113b:
	movl $0xa, -8(%rbp)
.LC1142:
	movl $0xb, -0xc(%rbp)
.LC1149:
	cmpl $0x64, -8(%rbp)
.LC114d:
	jge .L115a
.LC1153:
	movl $0xa, -0xc(%rbp)
.L115a:
.LC115a:
	movl -0xc(%rbp), %eax
.LC115d:
	popq %rbp
.LC115e:
	retq 
.size main,.-main
