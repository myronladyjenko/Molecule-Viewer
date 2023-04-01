from http.server import HTTPServer, BaseHTTPRequestHandler;
import io;
import sys;
import MolDisplay;
import re;
import molsql;
import urllib;

db = molsql.Database(reset=True);

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
            print(path);
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
        elif "styles.css" in self.path:  
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
        if self.path == "/form_handler.html":
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
        elif self.path == "/molecule":
            # read the data from the server
            contentLength = int(self.headers.get('Content-length'));
            data_obtained = self.rfile.read(contentLength);
            temp_data = data_obtained;

            try:
                arr = data_obtained.decode('utf-8').split("\n");
            except UnicodeDecodeError:
                self.send_response(404);
                self.end_headers();
                self.wfile.write(bytes("404: not found", "utf-8"));
                return;

            # parse data obtained from the server to find correct information about rotations
            pattern = re.compile(r'^(Content-Disposition: form-data; name="(?:roll|pitch|yaw)"(?:\n|\r\n?)(?:\n|\r\n)(?:[+-]?\d+\.?[0]?\s+)(?:\n?|\r\n?))', re.MULTILINE);
            matchObject = pattern.findall(temp_data.decode('utf-8'));
 
            rot = { 'roll': 0,
		            'pitch': 0,
		            'yaw': 0,
	              };

            for index in range(len(matchObject)):
                getRot = re.search(r'roll', str(matchObject[index]));
                if getRot != None:
                    rot['roll'] = searchNum(matchObject[index])
                getRot = re.search(r'pitch', str(matchObject[index]));
                if getRot != None:
                    rot['pitch'] = searchNum(matchObject[index]);   
                getRot = re.search(r'yaw', str(matchObject[index]));
                if getRot != None:
                    rot['yaw'] = searchNum(matchObject[index]);

            # create a molecule and populate it
            mol = MolDisplay.Molecule();
            str_to_display = io.BytesIO(data_obtained);
            wrapper = io.TextIOWrapper(str_to_display, encoding = 'utf-8');
            mol.parse(wrapper);
            mol.sort();

            if rot['roll'] >= 0 and rot['pitch'] >= 0 and rot['yaw'] >= 0: 
                mol.rotation(rot['roll'], rot['pitch'], rot['yaw']);
                mol.sort();

            # send response back and display the molecule
            self.send_response(200);
            self.send_header("Content-type", "image/svg+xml");
            self.send_header("Content-length", len(mol.svg()));
            self.end_headers();

            self.wfile.write(bytes(mol.svg(), "utf-8"));
            return;
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
