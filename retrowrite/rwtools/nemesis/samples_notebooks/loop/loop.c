
int main(){
	int arr[3] = {10, 20, 30}; 
	int condition[3] = {0}; 
    int secret = 4;
	for (int i = 0; i < 3; i++){
		if (secret < arr[i]){
			condition[i] = 420;
		} else {
			condition[i] = 69;
		}
	}
	if (condition[0] == 420){
	    return 100;
	} else{
	return 12;
	}
}
