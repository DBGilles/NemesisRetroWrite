#include <stdlib.h> 
#include <stdio.h>

// int a is secret
int ifcompound(int a, int b, int c)
{
  int result;

  /* Secret-dependent branch */
  if ( (a == b) && (b < c) )
  {
    result = 7;
  }
  else
  {
    result = 3;
  }

  /* Secret-independent branch */
  if ( (b ^ c) == 0)
  {
    result *= 3;
  }

  return result;
}

int main(int argc, char* argv[]){
	if (argc != 4){
		printf("Incorrect number of arguments supplied: %i \n", argc-1); 
		return 0; 
	}
	int a = atoi(argv[1]);
	int b = atoi(argv[2]);  
	int c = atoi(argv[3]);  
	return ifcompound(a, b, c);  
}

