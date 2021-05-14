#include <stdio.h> 


int main(){
	int input; 
	printf("enter integer\nboundaries are 25, 50, 75\n"); 
	scanf("%i", &input); 
	
	if (input < 50){
		if (input < 25){
			return 0;  
		} else {
			return 1;
		}
	} else{ 
		if (input < 75){
			return 2; 
		} else {
			return 3;
		}
	}

}
