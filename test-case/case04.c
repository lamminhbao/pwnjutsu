// gcc -m32 -fno-stack-protector case04.c -o case04
#include <stdio.h>
#include <unistd.h>

void main() {
	int n = 100;
	char s[32];
	if (n > 0 ) {
		read(0, s, n);
	}
	else {
		printf("Hello\n");
	}
}