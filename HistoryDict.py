import numpy as np

# History Make vlaue more smooth
class History():
    def __init__(self, dict_size, max_size = 5 ):
        self.Max_Size = max_size
        self.historyDict = {}
        for i in range(0, dict_size):
            self.historyDict[ str(i) ] = []

    # add a history
    def add(self, values):
        for (key, value) in zip( self.historyDict, values ):
            self.historyDict[key] += [value]

    # remove first one history
    def pop(self):
        for key in self.historyDict:
            self.historyDict[key].pop(0)
    
    # get history size
    def get_size(self):
        return len( self.historyDict[ '0' ] )

    # get all of dict average 
    def get_average(self):
        res = []
        for key in self.historyDict:
            res += [np.mean( self.historyDict[key], axis=0)]
        return res

    # judge is that history size full
    def is_full(self):
        return True if (len( self.historyDict[ '0' ] ) >= self.Max_Size) else False
        