// gcc -m32 -fno-stack-protector case05.c -o case05
#include <stdio.h>
#include <unistd.h>

void main() {
	int n;
	char num[32];
	char s[32];
	read(0, num, 32);
	n = atoi(num);
	if (n > 0) {
		read(0, s, n);
	}
	else {
		printf("Hello\n");
	}
}