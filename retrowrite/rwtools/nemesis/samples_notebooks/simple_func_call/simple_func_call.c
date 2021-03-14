
int foo(int input){
    int secret = 10;
	if (input < secret){
		return 32;
	} else{
		return 44;
	}
}

int main(){
    int x = foo(10);
    return x;

}
