int foo(int a, int b, int c){
	if (a < b){
		a += b; 
	}
	return a + b + c; 
}
int main(){
	

	int a, b;
 	a = 10; 
	b = 20; 
	int result; 
	if (a>b){
		result = foo(a, b, 9); 
	}
	else{
		result = 0; 
	}
	return result; 
}
