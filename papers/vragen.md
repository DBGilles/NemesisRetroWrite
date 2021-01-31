 - mapping routine: What exactly does the mapping tablae contain?  
"More specifically,
we generate a mapping table from each address in the old code
section to the size of the corresponding rewritten bytes in the
.newsec section"  
The offset corresponds to the amount of aded bytes at the time of copying that insruction?
concrete question: how exactly is the offset calculated?
- clarification on sanitization:  
when memory is allocated, update metadata store  
when memory is read/written, query metadata store ?
- the original code is maintained. Is this to ensure any references to this section is preserved?   
For example the pointer to var in section 3.2
- how is the offset calculated for static brances? based on number of aded instructions? or is it simply the size of the .newsec section?
-
