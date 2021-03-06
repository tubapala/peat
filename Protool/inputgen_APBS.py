#!/usr/bin/env python
#
# # Protool - Python class for manipulating protein structures
# Copyright (C) 2010 Jens Erik Nielsen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Contact information: 
# Email: Jens.Nielsen_at_gmail.com
# Normal mail:
# Jens Nielsen
# SBBS, Conway Institute
# University College Dublin
# Dublin 4, Ireland

import errors

class inputGen:
    #
    # Creating input files for the pKa calculations
    #
    
    def __init__(self, Protool_instance,settings=None):
        """
            Initialize the inputGen class
            
            Parameters
                pqrpath: The full path to the PQR file (string)
                center_residue: The residue on which the fine grid will be centered
        """
        #
        # Defs by Jens
        # Override by anything in settings
        #defaults={'sdie':78.54,'pdie':8.0,
        #          'finegridpoints':[65,65,65],
        #          'coarsedim':[],
        #          'method':'mg-auto',
        #          'ions':[[-1,0.150,2.0],[1,0.150,2.0]]}
        defaults={'sdie':78.54,'pdie':8.0,
                  'finegridpoints':[65,65,65],
                  'coarsedim':[],
                  'method':'mg-auto',
                  'ions':[[-1,0.0,2.0],[1,0.0,2.0]],
                  'use_epsmap':False}

        if settings:
            for k in settings.keys():
                defaults[k]=settings[k]
        self.ions=defaults['ions']
        #
        # PQR file
        #
        self.P=Protool_instance
        #
        # Write a simple PQR file for this protein
        #
        import os
        self.pqrfile=os.path.join(os.getcwd(),'Protool_pqrfile')
        self.P.writepqr(self.pqrfile)
        pqrpath=self.pqrfile
        self.pqrname=pqrpath
        self.fullpath=pqrpath
        self.type='not set'
        #
        center,extent=self.getCenter()
        #
        # Make the coarse grid twice as big as the protein
        #
        for axis in extent:
            defaults['coarsedim'].append(axis*3.0)
        #
        # Center coarse grid on the center of the molecule
        #
        defaults['coarsecent']=center
        #
        # fine grid is 16.25 (res = 0.25 A/grid point)
        #
        defaults['finedim']=[16.25,16.25,16.25]
        #
        # Center the fine grid on the center of the protein to start with
        #
        defaults['finecent']=center
        #
        # Set all the attributes
        #
        for prop in defaults.keys():
            setattr(self,prop,defaults[prop])
        return

    #
    # -----
    #
    
    def getCenter(self):
        #
        # Reads the PQR file and get the dimensions and the center of the molecule
        #
        import string
        coords=[]
        fd=open(self.pqrfile)
        line=fd.readline()
        while line:
            split=string.split(line)
            if split[0] in ['ATOM','HETATM']:
                x=float(line[30:38])
                y=float(line[39:46])
                z=float(line[47:55])
                coords.append([x,y,z])
            line=fd.readline()
        fd.close()
        #
        # Find extent 
        #
        minmax=[[999.9,-999.9],[999.9,-999.9],[999.9,-999.9]]
        for coord in coords:
            for axis in xrange(3):
                if coord[axis]<minmax[axis][0]:
                    minmax[axis][0]=coord[axis]
                if coord[axis]>minmax[axis][1]:
                    minmax[axis][1]=coord[axis]
        #
        # Calc the geometric center and extent
        #
        center=[0,0,0]
        extent=[0,0,0]
        for axis in xrange(3):
            extent[axis]=minmax[axis][1]-minmax[axis][0]
            center[axis]=extent[axis]/2.0+minmax[axis][0]
        return center,extent
    
    def setfineCenter(self, center):
        #
        # Set the center of the fine grid to center
        #
        self.finecent = center
        return

    def set_method(self,method):
        #
        # Set the method
        #
        self.method=method
        return

    def set_type(self,type):
        #
        # Set the type of calculation
        #
