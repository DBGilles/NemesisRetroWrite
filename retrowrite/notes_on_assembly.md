## Notes on Assembly and ELF 
This document contains an introduction to how assembly works, the various sections etc. 
Interesting resource: [x86 Assembly Language Reference Manual](https://docs.oracle.com/cd/E19620-01/805-4693/index.html)

## Object files in Exectuable and Linking Format (ELF) 
See reference manual, chapter 3: assembler output 
> This chapter is an overview of ELF (Executable and Linking Format) for the relocatable object files produced by the assembler.

>The main output produced by assembling an input assembly language source file is the translation of that file into an object file in (ELF). ELF files produced
> by the assembler are relocatable files that hold code and/or data. They are input files for the linker. The linker combines these relocatable files with 
>other ELF object files to create an executable file or a shared object file in the next stage of program building, after translation from source files into 
>object files.
>
>The three main kinds of ELF files are relocatable, executable and shared object files.
>
>The assembler can also produce ancillary output incidental to the translation process. For example, if the assembler is invoked with the -V option, 
>it can write information to standard output and to standard error.
>
>The assembler also creates a default output file when standard input or multiple input files are used. Ancillary output has little direct 
> connection to the translation process, so it is not properly a subject for this manual. Information about such output appears in as(1) manual page.
>
> Certain assembly language statements are directives to the assembler regarding the organization or content of the object file to be generated. 
>Therefore, they have a direct effect on the translation performed by the assembler. To understand these directives, described in Chapter 2, 
>Instruction-Set Mapping ", it is helpful to have some working knowledge of ELF, at least for relocatable files.

Compiler output files are ELF files. To verify this run 
```
file /path/to/bin 
```
So a library like Pyelftools can parse this file and determine the names and contents of each of the sections. 
I believe that these sections dont neccesarily correspond to sections in assembly. instead they are sections generated during the compilation process. 


## ELF Section Header 
[source](https://docs.oracle.com/cd/E19620-01/805-4693/elf-2/index.html)
The section header table has all of the information necessary to locate and isolate each of the file's sections. 
A section header entry in a section header table contains information characterizing the contents of the corresponding section, if the file has such a section.
Each entry in the section header table is a section header. A section header is a structure of fixed size and format, consisting of the following fields, or members:
- sh_name : setion name 
- sh_type : section type (see source for the various types)
- sh_flags 
- sh_addr : address where first byte resides if the sectin appears in the memory image of a process 
- sh_offset : specifies byte offset from beginning of the file to the first byte in the section 
- sh_size 
- sh_link 
- sh_info 
- sh_addralign 
- shh_entsize : Some sections hold a table of fixed-size entries, such as a symbol table. For such a section, 
this member gives the size in bytes of each entry. The member contains 0 if the section does not hold a table of fixed-size entries.

## ELF symbol tables 
<https://docs.oracle.com/cd/E19620-01/805-4693/elf-6/index.html> 

## Data sections 
.rodata - contains read only data 
.data - initialized read-write data 
.bass - uninitialized read-write data 
.init - runtime initialization instructions 
[".rodata", ".data", ".bss", ".data.rel.ro", ".init_array"]