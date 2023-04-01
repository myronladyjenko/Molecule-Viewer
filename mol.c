#include "mol.h"

/**
 * @brief This function initializes parameters of atom
 *
 * @param atom - atom to be initialized
 * @param element - name of the atom
 * @param x - x-coordinate of the atom in 3D
 * @param y - y-coordinate of the atom in 3D
 * @param z - z-coordinate of the atom in 3D
 */
void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
 if (atom == NULL) {
    return;
 }

  atom->x = *x;
  atom->y = *y;
  atom->z = *z;

  strcpy(atom->element, element);
}

/**
 * @brief This function gets the parameters stored in atom
 *
 * @param atom - atom to get the values from
 * @param element - name of the atom
 * @param x - x-coordinate of the atom in 3D
 * @param y - y-coordinate of the atom in 3D
 * @param z - z-coordinate of the atom in 3D
 */
void atomget(atom *atom, char element[3], double *x, double *y, double *z) {
  if (atom == NULL) {
    return;
  }

  *x = atom->x;
  *y = atom->y;
  *z = atom->z;

  strcpy(element, atom->element);
}

/**
 * @brief This function initializes the parameters of the bond
 *
 * @param bond - bond to be initialize
 * @param a1 - index of the first atom in the co-valent bond
 * @param a2 - index of the second atom in the co-valent bond
 * @param atoms - pointer to an array of atoms
 * @param epairs - the number of electronic pairs
 */
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
  if (bond == NULL) {
    return;
  }

  bond->a1 = *a1;
  bond->a2 = *a2;
  bond->epairs = *epairs;
  bond->atoms = *atoms;
  compute_coords(bond);
}

/**
 * @brief This function computes the characteristics of the bond
 * (assigns coordinates appropriatly) + calculates the distances
 *
 * @param bond - bond to calculate the characteristics of
 */
void compute_coords(bond *bond) {
  bond->x1 = bond->atoms[bond->a1].x;
  bond->y1 = bond->atoms[bond->a1].y;
  bond->x2 = bond->atoms[bond->a2].x;
  bond->y2 = bond->atoms[bond->a2].y;
  bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2.0;
  bond->len = sqrt((bond->x1 - bond->x2) * (bond->x1 - bond->x2) + (bond->y1 - bond->y2) * (bond->y1 - bond->y2));
  bond->dx = (bond->x2 - bond->x1) / (1.0 * (bond->len));
  bond->dy = (bond->y2 - bond->y1) / (1.0 * (bond->len));
}

/**
 * @brief This function gets the parameters of the bond
 *
 * @param bond - the bond to get the parameters from
 * @param a1 - pointer to the index of the first atom in the bond
 * @param a2 - pointer to the index of the second atom in the bond
 * @param atoms - double pointer that will store the pointer to an array of
 * atoms
 * @param epairs - value to store electronic pairs
 */
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
  if (bond == NULL) {
    return;
  }

  *a1 = bond->a1;
  *a2 = bond->a2;
  *epairs = bond->epairs;
  *atoms = bond->atoms;
}

/**
 * @brief This function allocates memory for the molecule for number of atom_max atoms and number of bond_max bonds
 * 
 * @param atom_max - number of atoms to allocate for
 * @param bond_max - number of bonds to allocate for
 * @return molecule* - new allocated molecule
 */
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {
  molecule *mol = NULL;
  mol = (molecule*) malloc(sizeof(molecule));
  if (mol == NULL) {
    return NULL;
  }

  if (atom_max == 0) {
    mol->atom_max = 0;
    mol->atom_no = 0;
    mol->atoms = NULL;
    mol->atom_ptrs = NULL;
  } else {
    mol->atom_max = atom_max;
    mol->atom_no = 0;


    mol->atoms = (atom *)malloc(sizeof(atom) * atom_max);
    if (mol->atoms == NULL) {
      free(mol);
      return NULL;
    }

    mol->atom_ptrs = (atom **)malloc(sizeof(atom *) * atom_max);
    if (mol->atom_ptrs == NULL) {
      molfree(mol);
      return NULL;
    }
  }

  if (bond_max == 0) {
    mol->bond_max = 0;
    mol->bond_no = 0;
    mol->bonds = NULL;
    mol->bond_ptrs = NULL;
  } else {
    mol->bond_max = bond_max;
    mol->bond_no = 0;
    
    mol->bonds = (bond *)malloc(sizeof(bond) * bond_max);
    if (mol->bonds == NULL) {
      molfree(mol);
      return NULL;
    }

    mol->bond_ptrs = (bond **)malloc(sizeof(bond *) * bond_max);
    if (mol->bond_ptrs == NULL) {
      molfree(mol);
      return NULL;
    }
  }

  return mol;
}

