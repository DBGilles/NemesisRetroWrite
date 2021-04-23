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
.LC2004:
	.byte 0xa
.LC2005:
	.byte 0x0
.LC2006:
	.byte 0x0
.LC2007:
	.byte 0x0
.LC2008:
	.byte 0x14
.LC2009:
	.byte 0x0
.LC200a:
	.byte 0x0
.LC200b:
	.byte 0x0
.LC200c:
	.byte 0x1e
.LC200d:
	.byte 0x0
.LC200e:
	.byte 0x0
.LC200f:
	.byte 0x0

.section .data
.align 8
.LC4020:
	.byte 0x0
.LC4021:
	.byte 0x0
.LC4022:
	.byte 0x0
.LC4023:
	.byte 0x0
.LC4024:
	.byte 0x0
.LC4025:
	.byte 0x0
.LC4026:
	.byte 0x0
.LC4027:
	.byte 0x0
.LC4028:
	.quad .LC4028
.section .bss
.align 1
.type	completed.8060_4030,@object
.globl completed.8060_4030
completed.8060_4030: # 4030 -- 4031
.LC4030:
	.byte 0x0
.LC4031:
	.byte 0x0
.LC4032:
	.byte 0x0
.LC4033:
	.byte 0x0
.LC4034:
	.byte 0x0
.LC4035:
	.byte 0x0
.LC4036:
	.byte 0x0
.LC4037:
	.byte 0x0
.section .text
.align 16
	.text
.globl main
.type main, @function
main:
.L1140:
.LC1140:
	pushq %rbp
.LC1141:
	movq %rsp, %rbp
.LC1144:
	subq $0x30, %rsp
.LC1148:
	xorl %esi, %esi
.LC114a:
	movl $0, -4(%rbp)
.LC1151:
	movq .LC2004(%rip), %rax
.LC1158:
	movq %rax, -0x10(%rbp)
.LC115c:
	movl .LC200c(%rip), %ecx
.LC1162:
	movl %ecx, -8(%rbp)
.LC1165:
	leaq -0x1c(%rbp), %rax
.LC1169:
	movq %rax, %rdi
.LC116c:
	movl $0xc, %edx
.LC1171:
	callq memset@PLT
.LC1176:
	movl $4, -0x20(%rbp)
.LC117d:
	movl $0, -0x24(%rbp)
.L1184:
.LC1184:
	cmpl $3, -0x24(%rbp)
.LC1188:
	jge .L11cf
.LC118e:
	movl -0x20(%rbp), %eax
.LC1191:
	movslq -0x24(%rbp), %rcx
.LC1195:
	cmpl -0x10(%rbp, %rcx, 4), %eax
.LC1199:
	jge .L11b0
.LC119f:
	movslq -0x24(%rbp), %rax
.LC11a3:
	movl $0x1a4, -0x1c(%rbp, %rax, 4)
.LC11ab:
	jmp .L11bc
.L11b0:
.LC11b0:
	movslq -0x24(%rbp), %rax
.LC11b4:
	movl $0x45, -0x1c(%rbp, %rax, 4)
.L11bc:
.LC11bc:
	jmp .L11c1
.L11c1:
.LC11c1:
	movl -0x24(%rbp), %eax
.LC11c4:
	addl $1, %eax
.LC11c7:
	movl %eax, -0x24(%rbp)
.LC11ca:
	jmp .L1184
.L11cf:
.LC11cf:
	cmpl $0x1a4, -0x1c(%rbp)
.LC11d6:
	jne .L11e8
.LC11dc:
	movl $0x64, -4(%rbp)
.LC11e3:
	jmp .L11ef
.L11e8:
.LC11e8:
	movl $0xc, -4(%rbp)
.L11ef:
.LC11ef:
	movl -4(%rbp), %eax
.LC11f2:
	addq $0x30, %rsp
.LC11f6:
	popq %rbp
.LC11f7:
	retq 
.size main,.-main
