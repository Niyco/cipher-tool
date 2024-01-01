ctools:
	gcc -shared -O3 -o build/ctools.dll $(wildcard src/ctools/*.c)