
import numpy as np
from scipy.optimize import curve_fit


class CurveF(object):
    
    @staticmethod
    def liner(t, a, b):
        return(a * t + b)
    
    @staticmethod
    def logistic(t, a, b, c, d):
        return c + (d - c)/(1 + a * np.exp(- b * t))

    @staticmethod
    def exponential(t, a, b, c):
        return a * np.exp(b * t) + c

    
    def __init__(self, x=None, y=None, maxfev=1000000):
        self.x = None
        self.y = None
        self.maxfev = maxfev
        
        self.set_xy(x,y)
        
        self.fitinfo = {
            'liner'      :{ 'func':  CurveF.liner,        'popt': None, 'pcov': None, 'para': dict()},
            'logistic'   :{ 'func':  CurveF.logistic,     'popt': None, 'pcov': None, 'para': dict()},
            'exponential':{ 'func':  CurveF.exponential,  'popt': None, 'pcov': None, 'para': dict(bounds=([0,0,-100],[100,0.9,100]))}
        }

    def get_fitkind(self):
        ret = [ key for key,_ in self.fitinfo.items() ]
        return(ret)

    def set_xy(self, x, y):
        self.x = x
        self.y = y
        if( self.x is not None):
            if( type(self.x) != np.ndarray ):
                self.x = np.array(self.x, dtype=np.float)
        if( self.y is not None):
            if( type(self.y) != np.ndarray ):
                self.x = np.array(self.y, dtype=np.float)
    
    def fit(self, verbose=None, idstr=None):
        for i, (key, val) in enumerate(self.fitinfo.items()):
            if(verbose):
                prtstr = ''
                if( idstr is not None ):
                    prtstr += f'[{idstr}]'
                if(verbose is not None):
                    if(verbose == 1 and i==0):
                        print(f'{prtstr} fitting... ')
                    if(verbose >= 2):
                        print(f'{prtstr} fitting... {key}')
                
            popt = None
            pcov = None
            try:
                popt, pcov = curve_fit( val['func'], self.x,  self.y,  maxfev=self.maxfev, **val['para'])
            except:
                print(f"{prtstr} exception!!")
            val['popt'] = popt
            val['pcov'] = pcov
        if(verbose is not None):
            print(f'{prtstr} finish.')
    
    def calc(self, fitname, x ):
        fdic = self.fitinfo[fitname]
        if(fdic['popt'] is None):
            ret = []
        else:
            ret = fdic['func'](x, *fdic['popt'])
        ret = [ None if i is None else i.astype(int) for i in ret ]
        return(ret)