/**
 * @brief This function performs deep copy of the molecule (with reassigning of all the pointers)
 * 
 * @param src the molecule to make the deep copy of 
 * @return molecule* the new copied molecule
 */
molecule *molcopy(molecule *src) {
  if (src == NULL) {
    return NULL;
  }

  molecule *mol = NULL;

  mol = molmalloc(src->atom_max, src->bond_max);
  if (mol == NULL) {
    return NULL;
  }

  mol->atom_no = 0;
  mol->bond_no = 0;

  if (mol->atom_ptrs == NULL && src->atom_max != 0) {
    return NULL;
  }

  if (mol->atoms == NULL && mol->atom_max != 0) {
    return NULL;
  } else {
    for (int i = 0; i < src->atom_no; i++) {
      molappend_atom(mol, &src->atoms[i]);
    }
  }

  if (mol->bond_ptrs == NULL && src->bond_max != 0) {
    return NULL;
  }

  if (mol->bonds == NULL && mol->bond_max != 0) {
    return NULL;
  } else {
    for (int i = 0; i < src->bond_no; i++) {
      molappend_bond(mol, &src->bonds[i]);
      mol->bonds[i].atoms = mol->atoms;
    }
  }

  return mol;
}

/**
 * @brief The function frees the molecule with all of the associated allocated arrays
 * 
 * @param ptr The pointer to the molecule to be freed
 */
void molfree(molecule *ptr) {
  if (ptr == NULL) {
    return;
  }

  free(ptr->atoms);
  free(ptr->atom_ptrs);
  free(ptr->bonds);
  free(ptr->bond_ptrs);
  free(ptr);
}

/**
 * @brief This function appends the atom to the molecule (in the first available postition), 
 * all previous ones have been filled. Note that this function might allocate more space for the atom if needed
 * 
 * @param molecule molecule to append the atom to
 * @param atom atom to append to the mlecule
 */
void molappend_atom(molecule *molecule, atom *atom) {
  if (molecule == NULL) {
    return;
  }

  if (molecule->atom_max == 0 || molecule->atom_max == molecule->atom_no) {
    if (molecule->atom_max == 0) {
      molecule->atom_max += 1;
    } else {
      molecule->atom_max *= 2;
    }

    struct atom* temp = molecule->atoms;
    struct atom* ptr = realloc(molecule->atoms, molecule->atom_max * sizeof(struct atom));
    struct atom** double_ptr = realloc(molecule->atom_ptrs, molecule->atom_max * sizeof(struct atom *));

    if (ptr == NULL || double_ptr == NULL) {
      fprintf(stderr, "realloc() faild in molappend_atom()\n");
      molfree(molecule);
      exit(0);
    }

    if (molecule->atom_max == 1) {
      molecule->atoms = ptr;
      molecule->atom_ptrs = double_ptr;
    } else {
      molecule->atom_ptrs = double_ptr;

      if (molecule->atoms != ptr) {
        molecule->atoms = ptr;

        for (int i = 0; i < molecule->atom_no; i++) {
          int index = (molecule->atom_ptrs[i] - temp);
          molecule->atom_ptrs[i] = &molecule->atoms[index];
        }
      } else {
        molecule->atoms = ptr;
      }
    }
  }

  molecule->atoms[molecule->atom_no] = *atom;
  molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];

  molecule->atom_no += 1;
}

/**
 * @brief This function appends the bond to the molecule (in the first available postition), 
 * all previous ones have been filled. Note that might allocate more space for the bond if needed
 * 
 * @param molecule molecule to append the bond to
 * @param bond bond to append to the molecule
 */
