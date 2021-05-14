#include <stdlib.h>
#include <stdio.h>
void short_branch(int *secret){
	if (*secret < 10){
		if (*secret > 1){
			*secret *= 10;
			return;
		}
	}
	if (*secret < 100){
			secret += 100;
	}
	*secret *= 2;
}




int main(int argc, char* argv[]){
        if (argc != 2){
                printf("Incorrect number of arguments supplied: %i \n", argc-1);
                return 0;
        }
        int a = atoi(argv[1]);
        return 10;
}
