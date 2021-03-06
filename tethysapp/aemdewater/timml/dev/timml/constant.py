import numpy as np
import inspect # Used for storing the input
from element import Element
from equation import HeadEquation

class ConstantBase(Element, HeadEquation):
    def __init__(self, model, xr=0, yr=0, hr=0.0, layer=0,\
                 name='ConstantBase', label=None, aq=None):
        self.storeinput(inspect.currentframe())
        Element.__init__(self, model, Nparam=1, Nunknowns=1, layers=layer,\
                         name=name, label=label)
        self.Nparam = 1 # Defined here and not in Element as other elements can have multiple parameters per layers
        self.Nunknowns = 0
        self.xr = xr
        self.yr = yr
        self.hr = hr
        self.aq = aq
        self.model.add_element(self)
    def __repr__(self):
        return self.name + ' at ' + str((self.xr, self.yr)) + ' with head  ' + str(self.hr)
    def initialize(self):
        if self.aq is None:
            self.aq = self.model.aq.find_aquifer_data(self.xr, self.yr)
        self.aq.add_element(self)
        self.Ncp = 1
        self.xc = np.array([self.xr])
        self.yc = np.array([self.yr])
        self.pc = self.hr * self.aq.T[self.pylayers]
        self.parameters = np.atleast_2d(self.pc)
    def potinf(self, x, y, aq=None):
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((1, aq.Naq))
        if aq == self.aq:
            rv[0,0] = 1
        return rv
    def disinf(self, x, y, aq=None):
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((2, 1, aq.Naq))
        return rv

class Constant(ConstantBase, HeadEquation):
    def __init__(self, model, xr=0, yr=0, hr=0.0, layer=0, label=None):
        self.storeinput(inspect.currentframe())
        ConstantBase.__init__(self, model, xr=xr, yr=yr, hr=hr, layer=layer, \
                              name='Constant', label=label)
        self.Nunknowns = 1
    def initialize(self):
        ConstantBase.initialize(self)
        assert self.aq.ltype[0] == 'a', 'Constant element added to area that is semi-confined'
        self.resfac = 0.0  # required for HeadEquation
    def setparams(self, sol):
        self.parameters[:,0] = sol
        
class ConstantInside(Element):
    # Sets constant at points xc, yc equal to the average of the potential of all elements at points xc, yc
    # Used for the inside of an inhomogeneity
    def __init__(self, model, xc=0, yc=0, label=None):
        Element.__init__(self, model, Nparam=1, Nunknowns=1, layers=range(model.aq.Naq),\
                         name='ConstantInside', label=label)
        self.xc = np.atleast_1d(xc)
        self.yc = np.atleast_1d(yc)
        self.parameters = np.zeros((1,1))
        self.model.add_element(self)
    def __repr__(self):
        return self.name
    def initialize(self):
        self.aq = self.model.aq.find_aquifer_data(self.xc[0], self.yc[0])
        self.aq.add_element(self)
        self.Ncp = len(self.xc)
    def potinf(self, x, y, aq=None):
        '''Can be called with only one x,y value'''
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((1, aq.Naq))
        if aq == self.aq:
            rv[0,0] = 1
        return rv
    def disinf(self, x, y, aq=None):
        '''Can be called with only one x,y value'''
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((2, 1, aq.Naq))
        return rv
    def equation(self):
        mat = np.zeros((1, self.model.Neq))
        rhs = np.zeros(1)  # Needs to be initialized to zero
        for icp in range(self.Ncp):
            ieq = 0
            for e in self.model.elementlist:
                if e.Nunknowns > 0:
                    if e != self:
                        mat[0:, ieq:ieq+e.Nunknowns] += \
                        e.potinflayers(self.xc[icp], self.yc[icp], self.pylayers).sum(0)
                        ieq += e.Nunknowns
                    #else:
                    #    mat[0, ieq:ieq+e.Nunknowns] += -1
                else:
                    rhs[0] -= \
                    e.potentiallayers(self.xc[icp], self.yc[icp], self.pylayers).sum(0)
        return mat, rhs
    def setparams(self, sol):
        self.parameters[:,0] = sol
        
class ConstantStar(Element, HeadEquation):
    def __init__(self, model, hstar=0.0, label=None, aq=None):
        Element.__init__(self, model, Nparam=1, Nunknowns=0, layers=0,\
                         name='ConstantStar', label=label)
        self.hstar = hstar
        self.aq = aq
        self.model.add_element(self)
    def __repr__(self):
        return self.name + ' with head  ' + str(self.hstar)
    def initialize(self):
        self.aq.add_element(self)
        self.aq.constantstar = self
        self.parameters = np.zeros((1,1))
        self.potstar = self.hstar * self.aq.T
    def potinf(self, x, y, aq=None):
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((1, aq.Naq))
        return rv
    def potentiallayers(self, x, y, pylayers, aq=None):
        '''Returns array of size len(pylayers) only used in building equations
        Defined here as it is the particular solution inside a semi-confined aquifer
        and cannot be added by using eigen vectors'''
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        pot = np.zeros(len(pylayers))
        if aq == self.aq:
            pot[:] = self.potstar
        return pot[pylayers]
    def disinf(self, x, y, aq=None):
        if aq is None: aq = self.model.aq.find_aquifer_data(x, y)
        rv = np.zeros((2, 1, aq.Naq))
        return rv