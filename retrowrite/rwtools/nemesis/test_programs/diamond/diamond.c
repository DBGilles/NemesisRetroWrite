#include <stdlib.h> 
#include <stdio.h> 
int diamond(int a, int b){
	int result; 
	if (a == b){ // secret 
		result = 0; 
	}
	else if (a < b){ // secret
		result = 4; 
	}
	else {
		result = 7; 
	}

	if (b == 10){
		result *= 4; 
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
	return diamond(a, b); 
}

