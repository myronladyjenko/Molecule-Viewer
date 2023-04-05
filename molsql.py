import os;
import sqlite3;
import MolDisplay;

# Creating required tables for the database
elements = """CREATE TABLE IF NOT EXISTS Elements 
              (ELEMENT_NO     INTEGER     NOT NULL,
               ELEMENT_CODE   VARCHAR(3)  NOT NULL,
               ELEMENT_NAME   VARCHAR(32) NOT NULL,
               COLOUR1        CHAR(6)     NOT NULL,
               COLOUR2        CHAR(6)     NOT NULL,
               COLOUR3        CHAR(6)     NOT NULL,
               RADIUS         DECIMAL(3)  NOT NULL,
               PRIMARY KEY (ELEMENT_CODE));"""

atoms = """CREATE TABLE IF NOT EXISTS Atoms 
           (ATOM_ID        INTEGER      NOT NULL PRIMARY KEY AUTOINCREMENT,
            ELEMENT_CODE   VARCHAR(3)   NOT NULL,
            X              DECIMAL(7,4) NOT NULL,
            Y        DECIMAL(7,4)       NOT NULL,
            Z        DECIMAL(7,4)       NOT NULL,
            FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE));"""

bonds = """CREATE TABLE IF NOT EXISTS Bonds 
           (BOND_ID    INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
            A1         INTEGER     NOT NULL,
            A2         INTEGER     NOT NULL,
            EPAIRS     INTEGER     NOT NULL);"""

molecules = """CREATE TABLE IF NOT EXISTS Molecules 
               (MOLECULE_ID    INTEGER     NOT NULL PRIMARY KEY AUTOINCREMENT,
                NAME           TEXT        NOT NULL UNIQUE);"""       

molecule_atom = """CREATE TABLE IF NOT EXISTS MoleculeAtom
                   (MOLECULE_ID    INTEGER     NOT NULL,
                    ATOM_ID        INTEGER     NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                    FOREIGN KEY (ATOM_ID) REFERENCES Atoms(ATOM_ID));"""   

molecule_bond = """CREATE TABLE IF NOT EXISTS MoleculeBond
                   (MOLECULE_ID    INTEGER     NOT NULL,
                    BOND_ID        INTEGER     NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, BOND_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules(MOLECULE_ID),
                    FOREIGN KEY (BOND_ID) REFERENCES Bonds(BOND_ID));"""  

