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
	.byte 0x49
.LC2005:
	.byte 0x6e
.LC2006:
	.byte 0x63
.LC2007:
	.byte 0x6f
.LC2008:
	.byte 0x72
.LC2009:
	.byte 0x72
.LC200a:
	.byte 0x65
.LC200b:
	.byte 0x63
.LC200c:
	.byte 0x74
.LC200d:
	.byte 0x20
.LC200e:
	.byte 0x6e
.LC200f:
	.byte 0x75
.LC2010:
	.byte 0x6d
.LC2011:
	.byte 0x62
.LC2012:
	.byte 0x65
.LC2013:
	.byte 0x72
.LC2014:
	.byte 0x20
.LC2015:
	.byte 0x6f
.LC2016:
	.byte 0x66
.LC2017:
	.byte 0x20
.LC2018:
	.byte 0x61
.LC2019:
	.byte 0x72
.LC201a:
	.byte 0x67
.LC201b:
	.byte 0x75
.LC201c:
	.byte 0x6d
.LC201d:
	.byte 0x65
.LC201e:
	.byte 0x6e
.LC201f:
	.byte 0x74
.LC2020:
	.byte 0x73
.LC2021:
	.byte 0x20
.LC2022:
	.byte 0x73
.LC2023:
	.byte 0x75
.LC2024:
	.byte 0x70
.LC2025:
	.byte 0x70
.LC2026:
	.byte 0x6c
.LC2027:
	.byte 0x69
.LC2028:
	.byte 0x65
.LC2029:
	.byte 0x64
.LC202a:
	.byte 0x3a
.LC202b:
	.byte 0x20
.LC202c:
	.byte 0x25
.LC202d:
	.byte 0x69
.LC202e:
	.byte 0x20
.LC202f:
	.byte 0xa
.LC2030:
	.byte 0x0

.section .data
.align 8
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
.LC4030:
	.quad .LC4030
.section .bss
.align 1
.type	completed.8060_4038,@object
.globl completed.8060_4038
completed.8060_4038: # 4038 -- 4039
.LC4038:
	.byte 0x0
.LC4039:
	.byte 0x0
.LC403a:
	.byte 0x0
.LC403b:
	.byte 0x0
.LC403c:
	.byte 0x0
.LC403d:
	.byte 0x0
.LC403e:
	.byte 0x0
.LC403f:
	.byte 0x0
.section .text
.align 16
	.text
.globl foo
.type foo, @function
foo:
.L1150:
.LC1150:
	pushq %rbp
.LC1151:
	movq %rsp, %rbp
.LC1154:
	movq %rdi, -8(%rbp)
.LC1158:
	movq -8(%rbp), %rax
.LC115c:
	movl (%rax), %ecx
.LC115e:
	addl $1, %ecx
.LC1161:
	movl %ecx, (%rax)
.LC1163:
	popq %rbp
.LC1164:
	retq 
.size foo,.-foo
	.text
.globl call
.type call, @function
call:
.L1170:
.LC1170:
pushq %rbx
	pushq %rbp
.LC1171:
	movq %rsp, %rbp
.LC1174:
	subq $0x10, %rsp
.LC1178:
	movl %edi, -4(%rbp)
.LC117b:
	movl %esi, -8(%rbp)
.LC117e:
	cmpl $2, -4(%rbp)
.LC1182:
	jne .L0
.LC1188:
	leaq -8(%rbp), %rdi
.LC118c:
	callq .L1150
jmp .R586
.L1191:
.LC1191:
.L0:
add $0, %rax
callq .L1150
jmp .R34
.R34:
.R586:
	movl -8(%rbp), %eax
.LC1194:
	addq $0x10, %rsp
.LC1198:
	popq %rbp
popq %rbx
.LC1199:
	retq 
.size call,.-call
	.text
.globl main
.type main, @function
main:
.L11a0:
.LC11a0:
	pushq %rbp
.LC11a1:
	movq %rsp, %rbp
.LC11a4:
	subq $0x20, %rsp
.LC11a8:
	movl $0, -4(%rbp)
.LC11af:
	movl %edi, -8(%rbp)
.LC11b2:
	movq %rsi, -0x10(%rbp)
.LC11b6:
	cmpl $3, -8(%rbp)
.LC11ba:
	je .L11e2
.LC11c0:
	movl -8(%rbp), %eax
.LC11c3:
	subl $1, %eax
.LC11c6:
	leaq .LC2004(%rip), %rdi
.LC11cd:
	movl %eax, %esi
.LC11cf:
	movb $0, %al
.LC11d1:
	callq printf@PLT
.LC11d6:
	movl $0, -4(%rbp)
.LC11dd:
	jmp .L1210
.L11e2:
.LC11e2:
	movq -0x10(%rbp), %rax
.LC11e6:
	movq 8(%rax), %rdi
.LC11ea:
	callq atoi@PLT
.LC11ef:
	movl %eax, -0x14(%rbp)
.LC11f2:
	movq -0x10(%rbp), %rcx
.LC11f6:
	movq 0x10(%rcx), %rdi
.LC11fa:
	callq atoi@PLT
.LC11ff:
	movl %eax, -0x18(%rbp)
.LC1202:
	movl -0x14(%rbp), %edi
.LC1205:
	movl -0x18(%rbp), %esi
.LC1208:
	callq .L1170
.LC120d:
	movl %eax, -4(%rbp)
.L1210:
.LC1210:
	movl -4(%rbp), %eax
.LC1213:
	addq $0x20, %rsp
.LC1217:
	popq %rbp
.LC1218:
	retq 
.size main,.-main
