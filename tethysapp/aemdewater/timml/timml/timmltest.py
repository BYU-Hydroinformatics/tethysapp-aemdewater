from timml import *
import numpy
ml = Model(k = [2,6,4], zb = [140,80,0], zt = [165,120,60], c = [2000,20000], n = [0.3,0.25,0.3], nll = [0.2,0.25])
rf = Constant(ml,20000,20000,175,[0])
p=CircAreaSink(ml,10000,10000,15000,0.0002,[0])
w1=Well(ml,10000,8000,3000,.3,[1],'well 1')
w2=Well(ml,12000,8000,5000,.3,[2],'well 2')
w3=Well(ml,10000,4600,5000,.3,[1,2],'maq well')
#
HeadLineSink(ml, 9510,  19466, 12620, 17376, 170,[0])
HeadLineSink(ml, 12620, 17376, 12753, 14976, 168,[0])
HeadLineSink(ml, 12753, 14976, 13020, 12176, 166,[0])
HeadLineSink(ml, 13020, 12176, 15066, 9466,  164,[0])
HeadLineSink(ml, 15066, 9466,  16443, 7910,  162,[0])
HeadLineSink(ml, 16443, 7910,  17510, 5286,  160,[0])
HeadLineSink(ml, 17510, 5286,  17600, 976,   158,[0])
#
HeadLineSink(ml, 356,   6976,  4043,  7153, 174,[0])
HeadLineSink(ml, 4043,  7153,  6176,  8400, 171,[0])
HeadLineSink(ml, 6176,  8400,  9286,  9820, 168,[0])
HeadLineSink(ml, 9286,  9820,  12266, 9686, 166,[0])
HeadLineSink(ml, 12266, 9686,  15066, 9466, 164,[0])
#
HeadLineSink(ml, 1376,  1910,  4176,  2043, 170,[0])
HeadLineSink(ml, 4176,  2043,  6800,  1553, 166,[0])
HeadLineSink(ml, 6800,  1553,  9953,  2086, 162,[0])
HeadLineSink(ml, 9953,  2086,  14043, 2043, 160,[0])
HeadLineSink(ml, 14043, 2043,  17600, 976 , 158,[0])
#

def trace_example1():
    from timml import mlutil
    from timml import mltrace
    an = numpy.arange(0,2*numpy.pi,numpy.pi/5.0)
    mlutil.timtracelines(ml,w1.xw+numpy.cos(an),w1.yw+numpy.sin(an),100*numpy.ones(len(an)),-100,Nmax=500)
    mlutil.timtracelines(ml,w2.xw+numpy.cos(an),w2.yw+numpy.sin(an),30*numpy.ones(len(an)),-100,Nmax=500)
    mlutil.timtracelines(ml,w3.xw+numpy.cos(an),w3.yw+numpy.sin(an),100*numpy.ones(len(an)),-100,tmax=200*365,Nmax=200)
    mltrace.traceline(ml,[12933],[5990],[160],1,tmax=1e30,maxsteps=100000,tstart=0.0,window=[-1e30,-1e30,1e30,1e30],\
              labfrac = 2.0, Hfrac = 2.0, verbose = True)

try:
    # equivalent to %matplotlib in IPython
    get_ipython().magic('matplotlib')
except:
    pass
# Solve model
ml.solve()
# Contour results
contourList = timcontour(ml, 0, 20000, 50, 0, 20000, 50, 3, 20,returncontours = True)

trace_example1()

print "The contour elevations are:"
print contourList.levels

i = 0
while True:
    print "Contour for elevation: " + str(161 + i)
    print contourList.collections[i].get_paths()
    print i
    i += 1
