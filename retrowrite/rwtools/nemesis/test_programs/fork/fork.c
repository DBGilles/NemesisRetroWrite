#include <stdlib.h> 
#include <stdio.h>
int fork(int a, int b){
	int result = 3; 
	if (a < b){
		result = a + 2;
	}
	return result; 
}

int main(int argc, char* argv[]){
	if (argc != 3){
		printf("Incorrect number of arguments supplied: %i \n", argc-1); 
		return 0; 
	}
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);  
	return fork(a, b); 
}

