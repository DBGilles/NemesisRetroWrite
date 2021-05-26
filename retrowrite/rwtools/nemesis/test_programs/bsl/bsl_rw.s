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
	.byte 0x30
.LC2005:
	.byte 0x31
.LC2006:
	.byte 0x32
.LC2007:
	.byte 0x33
.LC2008:
	.byte 0x34
.LC2009:
	.byte 0x35
.LC200a:
	.byte 0x36
.LC200b:
	.byte 0x37
.LC200c:
	.byte 0x38
.LC200d:
	.byte 0x39
.LC200e:
	.byte 0x41
.LC200f:
	.byte 0x42
.LC2010:
	.byte 0x43
.LC2011:
	.byte 0x44
.LC2012:
	.byte 0x45
.LC2013:
	.byte 0x46
.LC2014:
	.byte 0x0
.LC2015:
	.byte 0x49
.LC2016:
	.byte 0x6e
.LC2017:
	.byte 0x63
.LC2018:
	.byte 0x6f
.LC2019:
	.byte 0x72
.LC201a:
	.byte 0x72
.LC201b:
	.byte 0x65
.LC201c:
	.byte 0x63
.LC201d:
	.byte 0x74
.LC201e:
	.byte 0x20
.LC201f:
	.byte 0x6e
.LC2020:
	.byte 0x75
.LC2021:
	.byte 0x6d
.LC2022:
	.byte 0x62
.LC2023:
	.byte 0x65
.LC2024:
	.byte 0x72
.LC2025:
	.byte 0x20
.LC2026:
	.byte 0x6f
.LC2027:
	.byte 0x66
.LC2028:
	.byte 0x20
.LC2029:
	.byte 0x61
.LC202a:
	.byte 0x72
.LC202b:
	.byte 0x67
.LC202c:
	.byte 0x75
.LC202d:
	.byte 0x6d
.LC202e:
	.byte 0x65
.LC202f:
	.byte 0x6e
.LC2030:
	.byte 0x74
.LC2031:
	.byte 0x73
.LC2032:
	.byte 0x20
.LC2033:
	.byte 0x73
.LC2034:
	.byte 0x75
.LC2035:
	.byte 0x70
.LC2036:
	.byte 0x70
.LC2037:
	.byte 0x6c
.LC2038:
	.byte 0x69
.LC2039:
	.byte 0x65
.LC203a:
	.byte 0x64
.LC203b:
	.byte 0x3a
.LC203c:
	.byte 0x20
.LC203d:
	.byte 0x25
.LC203e:
	.byte 0x69
.LC203f:
	.byte 0x20
.LC2040:
	.byte 0xa
.LC2041:
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
.align 4
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
.type	LockedStatus_4034,@object
.globl LockedStatus_4034
LockedStatus_4034: # 4034 -- 4038
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
.globl BSL430_unlock_BSL
.type BSL430_unlock_BSL, @function
BSL430_unlock_BSL:
.L1140:
.LC1140:
pushq %r13
	pushq %rbp
.LC1141:
	movq %rsp, %rbp
.LC1144:
	movq %rdi, -8(%rbp)
.LC1148:
	movl $0, -0x10(%rbp)
.LC114f:
	leaq .LC2004(%rip), %rax
.LC1156:
	movq %rax, -0x20(%rbp)
.LC115a:
	movl $0, -0xc(%rbp)
.L1161:
.LC1161:
	cmpl $0x10, -0xc(%rbp)
.LC1165:
	jg .L11b1
.LC116b:
	movq -0x20(%rbp), %rax
.LC116f:
	movsbl (%rax), %ecx
.LC1172:
	movq -8(%rbp), %rax
.LC1176:
	movslq -0xc(%rbp), %rdx
.LC117a:
	movsbl (%rax, %rdx), %esi
.LC117e:
	cmpl %esi, %ecx
or -0x4(%rbp), %r13
.LC1180:
	je .L0
.LC1186:
	movl -0x10(%rbp), %eax
.LC1189:
	orl $0x40, %eax
.LC118c:
	movl %eax, -0x10(%rbp)
jmp .R592
.L118f:
.LC118f:
.L0:
movq -0x4(%rbp), %r13
add $0, %rax
movq -0x4(%rbp), %r13
jmp .R16
.R16:
.R592:
	jmp .L1194
.L1194:
.LC1194:
	movl -0xc(%rbp), %eax
.LC1197:
	addl $1, %eax
.LC119a:
	movl %eax, -0xc(%rbp)
.LC119d:
	movq -0x20(%rbp), %rcx
.LC11a1:
	addq $1, %rcx
.LC11a8:
	movq %rcx, -0x20(%rbp)
.LC11ac:
	jmp .L1161
.L11b1:
.LC11b1:
movq -0x4(%rbp), %r13
movq -0x4(%rbp), %r13
movq -0x4(%rbp), %r13
movq -0x4(%rbp), %r13
movq -0x4(%rbp), %r13
add $0, %rax
	cmpl $0, -0x10(%rbp)
.LC11b5:
	jne .L11d1
.LC11bb:
	movl $0xa5a4, .LC4034(%rip)
add $0, %rax
.LC11c5:
	movl $0, -0x14(%rbp)
.LC11cc:
	jmp .L1
.L11d1:
.LC11d1:
	movl $0, .LC4034(%rip)
add $0, %rax
.LC11db:
	movl $5, -0x14(%rbp)
jmp .L1
.L11e2:
.LC11e2:
.L1:
jmp .R495
.R495:
	movl -0x14(%rbp), %eax
.LC11e5:
	movsbl %al, %eax
.LC11e8:
	popq %rbp
popq %r13
add $0, %rax
movq -0x4(%rbp), %r13
.LC11e9:
	retq 
.size BSL430_unlock_BSL,.-BSL430_unlock_BSL
	.text
.globl main
.type main, @function
main:
.L11f0:
.LC11f0:
	pushq %rbp
.LC11f1:
	movq %rsp, %rbp
.LC11f4:
	subq $0x10, %rsp
.LC11f8:
	movl $0, -4(%rbp)
.LC11ff:
	movl %edi, -8(%rbp)
.LC1202:
	movq %rsi, -0x10(%rbp)
.LC1206:
	cmpl $2, -8(%rbp)
.LC120a:
	je .L1232
.LC1210:
	movl -8(%rbp), %eax
.LC1213:
	subl $1, %eax
.LC1216:
	leaq .LC2015(%rip), %rdi
.LC121d:
	movl %eax, %esi
.LC121f:
	movb $0, %al
.LC1221:
	callq printf@PLT
.LC1226:
	movl $0, -4(%rbp)
.LC122d:
	jmp .L1245
.L1232:
.LC1232:
	movq -0x10(%rbp), %rax
.LC1236:
	movq 8(%rax), %rdi
.LC123a:
	callq .L1140
.LC123f:
	movsbl %al, %ecx
.LC1242:
	movl %ecx, -4(%rbp)
.L1245:
.LC1245:
	movl -4(%rbp), %eax
.LC1248:
	addq $0x10, %rsp
.LC124c:
	popq %rbp
.LC124d:
	retq 
.size main,.-main
