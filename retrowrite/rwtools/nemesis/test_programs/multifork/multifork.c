#include <stdlib.h> 
#include <stdio.h>
int multifork(int v)
{
  int result;

  switch (v)
  {
    case 12: result = 123; break;
    case 13: result = 129; break;
    case 69: result = 111; break;

    default: result = 0; break;
  }

  return result;
}

int main(int argc, char* argv[]){
	if (argc != 2){
		printf("Incorrect number of arguments supplied: %i \n", argc-1); 
		return 0; 
	}
	int a = atoi(argv[1]);
	return multifork(a); 
}

