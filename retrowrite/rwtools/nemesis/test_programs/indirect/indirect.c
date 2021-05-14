#include <stdlib.h> 
#include <stdio.h>

static int v;

// a is a secret 
int indirect(int a, int b)
{
  int result = 3;

  if (a < b)
  {
    result = 7;
  }

  /* Secret-dependent branch because result was assigned in a statement
   *  that is control-dependent on another secret-dependent branch.
   */
  if (result == b) 
  {
    v++;
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
	return indirect(a, b); 
}