class Database:
    def __init__(self, reset=False):
        if reset == True:
            if (os.path.exists('molecules.db')):
                os.remove('molecules.db');          
        self.connection = sqlite3.connect('molecules.db');
    
    # This function inserts a table to the database
    def create_tables(self):
        conn = self.connection;

        conn.execute(elements);
        conn.execute(atoms);
        conn.execute(bonds);
        conn.execute(molecules);
        conn.execute(molecule_atom);
        conn.execute(molecule_bond);       

    # This function overwrites __setitem__ method 
    # to set items in the table using '[]'  
    def __setitem__(self, table, values):
        if table == None:
            return;

        conn = self.connection;
        strNew = "";
        for i in range(len(values)):
            if (i == len(values) - 1):
                strNew += '?';
            else:
                strNew += '?, ';

        # This inserts a tuple to the database 
        query = "INSERT OR IGNORE INTO %s VALUES (%s)" % (table, strNew);
        conn.execute(query, (values));

    # This function adds atom's attributes to the Atom's table and MoleculeAtom table entry
    def add_atom(self, molname, atom):
        conn = self.connection;
        self['Atoms'] = (None, atom.c_atom.element, atom.c_atom.x, atom.c_atom.y, atom.z);

        data_atom_id = conn.execute("SELECT MAX(ATOM_ID) FROM Atoms");
        atom_id = int(data_atom_id.fetchone()[0]);

        data_molecule_id = conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=(?)", (molname,));
        molecule_id = int(data_molecule_id.fetchone()[0]);

        self['MoleculeAtom'] = (molecule_id, atom_id);

    # This function adds bond's attributes to the Bond's table and MoleculeBond table entry
    def add_bond(self, molname, bond):
        conn = self.connection;
        self['Bonds'] = (None, bond.c_bond.a1, bond.c_bond.a2, bond.c_bond.epairs);

        data_bond_id = conn.execute("SELECT MAX(BOND_ID) FROM Bonds");
        bond_id = int(data_bond_id.fetchone()[0]);

        data_molecule_id = conn.execute("SELECT MOLECULE_ID FROM Molecules WHERE NAME=(?)", (molname,));
        molecule_id = int(data_molecule_id.fetchone()[0]);

        self['MoleculeBond'] = (molecule_id, bond_id);

    # This function is used to add a molecule of type MolDisplay() to Molecules table 
    # and fills out Atoms, Bonds and other respective tables
    def add_molecule(self, name, fp):
        conn = self.connection;
        mol = MolDisplay.Molecule();
        if (mol.parse(fp) == -1):
            print("Error from parsing the file");
            return -1;

        self['Molecules'] = (None, name);
        numAtoms = mol.atom_no;
        numBonds = mol.bond_no;

        for i in range(0, numAtoms):
            a = MolDisplay.Atom(mol.get_atom(i));
            self.add_atom(name, a);

        for i in range(0, numBonds):
            b = MolDisplay.Bond(mol.get_bond(i));
            self.add_bond(name, b);
    
    # This function is used to load a molecule from a Database to the object Molecule
    def load_mol(self, name):
        conn = self.connection;
        mol = MolDisplay.Molecule();

        # This function is used to fetch atom's code and x, y, z values from the table using INNER JOIN and
        # then I append the atom with the retrieved values of the atom
        dataTableAtoms = conn.execute("""SELECT Atoms.ELEMENT_CODE, Atoms.X, Atoms.Y, Atoms.Z FROM Molecules 
                                         INNER JOIN MoleculeAtom ON Molecules.MOLECULE_ID=MoleculeAtom.MOLECULE_ID 
                                         INNER JOIN Atoms ON MoleculeAtom.ATOM_ID=Atoms.ATOM_ID WHERE Molecules.NAME=(?)""", (name,));
        dataTupleAtoms = dataTableAtoms.fetchall();
        for atom in dataTupleAtoms:
            mol.append_atom(str(atom[0]), float(atom[1]), float(atom[2]), float(atom[3]));
        
        # This function is used to fetch bond's code and x, y, z values from the table using INNER JOIN and
        # then I append the bond with the retrieved values of the bond 
        dataTableBonds = conn.execute("""SELECT Bonds.A1, Bonds.A2, Bonds.EPAIRS FROM Molecules 
                                         INNER JOIN MoleculeBond ON Molecules.MOLECULE_ID=MoleculeBond.MOLECULE_ID 
                                         INNER JOIN Bonds ON MoleculeBond.BOND_ID=Bonds.BOND_ID WHERE Molecules.NAME=(?)""", (name,));
        dataTupleBonds = dataTableBonds.fetchall();
        for bond in dataTupleBonds:
            mol.append_bond(bond[0], bond[1], bond[2]);

        return mol;

    # Creates and returns a dictionary between an element symbol(code) radius of the element
    def radius(self):
        conn = self.connection;
        dataDict = conn.execute("""SELECT Elements.ELEMENT_CODE, Elements.RADIUS FROM Elements""");
        dataTupleDict = dataDict.fetchall();
    
        dictionary = {};
        for elem in dataTupleDict:
            dictionary[elem[0]] = elem[1];

        return dictionary;

    # Creates and returns a dictionary between an element symbol(code) name of the element
    def element_name(self):
        conn = self.connection;
        dataDict = conn.execute("""SELECT Elements.ELEMENT_CODE, Elements.ELEMENT_NAME FROM Elements""");
        dataTupleDict = dataDict.fetchall();
    
        dictionary = {};
        for elem in dataTupleDict:
            dictionary[elem[0]] = elem[1];

        return dictionary;

    # This method creates svg statements of gradients to be applied to atoms
    def radial_gradients(self):
        conn = self.connection;
        finalString = "";

        # Get element name and colors from the table Elements 
        data = conn.execute("""SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements""");
        dataTuple = data.fetchall();

        for row in dataTuple:
            radialGradientSVG = f"""  <radialGradient id="{row[0]}" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
                                            <stop offset="0%" stop-color="{row[1]}" />
                                            <stop offset="50%" stop-color="{row[2]}" />
                                            <stop offset="100%" stop-color="{row[3]}" />
                                      </radialGradient>\n""";
            finalString += radialGradientSVG;

        return finalString;

    # This method is used to push the tables to the Database and close the connection
    def __del__(self):
        self.connection.commit();
        self.connection.close();

# MAIN ROUTINE
def main():
	print("You are in main function of molsql.py file! Use this program as a python library");

if __name__ == "__main__":
 	main();