.section .rodata
.align 16
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
	.byte 0x0
.LC2005:
	.byte 0x0
.LC2006:
	.byte 0x0
.LC2007:
	.byte 0x0
.LC2008:
	.byte 0x0
.LC2009:
	.byte 0x0
.LC200a:
	.byte 0x0
.LC200b:
	.byte 0x0
.LC200c:
	.byte 0x0
.LC200d:
	.byte 0x0
.LC200e:
	.byte 0x0
.LC200f:
	.byte 0x0
.LC2010:
	.byte 0x0
.LC2011:
	.byte 0x0
.LC2012:
	.byte 0x0
.LC2013:
	.byte 0x0
.LC2014:
	.byte 0x1
.LC2015:
	.byte 0x0
.LC2016:
	.byte 0x0
.LC2017:
	.byte 0x0
.LC2018:
	.byte 0x0
.LC2019:
	.byte 0x0
.LC201a:
	.byte 0x0
.LC201b:
	.byte 0x0
.LC201c:
	.byte 0x2
.LC201d:
	.byte 0x0
.LC201e:
	.byte 0x0
.LC201f:
	.byte 0x0
.LC2020:
	.byte 0x0
.LC2021:
	.byte 0x0
.LC2022:
	.byte 0x0
.LC2023:
	.byte 0x0
.LC2024:
	.byte 0x3
.LC2025:
	.byte 0x0
.LC2026:
	.byte 0x0
.LC2027:
	.byte 0x0
.LC2028:
	.byte 0x0
.LC2029:
	.byte 0x0
.LC202a:
	.byte 0x0
.LC202b:
	.byte 0x0
.LC202c:
	.byte 0x4
.LC202d:
	.byte 0x0
.LC202e:
	.byte 0x0
.LC202f:
	.byte 0x0
.LC2030:
	.byte 0x1
.LC2031:
	.byte 0x0
.LC2032:
	.byte 0x0
.LC2033:
	.byte 0x0
.LC2034:
	.byte 0x2
.LC2035:
	.byte 0x0
.LC2036:
	.byte 0x0
.LC2037:
	.byte 0x0
.LC2038:
	.byte 0x2
.LC2039:
	.byte 0x0
.LC203a:
	.byte 0x0
.LC203b:
	.byte 0x0
.LC203c:
	.byte 0x3
.LC203d:
	.byte 0x0
.LC203e:
	.byte 0x0
.LC203f:
	.byte 0x0
.LC2040:
	.byte 0x3
.LC2041:
	.byte 0x0
.LC2042:
	.byte 0x0
.LC2043:
	.byte 0x0
.LC2044:
	.byte 0x4
.LC2045:
	.byte 0x0
.LC2046:
	.byte 0x0
.LC2047:
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
.globl kruskal
.type kruskal, @function
kruskal:
.L1140:
.LC1140:
pushq %r10
	pushq %rbp
.LC1141:
	movq %rsp, %rbp
.LC1144:
	subq $0x30, %rsp
.LC1148:
	movq %rdi, -8(%rbp)
.LC114c:
	movq %rsi, -0x10(%rbp)
.LC1150:
	movq %rdx, -0x18(%rbp)
.LC1154:
	movl %ecx, -0x1c(%rbp)
.LC1157:
	movl $0, -0x20(%rbp)
.L115e:
.LC115e:
	movl -0x20(%rbp), %eax
.LC1161:
	cmpl -0x1c(%rbp), %eax
.LC1164:
	jge .L1195
.LC116a:
	movq -0x10(%rbp), %rax
.LC116e:
	movslq -0x20(%rbp), %rcx
.LC1172:
	movl $0xffffffff, (%rax, %rcx, 4)
.LC1179:
	movl -0x20(%rbp), %edx
.LC117c:
	movq -0x18(%rbp), %rax
.LC1180:
	movslq -0x20(%rbp), %rcx
.LC1184:
	movl %edx, (%rax, %rcx, 4)
.LC1187:
	movl -0x20(%rbp), %eax
.LC118a:
	addl $1, %eax
.LC118d:
	movl %eax, -0x20(%rbp)
.LC1190:
	jmp .L115e
.L1195:
.LC1195:
	movl $0, -0x24(%rbp)
.LC119c:
	movl $1, -0x28(%rbp)
.L11a3:
.LC11a3:
	movl -0x28(%rbp), %eax
.LC11a6:
	cmpl -0x1c(%rbp), %eax
.LC11a9:
	jge .L123b
.LC11af:
	movq -8(%rbp), %rax
.LC11b3:
	movslq -0x28(%rbp), %rcx
.LC11b7:
	movl (%rax, %rcx, 4), %edi
.LC11ba:
	movq -0x18(%rbp), %rsi
.LC11be:
	callq .L1260
.LC11c3:
	movl %eax, -0x2c(%rbp)
.LC11c6:
	movq -8(%rbp), %rcx
.LC11ca:
	movl -0x28(%rbp), %eax
.LC11cd:
	addl $1, %eax
.LC11d0:
	movslq %eax, %rdx
.LC11d3:
	movl (%rcx, %rdx, 4), %edi
