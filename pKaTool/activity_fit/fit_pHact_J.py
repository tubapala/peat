#!/usr/bin/env python
#
# pKaTool - analysis of systems of titratable groups
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

import numpy 
#import matplotlib.pyplot as plt
#from matplotlib.colors import LinearSegmentedColormap

cdict1 = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 0.1),
                   (1.0, 1.0, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 1.0),
                   (0.5, 0.1, 0.0),
                   (1.0, 0.0, 0.0))
        }

cdict2 = {'red':   ((0.0, 0.0, 0.0),
                   (0.5, 0.0, 1.0),
                   (1.0, 0.1, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.1),
                   (0.5, 1.0, 0.0),
                   (1.0, 0.0, 0.0))
        }

cdict3 = {'red':  ((0.0, 0.0, 0.0),
                   (0.25,0.0, 0.0),
                   (0.5, 0.8, 1.0),
                   (0.75,1.0, 1.0),
                   (1.0, 0.4, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.25,0.0, 0.0),
                   (0.5, 0.9, 0.9),
                   (0.75,0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.0, 0.4),
                   (0.25,1.0, 1.0),
                   (0.5, 1.0, 0.8),
                   (0.75,0.0, 0.0),
                   (1.0, 0.0, 0.0))
        }

def heatmap(values,title='Effect of mutations',firstkey='X',secondkey='Y',colorbar=True,zlabel='Z',firstticks=False,secondticks=False,vmin=None,vmax=None):
    # Now we will use this example to illustrate 3 ways of
    # handling custom colormaps.
    # First, the most direct and explicit:

    blue_red1 = LinearSegmentedColormap('BlueRed1', cdict1)

    # Second, create the map explicitly and register it.
    # Like the first method, this method works with any kind
    # of Colormap, not just
    # a LinearSegmentedColormap:

    blue_red2 = LinearSegmentedColormap('BlueRed2', cdict2)
    #plt.register_cmap(cmap=blue_red2)

    # Third, for LinearSegmentedColormap only,
    # leave everything to register_cmap:

    #plt.register_cmap(name='BlueRed3', data=cdict3) # optional lut kwarg
    #
    # Reformat the data
    #
    X=[]
    Y=[]
    Z=[]
    allvals=[]
    xvals=values.keys()
    xvals.sort()
    yvals=values[xvals[0]].keys()
    yvals.sort()
    for yval in yvals:
        xs=[]
        ys=[]
        zs=[]
        for xval in xvals:
            xs.append(xval)
            ys.append(yval)
            zs.append(values[xval][yval])
            if values[xval][yval]:
                allvals.append(values[xval][yval])
        X.append(xs)
        Y.append(ys)
        Z.append(zs)

    #plt.figure(figsize=(10,10))
    # 
    # Set value axis min and max
    #
    if vmin is None:
        vmin=min(allvals)
    if vmax is None:
        vmax=max(allvals)
    #
    # Plot
    #
    plt.imshow(Z,interpolation='nearest',vmin=vmin,vmax=vmax)#,vmax=2.8)#, interpolation='nearest', cmap=blue_red1)
    plt.ylabel(secondkey)
    plt.xlabel(firstkey)
    #
    # Plot ticks if so asked
    #
    if firstticks:
        plt.xticks(range(len(xvals)),xvals,rotation='vertical')
    if secondticks:
        plt.yticks(range(len(yvals)),yvals)
    if colorbar:
        cbar=plt.colorbar()
        cbar.set_label(zlabel)
    # Add the title
    plt.title(title)
    import numpy
    #plt.xticks(numpy.arange(0,121,10))
    #plt.yticks(numpy.arange(0,165,10))

    plt.show()
    return

import LM_Fitter

