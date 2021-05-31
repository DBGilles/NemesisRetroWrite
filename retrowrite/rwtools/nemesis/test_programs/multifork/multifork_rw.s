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
.globl multifork
.type multifork, @function
multifork:
.L1150:
.LC1150:
pushq %r12
	pushq %rbp
.LC1151:
	movq %rsp, %rbp
.LC1154:
	movl %edi, -4(%rbp)
.LC1157:
	movl -4(%rbp), %eax
.LC115a:
	movl %eax, %ecx
.LC115c:
	subl $0xc, %ecx
.LC115f:
	movl %eax, -0xc(%rbp)
.LC1162:
	je .L118f
.LC1168:
movq -0x4(%rbp), %r12
	jmp .L116d
.L116d:
.LC116d:
	movl -0xc(%rbp), %eax
.LC1170:
	subl $0xd, %eax
.LC1173:
	je .L119b
.LC1179:
movq -0x4(%rbp), %r12
	jmp .L117e
.L117e:
.LC117e:
	movl -0xc(%rbp), %eax
.LC1181:
	subl $0x45, %eax
.LC1184:
	je .L11a7
.LC118a:
movq -0x4(%rbp), %r12
	jmp .L11b3
.L118f:
.LC118f:
	movl $0x7b, -8(%rbp)
.LC1196:
	jmp .L4
.L119b:
.LC119b:
	movl $0x81, -8(%rbp)
.LC11a2:
	jmp .L7
.L11a7:
.LC11a7:
	movl $0x6f, -8(%rbp)
.LC11ae:
	jmp .L8
.L11b3:
.LC11b3:
	movl $0, -8(%rbp)
jmp .R592
.L11ba:
.LC11ba:
.L8:
movq -0x4(%rbp), %r12
jmp .R592
.L7:
movq -0x4(%rbp), %r12
add $0, %rax
jmp .R212
.R212:
.L6:
movq -0x4(%rbp), %r12
jmp .R474
.R474:
.L5:
movq -0x4(%rbp), %r12
jmp .R592
.L4:
movq -0x4(%rbp), %r12
add $0, %rax
jmp .R586
.R586:
.L3:
movq -0x4(%rbp), %r12
jmp .R34
.R34:
.L2:
movq -0x4(%rbp), %r12
add $0, %rax
jmp .R440
.R440:
.L1:
movq -0x4(%rbp), %r12
jmp .R495
.R495:
.L0:
movq -0x4(%rbp), %r12
jmp .R16
.R16:
.R592:
	movl -8(%rbp), %eax
.LC11bd:
	popq %rbp
popq %r12
.LC11be:
	retq 
.size multifork,.-multifork
	.text
.globl main
.type main, @function
main:
.L11c0:
.LC11c0:
	pushq %rbp
.LC11c1:
	movq %rsp, %rbp
.LC11c4:
	subq $0x20, %rsp
.LC11c8:
	movl $0, -4(%rbp)
.LC11cf:
	movl %edi, -8(%rbp)
.LC11d2:
	movq %rsi, -0x10(%rbp)
.LC11d6:
	cmpl $2, -8(%rbp)
.LC11da:
	je .L1202
.LC11e0:
	movl -8(%rbp), %eax
.LC11e3:
	subl $1, %eax
.LC11e6:
	leaq .LC2004(%rip), %rdi
.LC11ed:
	movl %eax, %esi
.LC11ef:
	movb $0, %al
.LC11f1:
	callq printf@PLT
.LC11f6:
	movl $0, -4(%rbp)
.LC11fd:
	jmp .L121d
.L1202:
.LC1202:
	movq -0x10(%rbp), %rax
.LC1206:
	movq 8(%rax), %rdi
.LC120a:
	callq atoi@PLT
.LC120f:
	movl %eax, -0x14(%rbp)
.LC1212:
	movl -0x14(%rbp), %edi
.LC1215:
	callq .L1150
.LC121a:
	movl %eax, -4(%rbp)
.L121d:
.LC121d:
	movl -4(%rbp), %eax
.LC1220:
	addq $0x20, %rsp
.LC1224:
	popq %rbp
.LC1225:
	retq 
.size main,.-main
