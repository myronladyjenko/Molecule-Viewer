# Author Information
- Myron Ladyjenko
- 1172255
- A3 + Nightmare mode

!!! IMPORTNAT !!!      
I have completed the assignment in Nightmare mode. To enable Nightmare mode, call method svg() on a Molecule object (MolDisplay.Molecule()) with a parameter "True". Also, MAKE SURE to use my submitted molecule.i file (pushed to GitLab). It contains extra functions to get atoms from the bond in svg() methods of the Bond class (in MolDisplay.py). Example code:
```
mol = MolDisplay.Molecule();
mol.svg(True);
```
This will call svgNightmare() instead of svg() inside the Bond class. Note that if you pass nothing to svg() method of the Molecule class, the Nightmare node is set to False.

# Compiling
To compile the program, please execute the following command:
```
make
```
or
```
make libmol.so _molecule.so
```
Note that my makefile contains other dependecies that were used for testing. Please, ignore them.
