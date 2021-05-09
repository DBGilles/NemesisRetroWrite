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
.align 4
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
.type	v_403c,@object
.globl v_403c
v_403c: # 403c -- 4040
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
	movl %edi, -4(%rbp)
.LC1157:
	movl -4(%rbp), %eax
.LC115a:
	movl %eax, .LC403c(%rip)
.LC1160:
	movl .LC403c(%rip), %eax
.LC1166:
	movl %eax, %ecx
.LC1168:
	addl $1, %ecx
.LC116b:
	movl %ecx, .LC403c(%rip)
.LC1171:
	popq %rbp
.LC1172:
	retq 
.size foo,.-foo
	.text
.globl call
.type call, @function
call:
.L1180:
.LC1180:
pushq %r15
	pushq %rbp
.LC1181:
	movq %rsp, %rbp
.LC1184:
	subq $0x10, %rsp
.LC1188:
	movl %edi, -8(%rbp)
.LC118b:
	movl %esi, -0xc(%rbp)
.LC118e:
	cmpl $2, -8(%rbp)
.LC1192:
	jne .L11a8
.LC1198:
	movl -0xc(%rbp), %edi
.LC119b:
	callq .L1150
.LC11a0:
	movl %eax, -4(%rbp)
.LC11a3:
	jmp .L11af
.L11a8:
.LC11a8:
	movl $0, -4(%rbp)
callq .L1150
movq -0x4(%rbp), %r15
jmp .L11af
.L11af:
.LC11af:
	movl -4(%rbp), %eax
.LC11b2:
	addq $0x10, %rsp
.LC11b6:
	popq %rbp
popq %r15
.LC11b7:
	retq 
.size call,.-call
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
	subq $0x30, %rsp
.LC11c8:
	movl $0, -4(%rbp)
.LC11cf:
	movl %edi, -8(%rbp)
.LC11d2:
	movq %rsi, -0x10(%rbp)
.LC11d6:
	cmpl $3, -8(%rbp)
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
	jmp .L1251
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
	movq -0x10(%rbp), %rcx
.LC1216:
	movq 0x10(%rcx), %rdi
.LC121a:
	callq atoi@PLT
.LC121f:
	movl %eax, -0x18(%rbp)
.LC1222:
	rdtsc 
.LC1224:
	shlq $0x20, %rdx
.LC1228:
	orq %rdx, %rax
.LC122b:
	movl %eax, -0x1c(%rbp)
.LC122e:
	movl -0x14(%rbp), %edi
.LC1231:
	movl -0x18(%rbp), %esi
.LC1234:
	callq .L1180
.LC1239:
	movl %eax, -0x24(%rbp)
.LC123c:
	rdtsc 
.LC123e:
	shlq $0x20, %rdx
.LC1242:
	orq %rdx, %rax
.LC1245:
	movl %eax, -0x20(%rbp)
.LC1248:
	movl -0x1c(%rbp), %eax
.LC124b:
	subl -0x20(%rbp), %eax
.LC124e:
	movl %eax, -4(%rbp)
.L1251:
.LC1251:
	movl -4(%rbp), %eax
.LC1254:
	addq $0x30, %rsp
.LC1258:
	popq %rbp
.LC1259:
	retq 
.size main,.-main
