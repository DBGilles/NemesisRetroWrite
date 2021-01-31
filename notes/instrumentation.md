1 - RetroWrite: Statically Instrumenting COTS Binaries for Fuzzing and Sanitization
https://hexhive.epfl.ch/publications/files/20Oakland.pdf

"RetroWrite is designed as a framework, with the re-
assembleable assembly-based rewriter at its core. Other mod-
ules can be added to the framework that instrument the gener-
ated assembly files to, e.g., track coverage for greybox fuzzers
or add redzone for ASAN"
--> makes RetroWrite a good choice, because it was designed to be extended with extra modules

Aditionally, they want to make the result performant -- important because
we use this tool for production binaries, so they should be maximally performant.

Requirement: must be compiled as position independent code (PIC/PIE)  
Is dit een probleem? Of eerder een limitatie van de solution?

Requirement: RetroWrite requires a none stripped executable
  
