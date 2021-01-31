## RetroWrite -- main exectuble 

RetroWrite is supplied a number of arguments, most importantly 
a) path to binary 
b) path where output (assembly file) needs to be stored 

as well as some arguments that are specific to 'asan' (one of the modules they implemented)

first, a 'loader' is created 
```
loader = Loader(/path/to/bin)
```
the loader has members 
```
self.fd = open(fname, 'rb           # file descriptor? a file handel 
self.elffile = ELFFile(self.fd)     #  elftools.elf.elffire.ELFFile -- main class for accessing ELF file (see package pyelftools) 
self.container = Container()
```

This container class contains a number of dictionaries
```
self.functions = dict()
self.function_names = set()
self.sections = dict()
self.globals = None
self.relocations = defaultdict(list)
self.loader = None
# PLT information
self.plt_base = None
self.plt = dict()

self.gotplt_base = None
self.gotplt_sz = None
self.gotplt_entries = list()
```

#### loading function list 
After creating an instance `loader`, RetroWriter loads the function lists from the symbol table 
```
flist = loader.flist_from_symtab()
```
This function constructs a list of symbol tables by iterating over the elffiler sections (elffile provies a function that returns an iterator over all sections)
and adding those that are an instance of `SymbolTableSection`

A `SymbolTableSection` is a `Section` with additional functions for querying the n'th entry (n'th symbol). The object return is an instance of class 
`Symbol` (consisting of a name and an entrym)

After getting all symbol table sections, `flist_from_symtab()` creates a dictionary of functions. It loops over each section, and then iterates over each symbol 
in the symbol table. If the entry shows that it is a function and satisfies certain conditions (e.g. it isn't 'hidden', whatever that may be) it adds an entry 
to the function list dictionary. AN entry maps the 'st_value' to a dictionary containing more information. This 'st_value' is the value of the assosciated symbol,. 
It can be an absolute value or an address, depending on the context.  

After loading the function list, it loads the functions into the `Container` instance. See `loader.load_functions(fn_list)` . 
This function queries the `.text` section (the part that contains the executable instructions). It gets the base address of the text section. 
It iterates over each value in the function_list, and creates `Function` objects. 

The `Function` class is a RetroWrite class that represents functions. It contains a name, start address, btures, etc. 

The information contained in the function list can be used to extract all information neccesary. The keys in the function list dictionary (apparently) represent
offsets from the start of the .text section, and the values contain the information for the corresponding function (such as its size), which can be used to 
extract all the relevant bytes of data. These `Function` objects are then added to the container. This container object contains a dictionary 
`self.functions` that maps function start address to the function objects, and keeps track of function names

**Result** The container contains a mapping from function start addresses to `Function` objects that contain the name, addr, size, bytes, and the binding of the functin 

##### Generating Symbol list and loading data sections  
Now the loader creates a dictionary mapping section names to section metadata (base, size, offset, and align)  
```
slist = loader.slist_from_symtab() 
```
Then, having craeted this dictionary, the loader loads all datasections into the container (the second argument is a filter function that is applied during
the process). This filter function returns true if x is one of [".rodata", ".data", ".bss", ".data.rel.ro", ".init_array"]. 
See <https://docs.oracle.com/cd/E19620-01/805-4693/elf-3/index.html> for more info on the various sections 
```
loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)
```
Each section that satisfies the filter is loaded into the container (analogously to how it loaded in the functions). Using the information obtained 
when loading the section list from the symbol table it extracts the base address, the size, the  actual data (bytes) and the alignment. It stores this information
in a `DataSection` object, and add this object to the container. The container again has a dictionary mapping section names to the corresponding `DataSection` 

*example*  
The very simply print code has the string "result is %i" stored in .rodata 

#### Generating relocatin list and loading relocations 
RetroWrite now generates a 'relocation list'. It does so by iterating over each section that is an instance of a `RelocationSection`. This `RelocationSection` 
is a collection of Relocation Entries. These stored the information found in ELF relocation tables (I think). 

**TODO: wat is die relocation information juist, hoe wordt deze gebruikt?** 

Then, again, the loader adds these objects containing the relocation information to the container object. It addadds this relocation information 
to the section itself 
```
    if section in self.container.sections:
        self.container.sections[section].add_relocations(relocations)
    else:
        print("[*] Relocations for a section that's not loaded:",
              reloc_section)
        self.container.add_relocations(section, relocations)
```

#### loading global data list 
CFR previous lists and adding to container, except now the loaded data is global data (not sure exactly what global means in this context)

#### Container at this point 
What does the container contain at this point? 
1) `container.functions` -- dictionary mapping function locations (offsets I think) to 'Function' object.  
Function object keeps track of information about function -- name, cache (disassembled function I think), start (same as dict key), size, 
bytes (raw bytes of the function), bbstarts (geen idee), and binding (e.g. local or global binding)
2) `container.function_names 1` -- a set of function names. THese are also stored in `container.functions`, but I'm guessing it will be convenient to have
easy access to these as well 
3) `container.sections` -- A dictionary mapping names to DataSection objects (e.g. .rodata : DataSection, .data : Datasection, ...)  
Datasection keeps track of name, cache, base (base address of the section (?)), size, bytes (raw data contained in section), relocations (instances of 
Relocation class), align (how it's aligned), and named globals 
4) `container.globals` --
5)  `container.plt_base` and `container.plt` -- plt stand for Procedure Linkage Table. Procedure Linking Table and Global Offsets Table (GOT) are used 
to resolve addresses whose address isn't known at the time of linking. They have to be resolved by the dynamic linker at runtime   
more info: <https://www.technovelty.org/linux/plt-and-got-the-key-to-code-sharing-and-dynamic-libraries.html>
6) `container.gotplt_x` If there is a .plt.got' section, the information/data in this section is stored in there members . `container.gotplt_entries` contains 
disasembled binary instructions, for some reason? 