from numpy import *
from numpy.linalg import * 
inverse=inv
Float=float
class pKaTool_fitter:

    def __init__(self,system_spec,exp_data,CCPS,normalize=True,max_steps=1000,conv_crit=0.000005):
        #
        # Initialize
        #
        self.CCPS=CCPS
        self.normalize=normalize 
        self.exp_pHs=[]
        self.profiles={}
        self.exp_data=exp_data
        for pH,pop in exp_data:
            self.exp_pHs.append(pH)
        #
        # Reformat the variables
        #
        self.groups=system_spec.keys()
        self.groups.sort()
        self.vars=[]
        # intpkas
        for group in self.groups:
            self.vars.append(system_spec[group]['intpka'])
        # Matrix
        for group1 in self.groups:
            for group2 in self.groups:
                if system_spec[group1]['matrix'].has_key(group2):
                    self.vars.append(system_spec[group1]['matrix'][group2])
        self.start_vars=self.vars[:]
        #
        # Set up the pKaTool stuff
        #
        self.pHstart=0.0
        self.pHend=20.0
        self.pHstep=1.0
        self.numgroups=len(self.groups)
        self.CCPS=CCPS
        import pKa_calc
        self.PK=pKa_calc.Boltzmann()
        #
        # Set damper
        #
        self.LM_damper = 0.1
        #
        # Start fitting
        #
        old_diff=0.0000001
        #print 'Step    Diff   LM_damper'
        now_diff=self.activity_diff()
        self.start_score=now_diff
        #print '%5d  %6.4f  %6.4f' %(0, now_diff, self.LM_damper)
        for x in range(1,max_steps):
            self.fit_LM_activity()
            now_diff=self.activity_diff()
            #
            # Check convergence
            #
            #print '%5d  %6.4f  %6.4f' %(x, now_diff, self.LM_damper)
            if abs(now_diff-old_diff)<conv_crit:
                #print 'Converged',now_diff
                break
            else:
                old_diff=now_diff
            now_diff=self.activity_diff()
        self.diff=now_diff
        return 

    #
    # ------
    #

    def fit_LM_activity(self):
        """Do Levenberg-Marquardt fitting"""
        J,E =self.get_jacobian_activity()
        JT = transpose(J)
        JTE = dot(JT,E)
        JTJ = dot(JT,J)
        JTJd = JTJ + self.LM_damper*identity(shape(JTJ)[0])
        invJTJd = inv(JTJd)
        q = -dot(JTE,invJTJd)
        #out1 ='bv '
        #out2 ='av '
        for var in range(len(self.vars)):
            #out1 += '%4.6f '%self.vars[var]
            self.vars[var]=max(0.0,self.vars[var]+q[var]) # We don't allow any parameter to drop below 0.0
            #out2 += '%4.6f '%self.vars[var]
        return



    def get_jacobian_activity(self):
        """Get the Jacobian matrix and errors of the data points"""
        #
        # Get the number of data points
        #
        no_data_points = len(self.exp_data)
        errors = resize(array(0,float),[no_data_points])        
        jacobian = resize(array(0,float),[no_data_points,len(self.vars)])
        #
        # Precalculate the variation of all parameters
        #
        now=self.get_act_prof()
        variations=[]
        step = 1e-8
        for var in range(len(self.vars)):
            self.vars[var]=self.vars[var]+step
            variations.append(self.get_act_prof())
            self.vars[var]=self.vars[var]-step
        #
        # construct jacobian
        #
        data_id=0
        #
        # activity data
        #
        for ph,act in self.exp_data:
            x=float(ph)
            y=float(act)
            errors[data_id] = y-now[ph]
            #
            # Find the derivative at this ph (x) for this data point
            #
            diff=resize(array(0,float),[len(self.vars)])
            count=0
            for variation in variations:
                diff[count]=(now[ph]-variation[ph])/step
                count=count+1
            jacobian[data_id]=diff
            data_id=data_id+1
        return jacobian,errors
        
    #
    # -------
    #
        
    def activity_diff(self):
        """Get the sum of differences between exp data and fitted data"""
        act_prof_and_tc = self.get_act_prof()
        diff = 0.0
        for ph,act in self.exp_data:
            diff = diff + abs(act_prof_and_tc[ph]-act)
        return diff
        
    #
    # -------
    #
    
    def get_act_prof(self):
        """Get the pH-activity profile and titration curves"""
        #
        # titration data
        #
        self.setup_system(self.vars)
        # Calculate the CCPSs
        pKa_values,prot_states=self.PK._calc_pKas(mcsteps=0,phstep=self.pHstep,phstart=self.pHstart,phend=self.pHend,exp_pHs=self.exp_pHs,verbose=1)
        #
        # Primary activity data
        #
        act_prof1={}
        states=0
        for pH in self.exp_pHs:
            act=0.0
            for state in self.PK.all_states[pH].keys():
                if self.PK.all_states[pH][state]['def'] in self.CCPS:
                    act=act+self.PK.all_states[pH][state]['pop']
                    states=states+1
            act_prof1[pH]=act
        if states>0:
            max_act=max(act_prof1.values())
            if max_act==0.0:
                fact=1.0
            else:
                fact=1.0/max_act
            for ph in act_prof1.keys():
                act_prof1[ph] = fact*act_prof1[ph]
        else:
            act_prof1={}
        return act_prof1
        
    #
    # -----
    #
        
    def setup_system(self,variables):
        """Setup the system as per the system_spec dictionary"""
        # 
        # Get the intrinsic pKas
        #
        count=0
        self.PK.intrinsic_pKa={}
        self.PK.matrix={}
        for group in self.groups:
            self.PK.intrinsic_pKa[group]=variables[count]
            count=count+1
        #
        # Matrix
        #
        for group1 in self.groups:
            self.PK.matrix[group1]={}
        for group1 in self.groups:
            for group2 in self.groups:
                if group1<group2:
                    intene=self.PK.acid_base(group1)*self.PK.acid_base(group2)*variables[count]
                    self.PK.matrix[group1][group2]=[intene,0.0,0.0,0.0]
                    self.PK.matrix[group2][group1]=[intene,0.0,0.0,0.0]
                    count=count+1
                elif group1==group2:
                    self.PK.matrix[group1][group2]=[0.0,0.0,0.0,0.0]
        self.PK.prepare_matrix()
        #
        self.PK.groups=self.groups
        return


