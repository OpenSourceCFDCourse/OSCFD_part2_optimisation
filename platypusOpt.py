from platypus import NSGAII, Problem, Real, Integer, ProcessPoolEvaluator
import openturns.coupling_tools as ct
import numpy as np
import os
import csv


debug = False
CASECOUNT=1

def checkCommand(command):
    # exit function if we do not want to print debug info
    if not debug:
        return

    if not command.returncode:
        print('command {} succesfull'.format(command.args))
    else:
        print('command {} failed'.format(command.args))


def runCase(X):

    global CASECOUNT
    print('############## CASE {} ##############'.format(CASECOUNT))
    #We convert all to integer here as the resolution is already high would be ok if GEO was i meters.
    x1 = int(X[0])
    y1 = int(X[1])
    
    x2 = int(X[2])
    y2 = int(X[3])
    
    weight = int(X[4])
    
    caseName = "case{}_{}_{}_{}_{}_{}".format(CASECOUNT,x1,y1,x2,y2,weight)
    
    print("Case = {}".format(caseName))
    
    cp = ct.execute('cp -r template '+caseName, capture_output=True, shell=True)
    checkCommand(cp)
    
    cp = ct.execute('cd '+caseName, capture_output=True, shell=True)
    checkCommand(cp)
    
    os.chdir(caseName)
    
    ct.replace('createGeo.py.tmp','createGeo.py',tokens=["{x1}","{y1}","{x2}","{y2}","{weight}"],values=[x1,y1,x2,y2,weight])
    ct.replace('system/meshDict.tmp','system/meshDict',tokens=["{x1}","{y1}","{x2}","{y2}"],values=[x1,y1,x2,y2])
    
    cp = ct.execute('freecadcmd -c createGeo.py', capture_output=True, shell=True)
    checkCommand(cp)
    
    cp = ct.execute('sleep 1', capture_output=True, shell=True)
    checkCommand(cp)
    
    cp = ct.execute('cd STL && ./renameSTL.sh', capture_output=True, shell=True)
    checkCommand(cp)
    
    cp = ct.execute('surfaceToFMS STL/joined.stl', capture_output=True, shell=True)
    checkCommand(cp)
    
    cp = ct.execute('surfaceFeatureEdges -angle 80 STL/joined.fms STL/joined2.fms', capture_output=True, shell=True)
    checkCommand(cp)

    cp = ct.execute('export OMP_NUM_THREADS=1 && cartesian2DMesh', capture_output=True, shell=True)
    checkCommand(cp)

    cp = ct.execute('transformPoints -scale "(0.001 0.001 0.001)"', capture_output=True, shell=True)
    checkCommand(cp)

    cp = ct.execute('cp -r 0.orig 0', capture_output=True, shell=True)
    checkCommand(cp)
    
    try:
        #If simplefoam Blows up, geo is bad anyway so set to high numbers to penalize 
        cp = ct.execute('potentialFoam > log.potentialFoam', capture_output=True, shell=True)
        checkCommand(cp)
        
        print('Running simpleFoam, please wait')
        cp = ct.execute('simpleFoam > log.simpleFoam', capture_output=True, shell=True)
        checkCommand(cp)
    except:
        print('Failed to run case will discard')
        uniU = 1000
        avgP = 1000
    
    else:
        #Minimize problem so multiply with -1
        uniU = np.mean(np.loadtxt('./postProcessing/maxU/0/surfaceFieldValue.dat',comments='#',usecols=(1,),unpack=True)[-10:])
        avgP = np.mean(np.loadtxt('./postProcessing/pInlet/0/surfaceFieldValue.dat',comments='#',usecols=(1,),unpack=True)[-10:])
    
    
    finally:
        print("Uniformity index = {}%".format(uniU))
        print("Average p = {}Pa".format(avgP))
        os.chdir('../')
        
        with open(csvfi,'a') as csvfile:
                csvf = csv.writer(csvfile, delimiter=';', lineterminator='\n')
                csvf.writerow([caseName, x1, y1, x2, y2, weight, uniU, avgP])
    
    CASECOUNT+=1
    return [uniU,avgP]
    
# House keeping folder and files
csvfi = 'outputdata.csv'

if os.path.isfile(csvfi):
    pass
else:
    with open(csvfi,'w') as csvfile:
        csvf = csv.writer(csvfile, delimiter=';', lineterminator='\n')
        csvf.writerow(['caseName', 'x1', 'y1', 'x2', 'y2','weight', 'U uniformity Index (%)', 'Average Pressure (Pa)'])


dim = 5 #Amount of variables
dimObj = 2 #Amount of objectives

x1Lower = 250
x1Upper = 290

y1Lower = 10
y1Upper = 90

x2Lower = 310
x2Upper = 390

y2Lower = -50
y2Upper = 0

weightLower = 1
weightUpper = 100


# Instantiate Optimization Problem 
problem = Problem(dim, dimObj)
problem.directions[0] = Problem.MAXIMIZE #Uniformity
problem.directions[1] = Problem.MINIMIZE #Pressure
problem.types[0] = Integer(x1Lower, x1Upper)
problem.types[1] = Integer(y1Lower, y1Upper)
problem.types[2] = Integer(x2Lower, x2Upper)
problem.types[3] = Integer(y2Lower, y2Upper)
problem.types[4] = Integer(weightLower, weightUpper)

problem.function = runCase

with ProcessPoolEvaluator(2) as evaluator:
    algorithm = NSGAII(problem, population_size=5, evaluator=evaluator)
    algorithm.run(40)
    
for solution in algorithm.result:
    print(solution.objectives)


#algorithm.run(40)