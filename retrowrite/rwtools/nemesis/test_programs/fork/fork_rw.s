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
.globl fork
.type fork, @function
fork:
.L1150:
.LC1150:
pushq %r9
	pushq %rbp
.LC1151:
	movq %rsp, %rbp
.LC1154:
	movl %edi, -4(%rbp)
.LC1157:
	movl %esi, -8(%rbp)
.LC115a:
	movl $3, -0xc(%rbp)
.LC1161:
	movl -4(%rbp), %eax
.LC1164:
	cmpl -8(%rbp), %eax
.LC1167:
	jge .L0
.LC116d:
	movl -4(%rbp), %eax
.LC1170:
	addl $2, %eax
.LC1173:
	movl %eax, -0xc(%rbp)
jmp .R586
.L1176:
.LC1176:
.L0:
movq -0x4(%rbp), %r9
add $0, %rax
movq -0x4(%rbp), %r9
jmp .R34
.R34:
.R586:
	movl -0xc(%rbp), %eax
.LC1179:
	popq %rbp
popq %r9
.LC117a:
	retq 
.size fork,.-fork
	.text
.globl main
.type main, @function
main:
.L1180:
.LC1180:
	pushq %rbp
.LC1181:
	movq %rsp, %rbp
.LC1184:
	subq $0x20, %rsp
.LC1188:
	movl $0, -4(%rbp)
.LC118f:
	movl %edi, -8(%rbp)
.LC1192:
	movq %rsi, -0x10(%rbp)
.LC1196:
	cmpl $3, -8(%rbp)
.LC119a:
	je .L11c2
.LC11a0:
	movl -8(%rbp), %eax
.LC11a3:
	subl $1, %eax
.LC11a6:
	leaq .LC2004(%rip), %rdi
.LC11ad:
	movl %eax, %esi
.LC11af:
	movb $0, %al
.LC11b1:
	callq printf@PLT
.LC11b6:
	movl $0, -4(%rbp)
.LC11bd:
	jmp .L11f0
.L11c2:
.LC11c2:
	movq -0x10(%rbp), %rax
.LC11c6:
	movq 8(%rax), %rdi
.LC11ca:
	callq atoi@PLT
.LC11cf:
	movl %eax, -0x14(%rbp)
.LC11d2:
	movq -0x10(%rbp), %rcx
.LC11d6:
	movq 0x10(%rcx), %rdi
.LC11da:
	callq atoi@PLT
.LC11df:
	movl %eax, -0x18(%rbp)
.LC11e2:
	movl -0x14(%rbp), %edi
.LC11e5:
	movl -0x18(%rbp), %esi
.LC11e8:
	callq .L1150
.LC11ed:
	movl %eax, -4(%rbp)
.L11f0:
.LC11f0:
	movl -4(%rbp), %eax
.LC11f3:
	addq $0x20, %rsp
.LC11f7:
	popq %rbp
.LC11f8:
	retq 
.size main,.-main