#
# --------------
#

class profile_fitter:

    def __init__(self,options,args):
        """Instantiate a class that fits an experimental pH-activity profile to a combination of CCPSes"""
        self.options=options
        #
        # read the file with experimental data
        #
        fd=open(options.expdata)
        lines=fd.readlines()
        fd.close()
        self.tempexp_data=[]
        vals=[]
        start_values=eval(self.options.svr)
        for line in lines:
            if line.strip()[0]=='#' or line.split()[0]=='pH':
                continue
            sp=line.split()
            self.tempexp_data.append([float(sp[0]),float(sp[1])])
            vals.append(float(sp[1]))
        maxval=max(vals)
        self.exp_data=[]
        for pH,act in self.tempexp_data:
            self.exp_data.append([pH,act/maxval])
        #
        # What should we do
        #
        if self.options.analyze:
            self.analyze(1)
        elif self.options.pca:
            self.PCA()
        elif self.options.PCA_dependent:
            self.do_fitting(start_values,1)
            self.analyze(1)
            self.PCA()
        elif self.options.PCA_independent:
            self.PCAindependent(start_values)
            
        return
    
    #
    # -----
    #
            
    def do_fitting(self,start_values,count):
        #
        # Set the group definition
        #
        import string, random
        groups=[]
        for group in range(self.options.ngroups):
            groups.append('%s:%s' %(string.zfill(group,4),'ASP'))
        #
        CCPS_def=eval(self.options.CCPS) 
        #
        print 'Doing %5d fits with maxstep: %4d with groups: %s, and CCPS definition: %s' %(self.options.nfits,self.options.max_steps,str(groups),str(CCPS_def))
        print 'The range of starting values: %s' %(str(start_values))
        solutions=[]
        for fitno in range(self.options.nfits):
            self.set_random_state(groups,start_values)
            score,variables,start_vals,start_score,profile=self.fit_system(CCPS_def)
            print 'Fit# %4d, score: %6.3f' %(fitno,score)
            solutions.append([score,variables,profile,CCPS_def,groups,start_vals,start_score])
        #
        # Save the solutions as pickle
        #
        fd=open(str(count)+self.options.outfile+'.pickle','w')
        import pickle
        pickle.dump(solutions,fd)
        fd.close()
        #
        # Save the solutions as csv
        #
        import csv
        features=[]
        for parm in range(len(solutions[0][1])):
            features.append('parm%d' %parm)
        f=open(str(count)+self.options.outfile+'.csv','w')
        cw=csv.writer(f)
        cw.writerow(features)
        for score,variables,profile,CCPS_def,groups,start_vals,start_score in solutions:
            cw.writerow(variables)
            cw.writerow(start_vals)
        f.close()
        return
        
    #
    # -----
    #
    
    def align_parms(self,solutions):
        """Sort the solutions so parameters are shifted around to give optimal overlap
        This only works well for 3-group systems (and perhaps not even for them)"""
        solutions.sort()
        ref_sol=solutions[0][1]
        aligned_sols=[solutions[0]]
        for score,variables,profile,CCPS_def,groups,start_values,start_scores in solutions[1:]:
            best_vars=variables[:]
            diff=self.get_similarity(variables,ref_sol)
            for permutation in range(len(groups)-1):
                variables=self.permute(variables,len(groups))
                if self.get_similarity(variables,ref_sol)<diff:
                    diff=self.get_similarity(variables,ref_sol)
                    best_vars=variables[:]
            aligned_sols.append([score,best_vars,profile,CCPS_def,groups,start_values,start_scores])
        return aligned_sols
    
    #
    # ------
    #
        
    def permute(self,variables,numgroups):
        """Construct a permutation of variables that is consistent with the geometry of the system"""
        groups=[]
        intpkas={}
        matrix={}
        count=0
        for group in range(numgroups):
            groups.append(group)
            intpkas[group]=variables[count]
            count=count+1
        # Matrix
        for group1 in groups:
            matrix[group1]={}
        for group1 in groups:
            for group2 in groups:
                if group1<group2:
                    intene=variables[count]
                    count=count+1
                    matrix[group1][group2]=intene
                    matrix[group2][group1]=intene
        #
        # permute so that group1 becomes last. subtract 1 from all other group numbers
        #
        variables=[]
        groups=groups[1:]+[groups[0]]
        for group in groups:
            variables.append(intpkas[group])
        # Matrix
        for pos1 in range(len(groups)):
            group1=groups[pos1]
            for pos2 in range(len(groups)):
                group2=groups[pos2]
                if pos1<pos2:
                    variables.append(matrix[group1][group2])
        return variables
            
    #
    # ------
    #
        
    def get_similarity(self,solution1,solution2):
        """Get the similarity of two solutions"""
        import math, numpy
        s1=numpy.array(solution1)
        s2=numpy.array(solution2)
        I=numpy.inner(s1,s2)
        costerm=I/(numpy.linalg.norm(s1)*numpy.linalg.norm(s2))
        #
        # Maybe better to get the length of the difference vector
        #
        return numpy.linalg.norm(s1-s2)
    
    #
    # -------
    #
        
    def analyze(self,ccountt):
        #
        # Load the pickle file and do the analysis
        #
        fd=open(self.options.infile+'.pickle')
        import pickle
        solutions=pickle.load(fd)
        fd.close()
        #
        # Sort the parameters - make sure that redundant solutions appear the same
        #
        solutions=self.align_parms(solutions)
        #
        # Print the solutions
        #
        solutions.sort()
        #
        # Keep only solutions that are less than 10% worse than the best solution
        #
        best_score=solutions[0][0]
        ok_sols=[]
        count=1
        for sol in solutions:
            if abs((sol[0]-best_score)/best_score)<=self.options.cluster_cutoff:
                print count,sol[0],sol[1]
                count=count+1
                ok_sols.append(sol)
        #
        # Plot the ranges of the variables
        #
        import pylab
        if self.options.var_ranges:
            xs=[]
            ys=[]
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:
                count=1
                for var in variables:
                    xs.append(count)
                    ys.append(var)
                    count=count+1
            import pylab
            pylab.plot(xs,ys,'ro')
            pylab.xlabel('Variable number')
            pylab.ylabel('Value')
            pylab.show()
        #
        # Plot all the fits
        #
        if self.options.plotfits:
            import pylab
            count=0
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:
                pHs=sorted(profile.keys())
                xs=[]
                ys=[]
                for pH in pHs:
                    xs.append(pH)
                    ys.append(profile[pH])
                if count==0:
                    pylab.plot(xs,ys,'r-',label='Fitted solutions')
                else:
                    pylab.plot(xs,ys,'r-')
                count=count+1
            #
            # Plot the exp data
            #
            xs=[]
            ys=[]
            for pH,act in self.exp_data:
                xs.append(pH)
                ys.append(act)
            pylab.plot(xs,ys,'bo',label='Experimental data')
            pylab.legend()
            pylab.xlabel('pH')
            pylab.ylabel('Normalized population')
            pylab.show()

        #
        # Generate files (.csv and .pickle) to store the analyzed data
        #
        if self.options.sol_only or self.options.PCA_dependent or self.options.PCA_independent:
            import csv
            features=[]
            features2=[]
            maxparm=[]
            minparm=[]
            minandmax=[]
            for parm in range(len(ok_sols[0][1])):
                features.append('parm%d' %parm)
            filename1=str(ccountt)+'anal_sols_only_score'+'.csv'
            filename2=str(ccountt)+'anal_sols_only'+'.csv'
            f=open(filename1,'w')
            cw=csv.writer(f)
            cw.writerow(features+['score'])
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:  
                cw.writerow(variables+[score])
            for parm in range(len(ok_sols[0][1])):
                features2.append('parm%d range' %parm)
            maxparm,minparm,minandmax=self.maxmindetermine(ok_sols)
            cw.writerow(features2)
            cw.writerow(minparm)
            cw.writerow(maxparm)
            f.close()
            f=open(filename2,'w')
            cw=csv.writer(f)
            cw.writerow(features)
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:  
                cw.writerow(variables)
            f.close()
            filename3=str(ccountt)+'anal_sols_only'+'.pickle'
            fd=open(filename3,'w')
            import pickle
            pickle.dump(ok_sols,fd)
            fd.close()
            if self.options.PCA_independent:
                return minandmax,ok_sols
        if self.options.both:
            import csv
            features=[]
            for parm in range(len(ok_sols[0][1])):
                features.append('parm%d' %parm)
            filename1=str(ccountt)+'anal_sols_score'+'.csv'
            filename2=str(ccountt)+'anal_sols'+'.csv'
            f=open(filename1,'w')
            cw=csv.writer(f)
            cw.writerow(features+['score'])
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:  
                cw.writerow(variables+[score])
                cw.writerow(start_vals+[start_score])
            maxparm=[]
            minparm=[]
            minandmax=[]
            maxparm,minparm,minandmax=self.maxmindetermine(ok_sols)
            cw.writerow(features2)
            cw.writerow(minparm)
            cw.writerow(maxparm)
            f.close()
            f=open(filename2,'w')
            cw=csv.writer(f)
            cw.writerow(features)
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in ok_sols:  
                cw.writerow(variables)
                cw.writerow(start_vals)
            f.close()
            filename3 = str(ccountt)+'anal_sols'+'.pickle'
            fd=open(filename3,'w')
            import pickle
            pickle.dump(ok_sols,fd)
            fd.close()
        #
        # Extract solutions according to the desired score range 
        #
        #if self.options.extract:
        #    self.extract(ok_sols)        
        return
        
    #
    # -----
    #
    
    def set_random_state(self,groups,start_values):
        #
        # Construct random starting values for the system
        #
        import pKa_calc
        import random
        X=pKa_calc.Boltzmann()
        self.system_spec={}
        #if self.options.tran:
        #    allstart_vals=start_values
        #else:
        #    allstart_vals=eval(self.options.svr)
        count=0
        for group in groups:
            self.system_spec[group]={'intpka':random.uniform(start_values[count][0],start_values[count][1]),'matrix':{}}
            count=count+1
        for group1 in groups:
            for group2 in groups:
                if group1<group2:
                    self.system_spec[group1]['matrix'][group2]=random.uniform(start_values[count][0],start_values[count][1])
                    count=count+1
        return

    #
    # -----
    #
        
    def fit_system(self,CCPS_def):
        #
        # Fit the system
        #
        self.FIT=pKaTool_fitter(self.system_spec,self.exp_data,CCPS_def,max_steps=self.options.max_steps,conv_crit=self.options.conv_crit)
        prof=self.FIT.get_act_prof()
        return self.FIT.diff,self.FIT.vars,self.FIT.start_vars,self.FIT.start_score,prof
    
    #
    # -----
    #
        
    def plot_current_fit(self):
        """Plot the current fit"""
        import pylab
        xs=sorted(prof.keys())
        ys=[]
        for x in xs:
            ys.append(prof[x])
        pylab.plot(xs,ys,'r-',label='fitted')
        #
        xs=[]
        ys=[]
        for x,y in self.exp_data:
            xs.append(x)
            ys.append(y)
        pylab.plot(xs,ys,'bo',label='experimental')
        pylab.legend()
        pylab.show()
        print
        print 'Done.'
        print 'Fitted variables',self.FIT.variables
        return
        
    #
    # -------
    #
    
    
    def PCA(self):
        """Reduce the dimensionality of the space, and produce a heatmap showing where the good fits cluster"""
        import csv
        import matplotlib  
        from matplotlib.font_manager import FontProperties
        import matplotlib.pyplot as plt 
        from mpl_toolkits.mplot3d import Axes3D
        
        fd=open(self.options.PCAfile+'.pickle')
        import pickle
        solutions=pickle.load(fd)
        fd.close()
        
        orgdata=[]
        if self.options.sol_only:
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in solutions:
                orgdata.append(score)
        else:
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in solutions:
                orgdata.append(score)
                orgdata.append(start_score)

            #
            # Add this for the colouring
            #
 
            #x.append(variables[0])
            #y.append(variables[1])
            #z.append(variables[2])
        #
        #if False:
        #    f=plt.figure()
        #    ax = Axes3D(f)
        #    ax.scatter(x,y,zs=z,marker='o',lw=2,alpha=0.5,c='b',s=30)
        #    ax.set_xlabel('pKa1')
        #    ax.set_ylabel('pKa2')
        #    ax.set_zlabel('pKa3')
        #    ax.legend()
        #    f.subplots_adjust(hspace=1,wspace=1) 
        from PEATDB.Ekin.Fitting import Fitting
        from PEATSA import Core
        m = Core.Matrix.matrixFromCSVFile(self.options.PCAfile+'.csv')
        import PEATDB.plugins.PCA as PCA
        P = PCA.PCAPlugin()
        evals, evecs, transformed_data = P.doPCA(m)
        print 'Eigenvalues'
        print evals
        print '-------------------'
        print 'Eigenvectors'
        for v in evecs:
            print v
        print
        #P.plotResults(evals, evecs, b, m)
        #
        # Plot the data in Ev1, Ev2 space
        #
        matrix={}
        xs=[]
        ys=[]
        data=[]
        count=0
        for evs in transformed_data:
            xs.append(evs[0])
            ys.append(evs[1])
            data.append([evs[0],evs[1],orgdata[count]])
            count=count+1
        minx=min(xs)
        maxx=max(xs)
        stepx=(maxx-minx)/100.0
        miny=min(ys)
        maxy=max(ys)
        stepy=(maxy-miny)/100.0
        import numpy
        for x in range(101):
            matrix[x]={}
            for y in range(101):
                matrix[x][y]=[]
        #
        # Populate the matrix
        #
        import numpy
        relation={}
        for x in range(101):
            relation[x]={}
            for y in range(101):
                relation[x][y]=[]
        count=0
        for x,y,z in data:
            xbin=int((x-minx)/stepx)
            ybin=int((y-miny)/stepy)
            matrix[xbin][ybin].append(z)
            relation[xbin][ybin].append(count)
            count=count+1
        newmatrix={}
        for x in matrix.keys():
            newmatrix[x]={}
            for y in matrix[x].keys():
                if len(matrix[x][y])>0:
                    newmatrix[x][y]=sum(matrix[x][y])/float(len(matrix[x][y]))
                else:
                    newmatrix[x][y]=nan
        if self.options.tran:
            self.translate(relation,solutions)
            return
        heatmap(newmatrix,title='pH-activity profile parameter space',firstkey='Ev1',secondkey='Ev2',zlabel='Abs(error)',vmin=self.options.vmin,vmax=self.options.vmax)
        return

    
    #
    # -------
    #
    
    def maxmindetermine(self,solutions):
        #
        #
        #
        temp=[]
        maxparm=[]
        minparm=[]
        minandmax=[]
        for i in range(len(solutions[0][1])):
            for variables in solutions:
                temp.append(variables[1][i])
            maxparm.append(max(temp))
            minparm.append(min(temp))
            minandmax.append([min(temp),max(temp)])
            temp=[]
        return maxparm,minparm,minandmax
    
    #
    # -------
    #    
    def translate(self,targetm,solutions):
        #
        # find the dots of interest in the targetm and translate it back into its original solution values from the source.
        # In PCA_translation_score.csv, the range of each parameter is given at the bottom.
        # A new round of fitting, whose start_val is based on the parameter ranges acquired here, is intrinsic in this function, i.e. you do not need to type in the ranges manually for re-fitting.
        #
        coordinate=eval(self.options.trange)
        translate=[]
        ran=[]
        ran.append(min(coordinate[0][0],coordinate[1][0]))
        ran.append(max(coordinate[0][0],coordinate[1][0]))
        ran.append(min(coordinate[0][1],coordinate[1][1]))
        ran.append(max(coordinate[0][1],coordinate[1][1]))
        print '---------------------------------------'
        print 'The range of your choice is:'
        print [ran[0],ran[2]],[ran[1],ran[2]]
        print [ran[0],ran[3]],[ran[1],ran[3]]
        import csv
        features=[]
        features2=[]
        maxparm=[]
        minparm=[]
        minandmax=[]
        temp=[]
        for parm in range(len(solutions[0][1])):
            features.append('parm%d' %parm)
        f=open('PCA_translation.csv','w')
        cw=csv.writer(f)
        #cw.writerow([ran[0],ran[2]]+[ran[1],ran[2]])
        #cw.writerow([ran[0],ran[3]]+[ran[1],ran[3]])
        cw.writerow(features)
        for i in range (ran[0],ran[1]+1):
            for j in range (ran[2],ran[3]+1): 
                if len(targetm[i][j])>0:
                    for k in range (len(targetm[i][j])):
                        num=targetm[i][j][k]
                        cw.writerow(solutions[num][1])
                        translate.append(solutions[num])
        f.close()
        f=open('PCA_translation_score.csv','w')
        cw=csv.writer(f)
        #cw.writerow([ran[0],ran[2]]+[ran[1],ran[2]])
        #cw.writerow([ran[0],ran[3]]+[ran[1],ran[3]])
        cw.writerow(features+['score'])
        for i in range (ran[0],ran[1]+1):
            for j in range (ran[2],ran[3]+1):
                if len(targetm[i][j])>0:
                    for k in range (len(targetm[i][j])):
                        num=targetm[i][j][k]
                        cw.writerow(solutions[num][1]+[solutions[num][0]])
        for parm in range(len(solutions[0][1])):
            features2.append('parm%d range' %parm)
        maxparm,minparm,minandmax=self.maxmindetermine(translate)
        cw.writerow(features2)
        cw.writerow(minparm)
        cw.writerow(maxparm)
        f.close()
        fd=open('PCA_translation.pickle','w')
        import pickle
        pickle.dump(translate,fd)
        fd.close()
        if self.options.PCA_dependent:
            self.do_fitting(minandmax,1)
            self.analyze(1)
            self.PCA()
        elif self.options.PCA_independent:
            self.options.PCAindependent(minandmax)
        return
        

    #
    # -------
    #
    
    def extract(self,solutions):
        #
        # extract solutions (without starting values) in terms of score range
        #
        import csv
        scorange=eval(self.options.scr)
        extraction=[]
        features=[]
        filename="best_sol"+self.options.scr
        for parm in range(len(solutions[0][1])):
            features.append('parm%d' %parm)
        f=open(filename+'.csv','w')
        cw=csv.writer(f)
        if self.options.addscore:
            cw.writerow(features+['score'])
        else:
            cw.writerow(features)
        for score,variables,profile,CCPS_def,groups,start_vals,start_score in solutions:
            if score<=scorange[1] and score>=scorange[0]:
                if self.options.addscore:
                    cw.writerow(variables+[score])
                else:
                    cw.writerow(variables)
                extraction.append([score,variables,profile,CCPS_def,groups,start_vals,start_score])
        fd=open(filename+'.pickle','w')
        import pickle
        pickle.dump(extraction,fd)
        fd.close()
        return

    #
    # -------
    #    

    def PCAindependent(self, start_values):
        #
        # Do the PCA_independent fitting cycle. The cycle ends when the average score of the new fitted data does not improve the amount indicated by the cutoff. 
        #
        count=1
        determinant=1
        minandmax=[]
        solutions=[]
        old_score_ave=100.0
        scoresum=0.0
        item=0
        while determinant!=0:
            self.do_fitting(start_values,count)
            start_values,solutions=self.analyze(count)
            for score,variables,profile,CCPS_def,groups,start_vals,start_score in solutions:
                scoresum=scoresum+score
                item=item+1
            new_score_ave=scoresum/item
            if (old_score_ave-new_score_ave)/old_score_ave>=0 and (old_score_ave-new_score_ave)/old_score_ave>=self.options.PCA_ind_cutoff:
                determinant=1
                old_score_ave=new_score_ave
                count=count+1
                item=0
            else:
                determinant=0
                return
            

    #
    # -------
    #