.LC11d6:
	movq -0x18(%rbp), %rsi
.LC11da:
	callq .L1260
.LC11df:
	movl %eax, -0x30(%rbp)
.LC11e2:
	movl -0x2c(%rbp), %eax
.LC11e5:
	cmpl -0x30(%rbp), %eax
.LC11e8:
	je .L0
.LC11ee:
	movl -0x2c(%rbp), %eax
.LC11f1:
	movq -0x10(%rbp), %rcx
.LC11f5:
	movl -0x24(%rbp), %edx
.LC11f8:
	addl $1, %edx
.LC11fb:
	movl %edx, -0x24(%rbp)
.LC11fe:
	movslq %edx, %rsi
.LC1201:
	movl %eax, (%rcx, %rsi, 4)
.LC1204:
	movl -0x30(%rbp), %eax
.LC1207:
	movq -0x10(%rbp), %rcx
.LC120b:
	movl -0x24(%rbp), %edx
.LC120e:
	addl $1, %edx
.LC1211:
	movl %edx, -0x24(%rbp)
.LC1214:
	movslq %edx, %rsi
.LC1217:
	movl %eax, (%rcx, %rsi, 4)
.LC121a:
	movl -0x30(%rbp), %eax
.LC121d:
	movq -0x18(%rbp), %rcx
.LC1221:
	movslq -0x2c(%rbp), %rsi
.LC1225:
	movl %eax, (%rcx, %rsi, 4)
jmp .R586
.L1228:
.LC1228:
.L0:
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
add $0, %rax
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
add $0, %rax
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
movq -0x4(%rbp), %r10
jmp .R34
.R34:
.R586:
	jmp .L122d
.L122d:
.LC122d:
	movl -0x28(%rbp), %eax
.LC1230:
	addl $2, %eax
.LC1233:
	movl %eax, -0x28(%rbp)
.LC1236:
	jmp .L11a3
.L123b:
.LC123b:
	movl -0x24(%rbp), %eax
.LC123e:
	cltd 
.LC123f:
	movl $2, %ecx
.LC1244:
	idivl %ecx
.LC1246:
	addl $1, %eax
.LC1249:
	movq -0x10(%rbp), %rsi
.LC124d:
	movl %eax, (%rsi)
.LC124f:
	addq $0x30, %rsp
.LC1253:
	popq %rbp
popq %r10
.LC1254:
	retq 
.size kruskal,.-kruskal
	.text
.local find
.type find, @function
find:
.L1260:
.LC1260:
	pushq %rbp
.LC1261:
	movq %rsp, %rbp
.LC1264:
	subq $0x10, %rsp
.LC1268:
	movl %edi, -8(%rbp)
.LC126b:
	movq %rsi, -0x10(%rbp)
.LC126f:
	movq -0x10(%rbp), %rax
.LC1273:
	movslq -8(%rbp), %rcx
.LC1277:
	movl (%rax, %rcx, 4), %edx
.LC127a:
	cmpl -8(%rbp), %edx
.LC127d:
	je .L129f
.LC1283:
	movq -0x10(%rbp), %rax
.LC1287:
	movslq -8(%rbp), %rcx
.LC128b:
	movl (%rax, %rcx, 4), %edi
.LC128e:
	movq -0x10(%rbp), %rsi
.LC1292:
	callq .L1260
.LC1297:
	movl %eax, -4(%rbp)
.LC129a:
	jmp .L12a5
.L129f:
.LC129f:
	movl -8(%rbp), %eax
.LC12a2:
	movl %eax, -4(%rbp)
.L12a5:
.LC12a5:
	movl -4(%rbp), %eax
.LC12a8:
	addq $0x10, %rsp
.LC12ac:
	popq %rbp
.LC12ad:
	retq 
.size find,.-find
	.text
.globl main
.type main, @function
main:
.L12b0:
.LC12b0:
	pushq %rbp
.LC12b1:
	movq %rsp, %rbp
.LC12b4:
	subq $0x220, %rsp
.LC12bb:
	leaq -0x200(%rbp), %rdx
.LC12c2:
	leaq -0x120(%rbp), %rsi
.LC12c9:
	leaq -0x40(%rbp), %rax
.LC12cd:
	leaq .LC2010(%rip), %rcx
.LC12d4:
	movq %rax, %rdi
.LC12d7:
	movq %rsi, -0x208(%rbp)
.LC12de:
	movq %rcx, %rsi
.LC12e1:
	movl $0x38, %ecx
.LC12e6:
	movq %rdx, -0x210(%rbp)
.LC12ed:
	movq %rcx, %rdx
.LC12f0:
	movq %rax, -0x218(%rbp)
.LC12f7:
	callq memcpy@PLT
.LC12fc:
	movq -0x218(%rbp), %rdi
.LC1303:
	movq -0x208(%rbp), %rsi
.LC130a:
	movq -0x210(%rbp), %rdx
.LC1311:
	movl $0xe, %ecx
.LC1316:
	callq .L1140
.LC131b:
	xorl %eax, %eax
.LC131d:
	addq $0x220, %rsp
.LC1324:
	popq %rbp
.LC1325:
	retq 
.size main,.-main