#### Creating a Rewriter
```
rw = Rewriter(loader.container, outfile)
```
This constructor first iterates over all sections in container.sections (DataSections)
Datasections are '.rodata', '.init_array', '.data', '.bss'
```
for sec, section in self.container.sections.items():
    section.load()
```

`DataSection.load()` iterates over the (raw) bytes it contains (stored in `DataSection.bytes`) and creates an instance of `DataCell` of size 1 contain 
the single byte
So after `DataSection.load()` the section contains a number of `DataCell` objects that encompass the raw bytes 

Then, in the `Rewriter` constructor
```
for _, function in self.container.functions.items():
    if function.name in Rewriter.GCC_FUNCTIONS:
        continue
    function.disasm()
```

`function.disasm()` disasembles the raw bytes, iterates over the instructions, and then adds an instance of InstructionWrapper to the `Function.cache`
```
    def disasm(self):
        assert not self.cache
        for decoded in disasm.disasm_bytes(self.bytes, self.start):
            self.cache.append(InstructionWrapper(decoded))
```
The `InstructionWrapper` contains all of the information stored in the original decoded instruction (which is a class defined in the disassembly library) --  
cs, address, mnemonic, op string, and size, as well as some before and after list that will be used in instrumentation and `self.cf_leaves_fn` (?).
*IMPORTANT* it looks like this `InstructionWrapper.before` and `InstructionWrapper.after` will contain the instructions you want to add before or after the instruction 
this is where I might have to add new instructions 

#### Symbolize 
Given the container, which now contains information on the various sections and symbols and whatnot, do the symbolization step 
```
rw = Rewriter(loader.container, outfile)
rw.symbolize()

    def symbolize(self):
        symb = Symbolizer()
        symb.symbolize_text_section(self.container, None)
        symb.symbolize_data_sections(self.container, None)

```

Symbolize the text sections (which contains code) using relocation information (stored in container.relocations)

## Package 'pyelftools'
<https://github.com/eliben/pyelftools> 
pyelftools comes with tools for parsing and decoding ELF (elftoofls/elf) and for parsing and decoding DWARF (elftools/dwarf)
RetroWrite uses the former, since it works with elf files  

#### Elf sections 
[source](https://github.com/eliben/pyelftools/wiki/User's-guide)   
>The main informational unit of an ELF file is a "section". The ELFFile entry point class has several methods for conveniently accessing the sections 
>in an ELF file (for example, count the sections, get the Nth sections, iterate over all sections, etc.)
>
>The object returned to represent a section will always implement at least the interface defined by the Section class (elftools/elf/sections.py). 
>This class represents a generic ELF section, allowing dictionary-like access to its header, and getting its data as a buffer. 
>
>Some sections in ELF are special and their semantics is at least partially defined by the standard and various platform ABIs. pyelftools 
>knows about these sections, and has special classes for representing them. For example, when reading a symbol table section from the stream, 
>ELFFile will return a SymbolTableSection class (also in elftools/elf/sections.py). This class provides additional methods for interacting with the 
>symbol table. There are other special sections pyelftools is familiar with, for example StringTableSection (in the same file) and RelocationSection 
>(in elftools/elf/relocation.py).

Section classes are implemented in `elftools/elf/sections.py`

#### SymbolTableSection 
>A section containing the section header table indices corresponding
>to symbols in the linked symbol table. This section has to exist if the
>symbol table contains an entry with a section header index set to
>SHN_XINDEX (0xffff). The format of the section is described at <https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.sheader.html>

From <https://refspecs.linuxfoundation.org/elf/gabi4+/ch4.sheader.html> 
>