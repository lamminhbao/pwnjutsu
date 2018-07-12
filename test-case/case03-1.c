// gcc -m32 -fno-stack-protector case03-1.c -o case03-1
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void main() {
	char *name = malloc(32);
	char *file = malloc(32);
	strcpy(file, "note.txt");
	gets(name);
	FILE* f = fopen(file, "r");
	char buf[100];
	fread(buf, 100, 1, f);
	printf("%s", buf);
	fclose(f);
}
