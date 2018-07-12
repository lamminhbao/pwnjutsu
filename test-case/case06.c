// gcc -m32 -fno-stack-protector case06.c -o case06
#include <stdio.h>

void f() {
	char s[16];
	gets(s);
	printf("-> %s\n", s);

}

void main() {
	f();
}