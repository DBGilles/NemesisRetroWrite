#include <string.h> 
#include <stdio.h> 
#include <stdlib.h> 

void foo(int* x){
	*x += 1;
}

int call(int a, int b){
	if (a == 2){
		foo(&b); 
	}	
	
	return b;
}

int main(int argc, char* argv[]){
	if (argc != 3){
		printf("Incorrect number of arguments supplied: %i \n", argc-1); 
		return 0; 
	}
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);  
	return call(a, b); 
}
