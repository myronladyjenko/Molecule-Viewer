CC = clang
CFLAGS = -std=c99 -Wall -pedantic
LIBS=-lm

all: libmol.so _molecule.so

libmol.so: mol.o
	$(CC) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -g -c mol.c -fPIC -o mol.o 

_molecule.so: molecule_wrap.o libmol.so 
	$(CC) molecule_wrap.o -dynamiclib -shared -L. -lmol -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7m -o _molecule.so

molecule_wrap.c molecule.py: molecule.i
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -g -c molecule_wrap.c -fPIC -I/usr/include/python3.7m -o molecule_wrap.o

# Tests
runTarget.o: testPart1.c mol.h
	$(CC) $(CFLAGS) -g -c testPart1.c -o runTarget.o

runTarget: runTarget.o libmol.so
	$(CC) runTarget.o -L. -lmol -o runTarget $(LIBS)

runTest: runTarget
	LD_LIBRARY_PATH=. valgrind -v --leak-check=full ./runTarget
#  valgrind -v --leak-check=full

clean:
	rm -f *.o *.so runTarget
