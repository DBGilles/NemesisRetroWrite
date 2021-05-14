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
.globl ifcompound
.type ifcompound, @function
ifcompound:
.L1150:
.LC1150:
pushq %r11
	pushq %rbp
.LC1151:
	movq %rsp, %rbp
.LC1154:
	movl %edi, -4(%rbp)
.LC1157:
	movl %esi, -8(%rbp)
.LC115a:
	movl %edx, -0xc(%rbp)
.LC115d:
	movl -4(%rbp), %eax
.LC1160:
	cmpl -8(%rbp), %eax
.LC1163:
	jne .L0
.LC1169:
	movl -8(%rbp), %eax
.LC116c:
	cmpl -0xc(%rbp), %eax
.LC116f:
	jge .R586
.LC1175:
	movl $7, -0x10(%rbp)
.LC117c:
	jmp .L1188
.L1181:
.LC1181:
.L0:
movq -0x4(%rbp), %r11
or -0x4(%rbp), %r11
jmp .R34
.R34:
.R586:
	movl $3, -0x10(%rbp)
jmp .L1188
.L1188:
.LC1188:
	movl -8(%rbp), %eax
.LC118b:
	xorl -0xc(%rbp), %eax
.LC118e:
	cmpl $0, %eax
.LC1191:
	jne .L119e
.LC1197:
	imull $3, -0x10(%rbp), %eax
.LC119b:
	movl %eax, -0x10(%rbp)
.L119e:
.LC119e:
	movl -0x10(%rbp), %eax
.LC11a1:
	popq %rbp
popq %r11
.LC11a2:
	retq 
.size ifcompound,.-ifcompound
	.text
.globl main
.type main, @function
main:
.L11b0:
.LC11b0:
	pushq %rbp
.LC11b1:
	movq %rsp, %rbp
.LC11b4:
	subq $0x20, %rsp
.LC11b8:
	movl $0, -4(%rbp)
.LC11bf:
	movl %edi, -8(%rbp)
.LC11c2:
	movq %rsi, -0x10(%rbp)
.LC11c6:
	cmpl $4, -8(%rbp)
.LC11ca:
	je .L11f2
.LC11d0:
	movl -8(%rbp), %eax
.LC11d3:
	subl $1, %eax
.LC11d6:
	leaq .LC2004(%rip), %rdi
.LC11dd:
	movl %eax, %esi
.LC11df:
	movb $0, %al
.LC11e1:
	callq printf@PLT
.LC11e6:
	movl $0, -4(%rbp)
.LC11ed:
	jmp .L1233
.L11f2:
.LC11f2:
	movq -0x10(%rbp), %rax
.LC11f6:
	movq 8(%rax), %rdi
.LC11fa:
	callq atoi@PLT
.LC11ff:
	movl %eax, -0x14(%rbp)
.LC1202:
	movq -0x10(%rbp), %rcx
.LC1206:
	movq 0x10(%rcx), %rdi
.LC120a:
	callq atoi@PLT
.LC120f:
	movl %eax, -0x18(%rbp)
.LC1212:
	movq -0x10(%rbp), %rcx
.LC1216:
	movq 0x18(%rcx), %rdi
.LC121a:
	callq atoi@PLT
.LC121f:
	movl %eax, -0x1c(%rbp)
.LC1222:
	movl -0x14(%rbp), %edi
.LC1225:
	movl -0x18(%rbp), %esi
.LC1228:
	movl -0x1c(%rbp), %edx
.LC122b:
	callq .L1150
.LC1230:
	movl %eax, -4(%rbp)
.L1233:
.LC1233:
	movl -4(%rbp), %eax
.LC1236:
	addq $0x20, %rsp
.LC123a:
	popq %rbp
.LC123b:
	retq 
.size main,.-main