def main():
    print
    print 'Fit enzymatic pH-activity profiles to pKaTool CCPS populations'
    print 'Jens Erik Nielsen, 2010'
    print
    import sys, os
    from optparse import OptionParser
    parser = OptionParser(usage='%prog [options] <file>',version='%prog 1.0')
    parser.add_option('-e',"--expdata",type='string',dest='expdata',action='store',
                      help='File with experimental pH-activity profile. Space separation. Default: %default',default='pH_act.txt')
    parser.add_option('-o',"--outfile",type='string',dest='outfile',action='store',
                      help='output file for solutions (type the filename WITHOUT the extensions). Default: %default',default='solutions')
    parser.add_option('-i',"--infile",type='string',dest='infile',action='store',
                      help='input file for analysis (type the filename WITHOUT the extensions). Default: %default',default='1solutions')
    parser.add_option('-n','--nfits',dest='nfits',action='store',type='int',
                        help='Number of random starting positions to evaluate. Default: %default',default=10)
    parser.add_option('-m','--maxsteps',dest='max_steps',action='store',type='int',
                        help='Max number of LM steps in any one fitting run. Default: %default',default=100)
    parser.add_option('-g','--ngroups',dest='ngroups',action='store',type='int',
                        help='Number of titratable groups. Default: %default',default=3)
    parser.add_option('-c','--convcrit',dest='conv_crit',type='float',action='store',
                        help='LM gradient convergence criterion. Default: %default',default=0.000005)
    parser.add_option('-d','--cluster',dest='cluster_cutoff',type='float',action='store',
                        help='Fractional deviation of solution scores from best score that is accepted when filtering solutions. Default: %default',default=0.1)
    parser.add_option('-a','--analyze',dest='analyze',action='store_true',default=False,
                        help='Do only analysis (i.e. skip fitting and use old output file) and generate new files storing the analyzed data. Default: %default')
    parser.add_option('-r','--var_ranges',dest='var_ranges',action='store_true',default=False,
                        help='Plot aligned variables ranges. Default: %default')
    parser.add_option('-f','--fits',dest='plotfits',action='store_true',default=False,
                        help='Plot experimental data and fits (only available after performing analyze first). Default: %default')
    parser.add_option('-p','--pca',dest='pca',action='store_true',default=False,
                        help='Do principal component analysis. Default: %default')
    parser.add_option('--vmax',dest='vmax',type='float',action='store',
                        help='Max value for colorbar in pca heatmap. Default: %default',default=10.0)
    parser.add_option('--vmin',dest='vmin',type='float',action='store',
                        help='Min value for colorbar in pca heatmap. Default: %default',default=0.0)
    parser.add_option('-s',"--CCPS",type='string',dest='CCPS',action='store',
                        help='Define the CCPS for pH-activity profile. Default: %default',default='[[1,0,0],[1,0,1]]')
    parser.add_option('--PCAfile',type='string',dest='PCAfile',action='store',default='1anal_sols_only',
                        help='Perform PCA on old files (type the filename WITHOUT the extensions). Default: %default')
    #parser.add_option('--extract',dest='extract',action='store_true',default=False,
    #                    help='Extract solutions with scores of desired range. Default: %default')
    #parser.add_option("--scr",type='string',dest='scr',action='store',
    #                    help='Define the score range for solution extraction. Default: %default',default='[0.0,1.0]')
    parser.add_option('--both',dest='both',action='store_true',default=False,
                        help='Create solution+start_values file (including three files) after analysis. Default: %default')
    parser.add_option('--sol_only',dest='sol_only',action='store_true',default=False,
                        help='Create solutions-only files (including three files) after analysis or perform PCA with only solutions. Default: %default')
    parser.add_option("--svr",type='string',dest='svr',action='store',
                        help='Define the range of randomly selected starting values in the format of [pKa0,pKa1,pKa2,intene01,intene02,intene12]. Default: %default',default='[[0,8],[0,8],[0,8],[0,10],[0,10],[0,10]]')
    parser.add_option('--tran',dest='tran',action='store_true',default=False,
                        help='Translate the dot on PCA map back to its original solution values, and automatically start a new round of fitting based on the ranges of the values. Default: %default')
    parser.add_option('--trange',type='string',dest='trange',action='store',
                        help='Give the diagonal vertices coordinates (int format) of the rectangular area of interest on PCA map for translation. Default: %default',default='[[0,0],[100,100]]')
    parser.add_option('--PCA_dependent',dest='PCA_dependent',action='store_true',default=False,
                        help='Allow you to do the PCA_dependent fitting of the pH-activity profile. Default: %default')
    parser.add_option('--PCA_independent',dest='PCA_independent',action='store_true',default=False,
                        help='Allow you to do the PCA_independent fitting of the pH-activity profile. Default: %default')
    parser.add_option('--PCA_ind_cutoff',dest='PCA_ind_cutoff',action='store',type='float',
                        help='Cutoff determining when the PCA_independent fitting cycle should end. Default: %default',default=0.05)
      
    (options, args) = parser.parse_args()
    #
    # Call main
    #
    X=profile_fitter(options,args)
    return


if __name__=="__main__":
    main()


