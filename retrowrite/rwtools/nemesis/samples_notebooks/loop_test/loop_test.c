
int main(){
	int secret = 4;
	if (secret < 10){
		for (int i = 0; i < 10; i++){
			secret ++; 
		}
	} else{
		secret = 10; 
	}
	return secret; 
} 