#        print 'type: %s' % (type)
        self.type=type
        if type=='desolv':
            self.set_method('mg-manual')
        elif type=='background': 
            self.set_method('mg-auto')
            self.finedim=[self.coarsedim[0]/1.5,self.coarsedim[1]/1.5,self.coarsedim[2]/1.5]
        elif type=='intene':
            self.set_method('mg-auto')
            self.setfineCenter(self.coarsecent)
            #
            # Set the grid to be a little bigger than the protein
            #
            self.finedim=[self.coarsedim[0]/1.5,self.coarsedim[1]/1.5,self.coarsedim[2]/1.5]
        else:
            #
            # Not a known type
            #
            raise errors.ProtoolError, 'unknown typei %s' % type
        return
        
    def getText_sub(self):
        """
            Get the text associated with the inputgen object

            Returns
                text:  The input file (string)
        """
        
        text  = "read\n"
        text += "    mol pqr %s\n" % self.pqrname
        if self.use_epsmap:
            for i in range(3):
                text += "    diel dx xdiel%d.dx ydiel%d.dx zdiel%d.dx\n"%(i, i, i)
        text += "end\n"
        text += "elec\n"
        text += "    %s\n" % self.method
        text += "    dime %i %i %i\n" % (self.finegridpoints[0], self.finegridpoints[1], self.finegridpoints[2])
        if self.method=='mg-auto':
            text += "    cglen %.4f %.4f %.4f\n" % (self.coarsedim[0], self.coarsedim[1], self.coarsedim[2])
            text += "    cgcent %.3f %.3f %.3f\n" %(self.coarsecent[0],self.coarsecent[1],self.coarsecent[2])
        
            text += "    fglen %.4f %.4f %.4f\n" % (self.finedim[0], self.finedim[1], self.finedim[2])
            text += "    fgcent %.3f %.3f %.3f\n" %(self.finecent[0],self.finecent[1],self.finecent[2])
        elif self.method=='mg-manual':
            text += "    glen %.4f %.4f %.4f\n" % (self.coarsedim[0], self.coarsedim[1], self.coarsedim[2])
            text += "    gcent %.3f %.3f %.3f\n" %(self.coarsecent[0],self.coarsecent[1],self.coarsecent[2])
            text += "    nlev 4\n"
            
        else:
            raise errors.ProtoolError, 'unknown method'
        #
        text += "    mol 1\n"                            
        text += "    lpbe\n"                             
        text += "    bcfl sdh\n"
        for charge,conc,radius in self.ions:
            text += "    ion \n     charge %5.2f\n     conc %6.3f\n     radius %5.2f\n" %(charge,conc,radius)            
        text += "    pdie %5.2f\n"  %self.pdie                
        text += "    sdie %5.2f\n" %self.sdie                
        text += "    srfm smol\n"                   
        text += "    chgm spl2\n"
        text += "    srad 1.4\n"          
        text += "    swin 0.3\n"         
        text += "    sdens 10.0\n"
        text += "    temp 298.15\n"     
        text += "    calcenergy total\n"
        text += "    calcforce no\n"
        text += "    write pot dx pot\n"
        text += "    write smol dx acc\n"
        text += "    write dielx dx xdiel%\n"
        text += "    write diely dx ydiel%\n"
        text += "    write dielz dx zdiel%\n"
        text += "    write kappa dx kappa%\n"
        text += "end\n"
        return text

    #
    # ------
    #

    def getText(self):
        #
        # Energy statements
        #
        text=self.getText_sub()
        if self.type=='background' or self.type=='intene':
            text += "\nprint energy 1 end\n"
            text += "\nquit\n"
            return text
        elif self.type=='desolv':
            #
            # For desolvation calcs, we calculate again with pdie=sdie
            #
            #oldpdie=self.pdie
            #self.pdie=self.sdie
            #text=text+self.getText_sub()
            #self.pdie=oldpdie
            #text += "\nprint energy 1 - 2 end\n"
            text += "\nquit\n"
            return text
        #
        # Eh?
        #
        raise errors.ProtoolError, 'type not set'

    #
    # ------
    #
    
    def printInput(self):
        import string
        period = string.find(self.fullpath,".")
        if period > 0:
            outname = self.fullpath[0:period] + ".in"
        else:
            outname = self.fullpath + ".in"
        file = open(outname, "w")
        file.write(self.getText())
        file.close()
        return outname
        
def main():
    import sys
    X=inputGenpKa(sys.argv[1],13)


if __name__ == "__main__":
    main()