void molappend_bond(molecule *molecule, bond *bond) {
  if (molecule == NULL) {
    return;
  }

  if (molecule->bond_max == 0 || molecule->bond_max == molecule->bond_no) {
    if (molecule->bond_max == 0) {
      molecule->bond_max += 1;
    } else {
      molecule->bond_max *= 2;
    }

    struct bond* temp = molecule->bonds;
    struct bond* ptr = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
    struct bond** double_ptr = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);

    if (ptr == NULL || double_ptr == NULL) {
      fprintf(stderr, "realloc() faild in molappend_bond()\n");
      molfree(molecule);
      exit(0);
    }

    if (molecule->bond_max == 1) {
      molecule->bonds = ptr;
      molecule->bond_ptrs = double_ptr;
    } else {
      molecule->bond_ptrs = double_ptr;

      if (molecule->bonds != ptr) {
        molecule->bonds = ptr;

        for (int i = 0; i < molecule->bond_no; i++) {
          int index = (molecule->bond_ptrs[i] - temp);
          molecule->bond_ptrs[i] = &(molecule->bonds[index]);
        }
      } else {
        molecule->bonds = ptr;
      }
    }
  }

  molecule->bonds[molecule->bond_no] = *bond;
  molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];

  molecule->bond_no += 1;
}

// helper function
/**
 * @brief This function is used as a comparator function for qsort() to sort atoms by the z coordinate.
 * This function detremines whether atom1 has lower, higher or same z-coordinate
 * 
 * @param atom1 first atom to compare z-coordinate of
 * @param atom2 second atom to compare z-coordinate of
 * @return int returns -1 if atom1 has z-ccordinate less than atom2, 1 otherwise and 0 if z-ccordinates are the same
 */
int compare_z_value_in_atoms(const void *atom1, const void *atom2) {
  const atom *atom_1 = *((const atom**)atom1);
  const atom *atom_2 = *((const atom**)atom2);

  double z1 = (double) atom_1->z;
  double z2 = (double) atom_2->z;

  if (z1 < z2) {
    return -1;
  } else if (z1 > z2) {
    return 1;
  } else {
    return 0;
  }
}

// helper function
/**
 * @brief This function is used as a comparator function for qsort() to sort
 * bonds by the average of z-coordinate. This function detremines whether bond1 or bond2 has lower,
 * higher or same z-coordinate
 *
 * @param bond1 first bond to compare the average of z-ccordinates of
 * @param bond2 second bond to compare the average of z-ccordinates of
 * @return int returns -1 if bond1 has z-ccordinate less than bond2, 1
 * otherwise and 0 if z-ccordinates are the same
 */
int compare_z_value_in_bonds(const void *bond1, const void *bond2) {
  const bond *bond_1 = *((bond **)bond1);
  const bond *bond_2 = *((bond **)bond2);

  double z1 = bond_1->z;
  double z2 = bond_2->z;

  if (z1 < z2) {
    return -1;
  } else if (z1 > z2) {
    return 1;
  } else {
    return 0;
  }
}

/**
 * @brief This function is used to sort atom_ptrs and bond_ptrs of the given molecule
 * 
 * @param molecule given molecule, arrays of which are to be sorted
 */
void molsort(molecule *molecule) {
  if (molecule == NULL) {
    return;
  }

  qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *),
        compare_z_value_in_atoms);
  qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *),
        compare_z_value_in_bonds);
}

/**
 * @brief This function is used to compute the x-rotation matrix based on the passed rotation angle (deg)
 * 
 * @param xform_matrix matrix to store x-rotation in
 * @param deg degress to rotate by 
 */
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
  double rad = deg * (M_PI / (1.0 * 180));

  xform_matrix[0][0] = 1;
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = cos(rad);
  xform_matrix[1][2] = -sin(rad);

  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = sin(rad);
  xform_matrix[2][2] = cos(rad);
}

/**
 * @brief This function is used to compute the y-rotation matrix based on the
 * passed rotation angle (deg)
 *
 * @param xform_matrix matrix to store y-rotation in
 * @param deg degress to rotate by
 */
void yrotation(xform_matrix xform_matrix, unsigned short deg) {
  double rad = deg * (M_PI / (1.0 * 180));

  xform_matrix[0][0] = cos(rad);
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = sin(rad);

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = 1;
  xform_matrix[1][2] = 0;

  xform_matrix[2][0] = -sin(rad);
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = cos(rad);
}

