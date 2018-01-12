from functools import wraps
import atexit
import pickle

class MemoizationError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message
    
    def __repr__(self):
        return 'MemoizationError({})'.format(self.message)

def temp(f):
    '''
    Memoizes the results of function calls, generally making the function
    faster but more memory intensive. Memoized results are lost when the
    program exits.
    
    Note: This should only be used with pure functions which have no side
    effects and always return the same value given a particular set of inputs.
    '''
    
    table = {}
    
    @wraps(f)
    def new_f(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key in table:
            return table[key]
            
        val = f(*args, **kwargs)
        table[key] = val
        return val
        
    new_f.memoized = table
    return new_f

def perm(f):
    '''
    Memoizes the results of function calls, generally making the function
    faster but more memory intensive. Memoized results are stored permanently
    so that they can be accessed even after the program exits.
    
    Calling dump() will force the results to be stored immediately. Otherwise,
    they will be stored right before the program exits normally.
    
    Note: This should only be used with pure functions which have no side
    effects and always return the same value given a particular set of inputs.
    '''
    
    filename = 'memoized.{}.{}.pickle'.format(f.__module__, f.__name__)
    
    # load memoized results
    try:
        file_obj = open(filename, 'rb')
        table = pickle.load(file_obj)
        file_obj.close()
    except:
        table = {}
    
    # store memoized results before the program exits
    @atexit.register
    def dump():
        try:
            file_obj = open(filename, 'wb')
            pickle.dump(table, file_obj)
            file_obj.close()
        except RecursionError:
            raise MemoizationError('Recursion depth exceeded in memoized data for function "{}"'.format(f.__name__))
        except pickle.PicklingError:
            raise MemoizationError('Encountered an unpickleable object in memoized data for function "{}"'.format(f.__name__))
        except:
            raise MemoizationError('Failed to write memoized data for function "{}"'.format(f.__name__))
    
    # method for clearing memoized data
    def clear():
        table = {}
    
    # create the memoized function
    @wraps(f)
    def new_f(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key in table:
            return table[key]
        
        val = f(*args, **kwargs)
        table[key] = val
        return val
    
    new_f.memoized = table
    new_f.clear = clear
    new_f.dump = dump
    return new_f
