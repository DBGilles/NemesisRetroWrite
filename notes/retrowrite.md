git repo: https://github.com/HexHive/retrowrite

paper: https://hexhive.epfl.ch/publications/files/20Oakland.pdf

## Introduction

"The fundamental difficulty for static rewriting techniques
is disambiguating reference and scalar constants, so that a
program can be “reflowed”, i.e., having its code and data
pointers adjusted according to the inserted instrumentation and
data section changes"

RetroWrite approach:  reassembleable assembly -- creates an assembly file
equivalent to what a compiler  emit, i.e., with relocation symbols for the
linker to resolve

This way the linker can resolve the relocation symbols after the added binary
instructions are added, and you dont have to worry about messing up refernces while
adding instructions (denk ik?)

Our rewriting technique,
called RetroWrite, leverages relocation information which
is required for position independent code, and produces assem-
bly files that can be reassembled into binaries.

--> input binary has to be position independent code

two key requirements for fuzzing binaries
1) performance
2) scalability

contributions
a) A static binary rewriting framework that allows sound,
efficient rewriting of 64-bit PIC binaries
b) An instrumentation pass] that allows binaries to be run
with AFL with the same performance as compiler-based
AFL instrumentation
c) An instrumentation pass] that retrofits binaries with
ASAN checks, increasing by 3x orders of magnitude the
efficiency of memory safety analysis for Binaries
d) A comprehensive evaluation of ASan and AFL instrumen-
tation on benchmarks and real-world applications,
followed by a discussion of limitations

## Binary rewriting
broadly, two techniques
1) Dynamic Binary Translation (DBT)
translates the binary while being executed (dynamic -- at runtime)
they leverage runtime information and od not depend on complex statisticala
analysis that may not scale.
2) Static Binary Rewriting
Static rewriting translates binary before it is executed (static -- at 'compile time')
rewriter can utilize complex analysis and optimize memory and runtime overhead

authors: "DBT suffers from prohibitive runtime
overhead and hence reduces efficacy of software testing prac-
tices"
"DBT remains prohibitively xpensive, and cannot compete with static rewrit-
ing techniques which optimize instrumentation offline"
"Static rewriting suffers from its reliance on static analyses, which
adds both imprecision and complexity. Consequently, existing
static techniques do not scale. A solution that combines
the scalability of DBT with the low (runtime) overhead of
static rewriting that remains sufficiently precise to support
security instrumentation is highly desirable. We will show that
reassembleable assembly is such a solution."

## Reassembly
Reassembleable assembly creates assembly files that appear
to be compiler-generated, i.e., they do not contain hard-
coded values but instead assembly labels. The core process
of generating reassembleable assembly is thus symbolization:
converting reference constants into assembler labels. Sym-
bolizing the assembly allows security-oriented rewriters to
directly modify binaries, much like editing compiler-generated
assembly files. Once modified, the symbolized assembly files
can be assembled using any off-the-shelf assembler to generate
an instrumented binary

However, the main drawback of reassembly-based tech-
niques is the requirement of completeness: no constant can
be misclassified as a reference or a scalar

## Retrowrite design
RetroWrite implements static rewriting through re-
assembleable assembly
The core operation to generate re-
assembleable assembly is symbolization, i.e., statically dis-
ambiguating between reference and scalar type for constants
and replacing references with appropriate assembler labels.
For PIC, we adopt a principled symbolization strategy without
heuristics. RetroWrite leverages the relocation information
in PIC binaries to reconstruct all labels that the compiler
previously emitted before a binary was assembled.

## symbolization
We do not use heuristics, rather
Therefore, our approach [to symbolization] is sound by construction and has zero
false positives and false negatives. This means our approach
is generic, and applicable to any real-world PIC binary.

## implementation
Once reassembleable assembly is generated,
writing instrumentation passes to safely instrument binaries at
low-overhead requires three things
(i) a logical abstraction for
analysis and instrumentation passes to operate on, e.g., mod-
ules, functions, or basic block level granularity
(ii) working
around the ABI to ensure the instrumentation does not break the binary
(iii) automatic register allocation to achieve
compiler-like overhead.

Wikipedia:
ABI = Appplication Binary Interface -- interface between two binary program modules
Adhering to an ABI (which may or may not be officially standardized) is
usually the job of a compiler, operating system, or library author

## alternative to retrowrite
Ramblr, like retrowrite it applies symbolization to generate reassembly assembly
to which instructions can more easily be added (I think) 