/**
 * @brief This function is used to compute the z-rotation matrix based on the
 * passed rotation angle (deg)
 *
 * @param xform_matrix matrix to store z-rotation in
 * @param deg degress to rotate by
 */
void zrotation(xform_matrix xform_matrix, unsigned short deg) {
  double rad = deg * (M_PI / (1.0 * 180));

  xform_matrix[0][0] = cos(rad);
  xform_matrix[0][1] = -sin(rad);
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = sin(rad);
  xform_matrix[1][1] = cos(rad);
  xform_matrix[1][2] = 0;

  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = 1;
}

/**
 * @brief This function performs the rotation specified by the xform_matrix of all of the atoms in the molecule
 * 
 * @param molecule molecule to perform the rotation of the atoms
 * @param matrix rotation matrix (either x,y,z-rotation)
 */
void mol_xform(molecule *molecule, xform_matrix matrix) {
  if (molecule == NULL) {
    return;
  }

  double x = 0.0;
  double y = 0.0;
  double z = 0.0;

  for (int i = 0; i < molecule->atom_no; i++) {
    x = molecule->atoms[i].x;
    y = molecule->atoms[i].y;
    z = molecule->atoms[i].z;

    molecule->atoms[i].x = 1.0 * matrix[0][0] * x + 1.0 * matrix[0][1] * y + 
                           1.0 * matrix[0][2] * z;
    molecule->atoms[i].y = 1.0 * matrix[1][0] * x + 1.0 * matrix[1][1] * y +
                           1.0 *  matrix[1][2] * z;
    molecule->atoms[i].z = 1.0 * matrix[2][0] * x + 1.0 * matrix[2][1] * y +
                           1.0 * matrix[2][2] * z;
  }

  for (int i = 0; i < molecule->bond_no; i++) {
    compute_coords(&molecule->bonds[i]);
  }
}

// Nightmare Mode
/**
 * @brief This function is used to perform and store the rotation of each atom in the molecule for degress of interval 5 (0,5,10,...).
 * One molecule stores rotation for one angle.
 * 
 * @param mol molecule to perform the atoms rotation for x,y,z-rotation matrices in the interval of 5 degrees
 * @return rotations* return the rotation matrix that stores rotations of molecules that differ by 5 degress and for x,y,z-rotations
 */
rotations *spin(molecule *mol) {
  if (mol == NULL) {
    return NULL;
  }

  rotations *rotationsStruct = NULL;
  
  xform_matrix matrixX;
  xform_matrix matrixY;
  xform_matrix matrixZ;
  molecule *molX;
  molecule *molY;
  molecule *molZ;

  rotationsStruct = (rotations *)malloc(sizeof(rotations));
  if (rotationsStruct == NULL) {
    return NULL;
  }

  for (int i = 0; i < 72; i++) {
    xrotation(matrixX, i * 5);
    yrotation(matrixY, i * 5);
    zrotation(matrixZ, i * 5);

    molX = molcopy(mol);
    molY = molcopy(mol);
    molZ = molcopy(mol);

    if (molX == NULL || molY == NULL || molZ == NULL) {
      for (int j = 0; j < i; j++) {
        molfree(rotationsStruct->x[j]);
        molfree(rotationsStruct->y[j]);
        molfree(rotationsStruct->z[j]);
      }

      molfree(molX);
      molfree(molY);
      molfree(molZ);

      return NULL;
    }

    mol_xform(molX, matrixX);
    rotationsStruct->x[i] = molX;
    mol_xform(molY, matrixY);
    rotationsStruct->y[i] = molY;
    mol_xform(molZ, matrixZ);
    rotationsStruct->z[i] = molZ;

    molsort(rotationsStruct->x[i]);
    molsort(rotationsStruct->y[i]);
    molsort(rotationsStruct->z[i]);
  }

  return rotationsStruct;
}

/**
 * @brief This function frees the rotation struct and all of the molecule inside of it
 * 
 * @param rotations rotation struct storing all of the rotations
 */
void rotationsfree(rotations *rotations) {
  if (rotations == NULL) {
    return;
  }

  for (int i = 0; i < 72; i++) {
    molfree(rotations->x[i]);
    molfree(rotations->y[i]);
    molfree(rotations->z[i]);
  }

  free(rotations);
}
