import math
import molecule;
import re;

header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">""";
footer = """</svg>""";

offsetx = 500;
offsety = 500;

# create an Atom wrapper class for passed atom
class Atom:
	def __init__(self, c_atom):
		self.c_atom = c_atom;
		self.z = c_atom.z;

	# create svg string to display atoms
	def svg(self):
		return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)" />\n' \
				% (self.c_atom.x * 100.0 + offsetx, self.c_atom.y * 100.0 + offsety, \
				radius[self.c_atom.element], element_name[self.c_atom.element]);

	def __str__(self):
		return 'Attributes of an atom: %s %.2f %.2f %.2f' % (self.c_atom.element, self.c_atom.x, self.c_atom.y, self.z)

# create an Bond wrapper class
class Bond:
	def __init__(self, c_bond):
		self.c_bond = c_bond;
		self.z = c_bond.z;
	
	# Create bond svg required by the assignment
	def svg(self):
		bond = self.c_bond;

		x1 = bond.x1 * 100 + bond.dy * 10 + offsetx;
		y1 = bond.y1 * 100 + bond.dx * 10 * (-1) + offsety;

		x2 = bond.x2 * 100 + bond.dy * 10 + offsetx;
		y2 = bond.y2 * 100 + bond.dx * 10 * (-1) + offsety;

		x3 = bond.x2 * 100 - bond.dy * 10 + offsetx;
		y3 = bond.y2 * 100 - bond.dx * 10 * (-1) + offsety;

		x4 = bond.x1 * 100 - bond.dy * 10 + offsetx;
		y4 = bond.y1 * 100 - bond.dx * 10 * (-1) + offsety;
		return ' <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x1, y1, x2, y2, x3, y3, x4, y4);

