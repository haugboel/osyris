import struct
import numpy as np
import config_osiris as conf

class OsirisCommon:
     
    def __init__(self):
                
        return

    #=======================================================================================
    # The new field function is used to create a new data field. Say you want to take the
    # log of the density. You create a new field by calling:
    # mydata.new_field(name="log_rho",operation="np.log10(density)",unit="g/cm3",label="log(Density)")
    # The operation string is then evaluated using the 'eval' function.
    #=======================================================================================
    def new_field(self,name,operation="",unit="",label="",verbose=True,values=[]):
        
        if (len(operation) == 0) and (len(values) > 0):
            new_data = values
            op_parsed = operation
            depth = -1
        else:
            [op_parsed,depth] = self.parse_operation(operation)
            try:
                new_data = eval(op_parsed)
            except NameError:
                if verbose:
                    print("Error parsing operation when trying to create variable: "+name)
                    print("The attempted operation was: "+op_parsed)
                return
        self.data[name] = dict()
        self.data[name]["values"   ] = new_data
        self.data[name]["unit"     ] = unit
        self.data[name]["label"    ] = label
        self.data[name]["operation"] = op_parsed
        self.data[name]["depth"    ] = depth+1
        
        return
    
    #=======================================================================================
    # The operation parser converts an operation string into an expression which contains
    # variables from the data dictionary. If a name from the variable list, e.g. "density",
    # is found in the operation, it is replaced by self.data["density"]["values"] so that it
    # can be properly evaluated by the 'eval' function in the 'new_field' function.
    #=======================================================================================
    def parse_operation(self,operation):
        
        max_depth = 0
        # Add space before and after to make it easier when searching for characters before
        # and after
        expression = " "+operation+" "
        # Sort the list of variable keys in the order of the longest to the shortest.
        # This guards against replacing 'B' inside 'logB' for example.
        key_list = sorted(self.data.keys(),key=lambda x:len(x),reverse=True)
        # For replacing, we need to create a list of hash keys to replace on instance at a
        # time
        hashkeys  = dict()
        hashcount = 0
        for key in key_list:
            # Search for all instances in string
            loop = True
            loc = 0
            while loop:
                loc = expression.find(key,loc)
                if loc == -1:
                    loop = False
                else:
                    # Check character before and after. If they are either a letter or a '_'
                    # then the instance is actually part of another variable or function
                    # name.
                    char_before = expression[loc-1]
                    char_after  = expression[loc+len(key)]
                    bad_before = (char_before.isalpha() or (char_before == "_"))
                    bad_after = (char_after.isalpha() or (char_after == "_"))
                    hashcount += 1
                    if (not bad_before) and (not bad_after):
                        theHash = "#"+str(hashcount).zfill(5)+"#"
                        # Store the data key in the hash table
                        hashkeys[theHash] = "self.data[\""+key+"\"][\"values\"]"
                        expression = expression.replace(key,theHash,1)
                        max_depth = max(max_depth,self.data[key]["depth"])
                    else:
                        # Replace anyway to prevent from replacing "x" in "max("
                        theHash = "#"+str(hashcount).zfill(5)+"#"
                        hashkeys[theHash] = key
                        expression = expression.replace(key,theHash,1)
                    loc += 1
        # Now go through all the hashes in the table and build the final expression
        for theHash in hashkeys.keys():
            expression = expression.replace(theHash,hashkeys[theHash])
    
        return [expression,max_depth]
    
    #=======================================================================================
    # The function get returns the values of the selected variable
    #=======================================================================================
    def get(self,var):
        return self.data[var]["values"]
        
    #=======================================================================================
    # This function writes the RAMSES data to a VTK file for 3D visualization
    #=======================================================================================
    def to_vtk(self,fname="osiris_data.vtu",variables=False):
        
        try:
            from scipy.spatial import Delaunay
        except ImportError:
            print("Scipy Delaunay library not found. This is needed for VTK output. Exiting.")

        # Print status
        if not fname.endswith(".vtu"):
            fname += ".vtu"
        print("Writing data to VTK file: "+fname)
        
        # Coordinates ot RAMSES cell centers
        points = np.array([self.get("x"),self.get("y"),self.get("z")]).T
        
        # Compute Delaunay tetrahedralization from cell nodes
        # Note that this step can take a lot of time!
        ncells = self.info["ncells"]
        print("Computing Delaunay mesh with %i points." % ncells)
        print("This may take some time...")
        tri = Delaunay(points)
        ntetra = np.shape(tri.simplices)[0]
        nverts = ntetra*4
        print("Delaunay mesh with %i tetrahedra complete." % ntetra)

        # Create list of variables by grouping x,y,z components together
        nvarmax = len(self.data.keys())
        n_components = [] #np.zeros([nvarmax],dtype=np.int32)
        varlist = []
        varnames = []
        for key in self.data.keys():
            if key.endswith("_x") or key.endswith("_y") or key.endswith("_z"):
                rawkey = key[:-2]
                try:
                    k = len(self.get(rawkey+"_x"))+len(self.get(rawkey+"_y"))+len(self.get(rawkey+"_z"))
                    ok = True
                    for i in range(np.shape(varlist)[0]):
                        for j in range(n_components[i]):
                            if key == varlist[i][j]:
                                ok = False
                                break
                    if ok:
                        varlist.append([rawkey+"_x",rawkey+"_y",rawkey+"_z"])
                        n_components.append(3)
                        varnames.append(rawkey+"_vec")
                except KeyError:
                    varlist.append([key,"",""])
                    n_components.append(1)
                    varnames.append(key)
            else:
                varlist.append([key,"",""])
                n_components.append(1)
                varnames.append(key)
        
        nvars = len(n_components)

        # Compute byte sizes
        nbytes_xyz   = 3 * ncells * 8
        nbytes_cellc =     nverts * 4
        nbytes_cello =     ntetra * 4
        nbytes_cellt =     ntetra * 4
        nbytes_vars  = np.zeros([nvars],dtype=np.int32)
        for i in range(nvars):
            nbytes_vars[i] = n_components[i] * ncells * 8

        # Compute byte offsets
        offsets = np.zeros([nvars+4],dtype=np.int64)
        offsets[0] = 0                             # xyz coordinates
        offsets[1] = offsets[0] + 4 + nbytes_xyz   # cell connectivity
        offsets[2] = offsets[1] + 4 + nbytes_cellc # cell offsets
        offsets[3] = offsets[2] + 4 + nbytes_cello # cell types
        offsets[4] = offsets[3] + 4 + nbytes_cellt # first hydro variable
        for i in range(nvars-1):
            offsets[i+5] = offsets[i+4] + 4 + nbytes_vars[i]
            
        # Open file for binary output
        f = open(fname, "wb")

        # Write VTK file header
        f.write('<?xml version=\"1.0\"?>\n')
        f.write('<VTKFile type=\"UnstructuredGrid\" version=\"0.1\" byte_order=\"LittleEndian\">\n')
        f.write('   <UnstructuredGrid>\n')
        f.write('   <Piece NumberOfPoints=\"%i\" NumberOfCells=\"%i\">\n' % (ncells,ntetra))
        f.write('      <Points>\n')
        f.write('         <DataArray type=\"Float64\" Name=\"Coordinates\" NumberOfComponents=\"3\" format=\"appended\" offset=\"%i\" />\n' % offsets[0])
        f.write('      </Points>\n')
        f.write('      <Cells>\n')
        f.write('         <DataArray type=\"Int32\" Name=\"connectivity\" format=\"appended\" offset=\"%i\" />\n' % offsets[1])
        f.write('         <DataArray type=\"Int32\" Name=\"offsets\" format=\"appended\" offset=\"%i\" />\n' % offsets[2])
        f.write('         <DataArray type=\"Int32\" Name=\"types\" format=\"appended\" offset=\"%i\" />\n' % offsets[3])
        f.write('      </Cells>\n')
        f.write('      <PointData>\n')
        for i in range(nvars):
            f.write('         <DataArray type=\"Float64\" Name=\"'+varnames[i]+'\" NumberOfComponents=\"%i\" format=\"appended\" offset=\"%i\" />\n' % (n_components[i],offsets[i+4]))
        f.write('      </PointData>\n')
        f.write('   </Piece>\n')
        f.write('   </UnstructuredGrid>\n')
        f.write('   <AppendedData encoding=\"raw\">\n')
        f.write('_')

        # Now write data in binary. Every data field is preceded by its byte size.
        
        # x,y,z coordinates of the points
        f.write(struct.pack('<i', *[nbytes_xyz]))
        f.write(struct.pack('<%id'%(ncells*3), *np.ravel(points)))

        # Cell connectivity
        f.write(struct.pack('<i', *[nbytes_cellc]))
        f.write(struct.pack('<%ii'%nverts, *np.ravel(tri.simplices)))

        # Cell offsets
        f.write(struct.pack('<i', *[nbytes_cello]))
        f.write(struct.pack('<%ii'%ntetra, *range(4,ntetra*4+1,4)))

        # Cell types: number 10 is tetrahedron in VTK file format
        f.write(struct.pack('<i', *[nbytes_cellt]))
        f.write(struct.pack('<%ii'%ntetra, *np.full(ntetra, 10,dtype=np.int32)))

        # Hydro variables
        #ivar = 0
        for i in range(nvars):
        #for key in self.data.keys():
            if n_components[i] == 3:
                celldata = np.ravel(np.array([self.get(varlist[i][0]),self.get(varlist[i][1]),self.get(varlist[i][2])]).T)
            else:
                celldata = self.get(varlist[i][0])
            f.write(struct.pack('<i', *[nbytes_vars[i]]))
            f.write(struct.pack('<%id'%(ncells*n_components[i]), *celldata))

        # Close file
        f.write('   </AppendedData>\n')
        f.write('</VTKFile>\n')
        f.close()
        
        # File size
        fsize_raw = offsets[nvars+3] + nbytes_vars[nvars-1]
        if fsize_raw > 1000000000:
            fsize = float(fsize_raw)/1.0e9
            funit = "Gb"
        elif fsize_raw > 1000000:
            fsize = float(fsize_raw)/1.0e6
            funit = "Mb"
        elif fsize_raw > 1000:
            fsize = float(fsize_raw)/1.0e3
            funit = "kb"
        else:
            fsize = float(fsize_raw)
            funit = "b"

        print("File "+fname+(" of size %.1f"%fsize)+funit+" succesfully written.")

        return

#=======================================================================================
# The function finds an arbitrary perpendicular vector to v.
# for two vectors (x, y, z) and (a, b, c) to be perpendicular,
# the following equation has to be fulfilled
#     0 = ax + by + cz
#=======================================================================================    
def perpendicular_vector(v):

    # x = y = z = 0 is not an acceptable solution
    if v[0] == v[1] == v[2] == 0:
        raise ValueError("zero-vector")
    
    if v[2] == 0:
        return [-v[1],v[0],0]
    else:
        return [1.0, 1.0, -1.0 * (v[0] + v[1]) / v[2]]

    #if v[0] == v[1] == 0:
        #return [1,0,0]
    #else:
        #return [-v[1],v[0],0]