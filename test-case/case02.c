// gcc -m32 -fno-stack-protector case02.c -o case02
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void main() {
	int a;
	char s[32];
	read(0, s, 32);
	printf(s);
}