# Create svg string to display bonds for Nightmare mode
	def svgNightmare(self):
		finalString = "";
		bond = self.c_bond;

		# get the atom1 on each side of the bond (from molecule.i)
		# recalculate dx and dy using 3d distance
		atom1 = bond.get_atom_1();
		atom2 = bond.get_atom_2();
		x1 = atom1.x;
		x2 = atom2.x;
		y1 = atom1.y;
		y2 = atom2.y;
		z1 = atom1.z;
		z2 = atom2.z;

		length = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2);
		dx = (x2 - x1) / length;
		dy = (y2 - y1) / length;

		x1 = bond.x1 * 100 + bond.dy * 15 + offsetx;
		y1 = bond.y1 * 100 + bond.dx * 15 * (-1) + offsety;
		x2 = bond.x2 * 100 + bond.dy * 15 + offsetx;
		y2 = bond.y2 * 100 + bond.dx * 15 * (-1) + offsety;
		x3 = bond.x2 * 100 - bond.dy * 15 + offsetx;
		y3 = bond.y2 * 100 - bond.dx * 15 * (-1) + offsety;
		x4 = bond.x1 * 100 - bond.dy * 15 + offsetx;
		y4 = bond.y1 * 100 - bond.dx * 15 * (-1) + offsety;

		startx1 = bond.x1 * 100 + offsetx;
		starty1 = bond.y1 * 100 + offsety;
		startx2 = bond.x2 * 100 + offsetx;
		starty2 = bond.y2 * 100 + offsety;

		cx = 0;
		cy = 0;
		rotDeg = 0;
		slope = 0;
		# based on the far away atom, shrink the bond
		if (z1 < z2):
			scale = math.sqrt(radius[atom1.element] * radius[atom1.element] - 30**2 / 4);
			x1 = x1 + dx * (scale);
			x4 = x4 + dx * (scale);
			y1 = y1 + dy * (scale);
			y4 = y4 + dy * (scale);

			scale2 = math.sqrt(radius[atom2.element] * radius[atom2.element] - 30**2 / 4);
			x2 = x2 - dx * (scale2);
			x3 = x3 - dx * (scale2);
			y2 = y2 - dy * (scale2);
			y3 = y3 - dy * (scale2);

			cx = startx1 + dx * (scale);
			cy = starty1 + dy * (scale);

			if (x1 == x2):
				rotDeg = 0;
			else:
				rotDeg = math.atan((y1 - y2) / (x1 - x2)) * 180 / math.pi;

			if (startx1 == startx2):
				slope = (starty1 - starty2);
			else:
				slope = (starty1 - starty2) / (startx1 - startx2);
		else:
			scale = math.sqrt(radius[atom2.element] * radius[atom2.element] - 30**2 / 4);
			x2 = x2 - dx * (scale);
			x3 = x3 - dx * (scale);
			y2 = y2 - dy * (scale);
			y3 = y3 - dy * (scale);

			scale2 = math.sqrt(radius[atom2.element] * radius[atom2.element] - 30**2 / 4);
			x1 = x1 + dx * (scale2);
			x4 = x4 + dx * (scale2);
			y1 = y1 + dy * (scale2);
			y4 = y4 + dy * (scale2);

			cx = startx2 - dx * (scale);
			cy = starty2 - dy * (scale);

			if (x2 == x1):
				rotDeg = 0;
			else:
				rotDeg = math.atan((y2 - y1) / (x2 - x1)) * 180 / math.pi;
			
			if (startx1 == startx2):
				slope = (starty1 - starty2);
			else:
				slope = (starty1 - starty2) / (startx1 - startx2);
	
		# This is the coordinates of the width for the bond on a far-away atom
		x1_new = 0;
		y1_new = 0;
		x2_new = 0;
		y2_new = 0;
		if (z1 < z2):
			x1_new = x1;
			y1_new = y1;
			x2_new = x4;
			y2_new = y4;
		else:
			x1_new = x2;
			y1_new = y2;
			x2_new = x3;
			y2_new = y3;

		if (slope < 0):
			if (y2_new > y1_new):
				temp = y2_new;
				y2_new = y1_new;
				y1_new = temp;
				temp = x2_new;
				x2_new = x1_new;
				x1_new = temp;

			# add bond gradient
			finalString += f"""  <linearGradient id="Bond{bond.a1}{bond.a2}" x1="{x2_new:.2f}" y1="{y2_new:.2f}" x2="{x1_new:.2f}" y2="{y1_new:.2f}" gradientUnits="userSpaceOnUse">
									<stop offset="0%" stop-color="#454545" />
									<stop offset="25%" stop-color="#606060" />
									<stop offset="50%" stop-color="#454545" />
									<stop offset="100%" stop-color="#252525" />
								</linearGradient>\n"""
			
			# add ellipse gradient
			finalString += f"""  <linearGradient id="Ellipse{bond.a1}{bond.a2}" x1="{x2_new:.2f}" y1="{y2_new:.2f}" x2="{x1_new:.2f}" y2="{y1_new:.2f}" gradientUnits="userSpaceOnUse" gradientTransform="rotate({-rotDeg}, {cx:.2f}, {cy:.2f})">
									<stop offset="0%" stop-color="#454545" />
									<stop offset="25%" stop-color="#606060" />
									<stop offset="50%" stop-color="#454545" />
									<stop offset="100%" stop-color="#252525" />
								</linearGradient>\n""";
		else:
			if (y1_new > y2_new):
				temp = y2_new;
				y2_new = y1_new;
				y1_new = temp;
				temp = x2_new;
				x2_new = x1_new;
				x1_new = temp;
			
			x11 = x1_new + (x1_new - x2_new);
			y11 = y1_new + (y1_new - y2_new);
			finalString += f"""  <linearGradient id="Bond{bond.a1}{bond.a2}" x1="{x2_new:.2f}" y1="{y2_new:.2f}" x2="{(x11):.2f}" y2="{(y11):.2f}" gradientUnits="userSpaceOnUse">
									<stop offset="0%" stop-color="#252525" />
									<stop offset="25%" stop-color="#404040" />
									<stop offset="50%" stop-color="#252525" />
									<stop offset="100%" stop-color="#050505" />
								</linearGradient>\n""";

			# add ellipse gradient
			finalString += f""" <linearGradient id="Ellipse{bond.a1}{bond.a2}" x1="{x2_new:.2f}" y1="{y2_new:.2f}" x2="{x11:.2f}" y2="{y11:.2f}" gradientUnits="userSpaceOnUse" gradientTransform="rotate({-rotDeg}, {cx:.2f}, {cy:.2f})">
									<stop offset="0%" stop-color="#252525" />
									<stop offset="25%" stop-color="#404040" />
									<stop offset="50%" stop-color="#252525" />
									<stop offset="100%" stop-color="#050505" />
								</linearGradient>\n""";
		
		angle = math.acos((abs(z2 - z1)) / (length * 1));
		rx = 15 * math.cos(angle);

		# add polygon to draw the bond itself
		finalString += '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="url(#Bond%d%d)" />\n' % (x1, y1, x2, y2, x3, y3, x4, y4, bond.a1, bond.a2);
		finalString += f"""  <ellipse cx="{cx:.2f}" cy="{cy:.2f}" rx="{rx:.2f}" ry="{15}" fill="url(#Ellipse{bond.a1}{bond.a2})" transform="rotate({rotDeg}, {cx:.2f}, {cy:.2f})" />\n""";
		
		return finalString;


	def __str__(self):
		bond = self.c_bond;
		return 'Attributes of a bond: %d %d %d %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f' % (bond.a1, bond.a2, bond.epairs, bond.x1, bond.y1, \
		 		bond.x2, bond.y2, self.z, bond.len, bond.dx, bond.dy);

