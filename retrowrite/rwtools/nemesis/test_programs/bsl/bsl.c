#include <stdio.h> 
#define INTERRUPT_VECTOR_START 0xFFE0
#define INTERRUPT_VECTOR_END   0xFFF0
#define BSL_PASSWORD_LENGTH    (INTERRUPT_VECTOR_END-INTERRUPT_VECTOR_START+1)


#define SUCCESSFUL_OPERATION 0x00
#define BSL_PASSWORD_ERROR   0x05

extern struct SancusModule bsl;

#define LOCKED   0x00
#define UNLOCKED 0xA5A4
static unsigned LockedStatus = LOCKED;

char BSL430_unlock_BSL(char* data){
  int    i;
  int    retValue = 0;
  int    result;
  char *ivt = "0123456789ABCDEF";
  for (i=0; i <= (INTERRUPT_VECTOR_END - INTERRUPT_VECTOR_START); i++, ivt++)
  {
    if (*ivt != data[i])
    {
      retValue |= 0x40;
    }
  }

  if (retValue == 0)
  {
    LockedStatus = UNLOCKED;

    result = SUCCESSFUL_OPERATION;
  }
  else
  {
    LockedStatus = LOCKED;

    result = BSL_PASSWORD_ERROR;
  }

  return result;
}

int main(int argc, char* argv[]){
	if (argc != 2){
    	printf("Incorrect number of arguments supplied: %i \n", argc-1); 
       	return 0; 
   	}
	return BSL430_unlock_BSL(argv[1]); 
}
