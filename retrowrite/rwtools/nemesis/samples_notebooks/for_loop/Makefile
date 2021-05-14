CC=clang 
# flags copied from retrowrite demo makefile https://github.com/HexHive/retrowrite/blob/master/demos/user_demo/Makefile 
CCFLAGS=  -O0 -ggdb -Wall -Wpedantic -Wextra -fPIC -fPIE -pie 

%.o : %.c
	$(CC) -c -o $@ $< $(CCFLAGS) # '-c' compile or assembly source files, but do not link -- output is an object file 

%.s : %.c 
	$(CC) -S -o $@ $< $(CCFLAGS) # '-S' stop after the stafe of compilation proper, do not assembly. output is form of assembler code 

% : %.c 
	$(CC) -o $@ $< $(CCFLAGS) 

.PHONY: clean all 
clean:
	rm *.s *.0 *.exe 

all: 
	make print   