# create molecule class the inherits all molecule methods
class Molecule(molecule.molecule):
	def __init__(self):
		super().__init__();

	def __str__(self):
		strAtoms = "";
		for i in range(0, self.atom_no):
			currStringA = '%d. Atoms: %s %f %f %f' \
						   % (i, self.get_atom(i).element, self.get_atom(i).x, self.get_atom(i).y, self.get_atom(i).z);
			strAtoms += "\n" + currStringA;

		strBonds = "";
		for i in range(0, self.bond_no):
			currStringB = '%d. Bonds: %d %d %d' \
						   % (i, self.get_bond(i).a1, self.get_bond(i).a2, self.get_bond(i).epairs);
			strBonds += "\n" + currStringB;
		
		return strAtoms + "\n" + strBonds;

	# this method creates an svg based on the svg for Atoms and Bonds to display Molecule
	def svg(self, Nightmare=False):
		finalString = "";
		finalString += header;

		numAtoms = self.atom_no;
		numBonds = self.bond_no;
		i = 0;
		j = 0;

		# use mergesort merging to sort the atoms based on the z-values 
		while i < numAtoms and j < numBonds:
			a = Atom(self.get_atom(i));
			b = Bond(self.get_bond(j));
			if a.z < b.z:
				finalString += a.svg();
				i += 1;
			else:
				if (Nightmare):
					finalString += b.svgNightmare();
				else:
					finalString += b.svg();
				j += 1;

		while i < numAtoms:
			finalString += Atom(self.get_atom(i)).svg();
			i += 1;

		while j < numBonds:
			if (Nightmare):
				finalString += Bond(self.get_bond(j)).svgNightmare();
			else:
				finalString += Bond(self.get_bond(j)).svg();
			j += 1;

		finalString += footer;
		return finalString;

	def parse(self, file_object):
		# for every line in file, find the line that matches the ones that contains an atom or a bond
		if (file_object == None):
			print("Error: the passed file pointer is None");
			return -1;

		for line in file_object:
			matchAtom = re.findall(r"(?:\+?\-?[0-9]+\.[0-9]{4}\s\w?)", line);
			pattern = re.compile(r"^(\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\n)");
			matchBond = pattern.findall(line);

			if (matchAtom == None and matchBond == None):
				continue;

			# parse atoms
			if (matchAtom != None and len(matchAtom) == 3):
				arr = matchAtom[2].strip().split(' ');
				if (len(arr) == 2):
					x = float(matchAtom[0]);
					y = float(matchAtom[1]);

					z = float(arr[0]);
					name = arr[1];
					self.append_atom(name, x, y, z);

			# parse bonds
			if (matchBond != []):
				arr = matchBond[0].strip().split();

				if (len(arr) >= 3):
					a1 = int(arr[0]);
					a2 = int(arr[1]);
					epairs = int(arr[2]);
					self.append_bond(a1 - 1, a2 - 1, epairs);

def main():
	print("You are in main function of MolDisplay.py file! Use this program as a python library");

if __name__ == "__main__":
 	main();
