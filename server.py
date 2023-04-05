from http.server import HTTPServer, BaseHTTPRequestHandler;
import io;
import sys;
import MolDisplay;
import re;
import molsql;
import urllib;
import molecule;

db = molsql.Database(reset=False);
db.create_tables();

# this function searches for the integer value in the string
# returns 0 - if doesn't, value - otherwise
def searchNum(matchObject):
    string = str(matchObject);
    objectFound = re.search(r'([+-]?\d+\.?[0]?\s*?)', string);
    if objectFound != None:
        return int(objectFound[0]);
    return 0;

class MyHTTPRequestHandler (BaseHTTPRequestHandler):
    def do_GET(self):
        if (((".html" ) in self.path) or ((".js" ) in self.path)):
            path = self.path;
            if (("html_files" not in path) and (".js" not in path)):
                path = "/html_files" + path;

            html_page = open("." + path).read();

            # send the html page to the webserver
            self.send_response(200); #OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(html_page));
            self.end_headers();

            self.wfile.write(bytes(html_page, "utf-8"));
        elif ".svg" in self.path: 
            svgImage = open("." + self.path).read();
        
            # send the .svg file to the webserver
            self.send_response(200); #OK
            self.send_header("Content-type", "image/svg+xml");
            self.send_header("Content-length", len(svgImage));
            self.end_headers();

            self.wfile.write(bytes(svgImage, "utf-8"));
        elif ".css" in self.path:  
            style = open("." + self.path).read();
        
            # send the .css file to the webserver
            self.send_response(200); #OK
            self.send_header("Content-type", "text/css");
            self.send_header("Content-length", len(style));
            self.end_headers();

            self.wfile.write(bytes(style, "utf-8" ));
        elif "/images/" in self.path:
            image = open("." + self.path, "rb").read();

            # send the png image to the webserver
            self.send_response(200); #OK
            self.send_header("Content-type", "image/png");
            self.send_header("Content-length", len(image));
            self.end_headers();

            self.wfile.write(image);
        elif self.path == "/":        
            home_page = open("html_files/index.html").read();

            # send the html page to the webserver
            self.send_response(200); #OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(home_page));
            self.end_headers();

            self.wfile.write(bytes(home_page, "utf-8" ));
        else:
            self.send_response(404);
            self.end_headers();
            self.wfile.write(bytes("404: not found", "utf-8"));

    def do_POST(self):
        if self.path == "/post_molecule.html":
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            postvars = urllib.parse.parse_qs(body.decode('utf-8'));

            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();

            header = MolDisplay.header;
            arr = header.split(">");
            MolDisplay.header = arr[0] + ">" + db.radial_gradients();
            mol = db.load_mol(postvars['name'][0]);

            if (postvars['value'][0] == '-1'):
                mx = molecule.mx_wrapper(int(postvars['x_value'][0]), int(postvars['y_value'][0]), int(postvars['z_value'][0]));
                mol.xform(mx.xform_matrix);
            mol.sort();

            svg = "";
            while (True):
                try:
                    svg = mol.svg();
                    break;
                except KeyError as e:
                    error = str(e);
                    errorElem = error.replace("'", "");
                    MolDisplay.radius[errorElem] = 30;
                    MolDisplay.element_name[errorElem] = 'defaultElem';
                    MolDisplay.header += f"""<radialGradient id="defaultElem" cx="-50%" cy="-50%" r="220%" fx="20%" fy="20%">
                                                <stop offset="0%" stop-color="#6F2DA8" />
                                                <stop offset="50%" stop-color="#6F2DA8" />
                                                <stop offset="100%" stop-color="#6F2DA8" />
                                            </radialGradient>\n""";
            
            self.send_response(200); # OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(svg));
            self.end_headers();

            self.wfile.write(bytes(svg, "utf-8"));
        elif self.path == "/molecule_manipulation.html":
            check = False;
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            postvars = urllib.parse.parse_qs(body.decode('utf-8'));

            if (postvars['value'][0] == '1'):
                molNames = db.connection.execute(("SELECT Molecules.NAME FROM Molecules;")).fetchall();
                for i in range(len(molNames)):
                    if (str(postvars['name'][0]) == str(molNames[i][0])):
                        check = True;

            if (check == False):
                if (postvars['value'][0] == '1'):
                    db.add_molecule(postvars['name'][0], io.StringIO(postvars['fileContents'][0]));
                elif (postvars['value'][0] == '-1'):
                    # Here we will delete the molecule accordingly
                    query = """DELETE FROM Atoms WHERE EXISTS (SELECT * FROM MoleculeAtom INNER JOIN Molecules ON
                                Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID WHERE Molecules.NAME=(?) AND MoleculeAtom.ATOM_ID=Atoms.ATOM_ID);"""
                    db.connection.execute(query, (str(postvars['name'][0]),));

                    query = """DELETE FROM Bonds WHERE EXISTS (SELECT * FROM MoleculeBond INNER JOIN Molecules ON
                                Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID WHERE Molecules.NAME=(?) AND MoleculeBond.BOND_ID=Bonds.BOND_ID);"""
                    db.connection.execute(query, (str(postvars['name'][0]),));

                    molId = (db.connection.execute("SELECT MOLECULE_ID FROM Molecules WHERE Molecules.NAME=(?)", (str(postvars['name'][0]),)).fetchall())[0][0];
                    query = """DELETE FROM MoleculeBond WHERE BOND_ID=(?);"""
                    db.connection.execute(query, (molId,));
                    query = """DELETE FROM MoleculeAtom WHERE ATOM_ID=(?);"""
                    db.connection.execute(query, (molId,));

                    db.connection.execute("DELETE FROM Molecules WHERE NAME=(?);", (str(postvars['name'][0]),));

            moleculeNames = db.connection.execute(("SELECT Molecules.NAME FROM Molecules;")).fetchall();
            rows = ""
            error_str="";
            for i in range(len(moleculeNames)):
                dataAtoms = db.connection.execute("""SELECT Atoms.ELEMENT_CODE FROM Molecules 
                                                    INNER JOIN MoleculeAtom ON Molecules.MOLECULE_ID=MoleculeAtom.MOLECULE_ID 
                                                    INNER JOIN Atoms ON MoleculeAtom.ATOM_ID=Atoms.ATOM_ID WHERE Molecules.NAME=(?)""", (moleculeNames[i][0],)).fetchall();
                
                dataBonds = db.connection.execute("""SELECT Bonds.A1 FROM Molecules 
                                                    INNER JOIN MoleculeBond ON Molecules.MOLECULE_ID=MoleculeBond.MOLECULE_ID 
                                                    INNER JOIN Bonds ON MoleculeBond.BOND_ID=Bonds.BOND_ID WHERE Molecules.NAME=(?)""", (moleculeNames[i][0],)).fetchall(); 

                viewButton = """<button id="view{}" class="material-symbols-outlined view-btn-icon"> visibility </button>""".format(i);
                deleteButton = """<button id="view{}" class="material-symbols-outlined delete-btn-icon"> delete </button>""".format(i);
                hiddenDiv = """<tr class="hidden">
                                    <td colspan="5">
                                        <div style="display: flex, flex-direction: column">
                                            <div id="rotations"> </div>
                                            <div class="mol-display-div"></div>
                                        </div>
                                    </td>
                                </tr>"""
              
                if (len(dataAtoms) == 0 or len(dataBonds) == 0):
                    error_str += "2" + "\n";

                rows += "<tr>";
                rows += "<td>" + viewButton + "</td>";
                rows += "<td>" + moleculeNames[i][0] + "</td>";
                rows += "<td>" + str(len(dataAtoms)) + "</td>";
                rows += "<td>" + str(len(dataBonds)) + "</td>";
                rows += "<td>" + deleteButton + "</td>";
                rows += "</tr>";
                rows += hiddenDiv;
            
            html_string = """
                            <body>
                                <table>
                                    <tr>
                                        <th> Display </th>                                       
                                        <th> Molecule name </th>
                                        <th> Number of atoms </th>
                                        <th> Number of Bonds </th>
                                        <th> Remove </th>
                                    </tr>
                                    {}
                                </table>
                            </body>
                          """.format(rows);
            
            if (check == True and postvars['value'][0] == '1'):
                html_string = "1" + "\n" + html_string;
            elif (postvars['value'][0] == '1' and error_str == ""):
                html_string = "0" + "\n" + html_string; 
            elif (postvars['value'][0] == '1'):
                html_string = error_str + html_string;

            self.send_response(200); # OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(html_string));
            self.end_headers();

            self.wfile.write(bytes(html_string, "utf-8"));
        elif self.path == "/elements_manipulation.html":
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            postvars = urllib.parse.parse_qs(body.decode('utf-8'));

            elementsTuple = {};
            if (postvars['value'][0] == '1'):
                elementsTuple = (int(postvars['number'][0]), postvars['code'][0], postvars['name'][0], postvars['color1'][0], postvars['color2'][0], postvars['color3'][0], int(postvars['radius'][0]));
                db['Elements'] = elementsTuple;
            elif (postvars['value'][0] == '-1'):
                db.connection.execute("DELETE FROM Elements WHERE ELEMENT_CODE=(?);", (str(postvars['code'][0]),));

            elementsData = db.connection.execute(("SELECT * FROM Elements;")).fetchall();
            extraInfo = "";

            rows = ""
            for element in elementsData:
                if (postvars['value'][0] == '0'):
                    extraInfo = extraInfo + element[1] + " ";

                rows += "<tr>";
                rows += "<td>" + str(element[0]) + "</td>";
                rows += "<td>" + element[1] + "</td>";
                rows += "<td>" + element[2] + "</td>";
                rows += "<td>" + element[3] + "</td>";
                rows += "<td>" + element[4] + "</td>";
                rows += "<td>" + element[5] + "</td>";
                rows += "<td>" + str(element[6]) + "</td>";
                rows += "</tr>";
            
            html_string = """
                            <body>
                                <table>
                                    <tr>
                                        <th> Element number </th>
                                        <th> Element code </th>
                                        <th> Element name </th>
                                        <th> Element color #1 </th>
                                        <th> Element color #2 </th>
                                        <th> Element color #3 </th>
                                        <th> Radius </th>
                                    </tr>
                                    {}
                                </table>
                            </body>
                          """.format(rows);
            
            if (postvars['value'][0] == '0'):
                html_string = extraInfo + "\n" + html_string;

            self.send_response(200); # OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(html_string));
            self.end_headers();

            self.wfile.write(bytes(html_string, "utf-8"));
        elif self.path == "/form_handler.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs(body.decode('utf-8'));
            form = open((postvars['url'])[0], "r").read();

            self.send_response(200); # OK
            self.send_header("Content-type", "text/html");
            self.send_header("Content-length", len(form));
            self.end_headers();

            self.wfile.write(bytes(form, "utf-8"));
        else:
            self.send_response(404);
            self.end_headers();
            self.wfile.write(bytes("404: not found", "utf-8"));

def main():
    # catch keyboard interrupt to prevent errors when stopping the server
    try:
        httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHTTPRequestHandler);
        httpd.serve_forever();
    except KeyboardInterrupt:
        print("\nShutting down the server...");
        return;

if __name__ == "__main__":
	main();
