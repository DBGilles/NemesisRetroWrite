#include <string.h> 
#include <stdio.h> 
#include <stdlib.h> 
#include <x86intrin.h>  

static volatile int v = 0; 

int foo(int x){
	v = x;
	return v++; 
}

int call(int a, int b){
	if (a == 2){
		return foo(b); 
	}	
	
	return 0;
}

int main(int argc, char* argv[]){
	if (argc != 3){
		printf("Incorrect number of arguments supplied: %i \n", argc-1); 
		return 0; 
	}
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);  
	unsigned int start, end; 	
	start = __rdtsc(); 
	int ret = call(a, b); 
	end = __rdtsc(); 
	return start - end;  
}
