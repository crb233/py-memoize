from functools import wraps
import atexit
import pickle
import os

class MemoizationError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return self.message
    
    def __repr__(self):
        return 'MemoizationError({})'.format(self.message)

class Memoizer:
    '''
    Creates a memoization decorator which memoizes the results of function
    calls, generally making the function faster but more memory intensive.
    
    If 'keep' is set to True, memoized results will be stored so that they can
    be accessed after the program exits.
    
    Other keyword parameters 'directory' and 'naming' can be set to control the
    location and naming scheme of stored memoization files.
    
    Calling dump() on a decorated function will force the results to be stored
    immediately. In any case, they will be stored right before the program
    exits, if it exits normally.
    
    Calling clear() on a decorated function will clear all memoized results.
    
    Note: This should only be used with pure functions which have no side
    effects and always return the same value given a particular set of inputs.
    '''
    
    DEFAULT_KEEP = True
    DEFAULT_DIRECTORY = ''
    DEFAULT_NAMING = '{.__module__}.{.__name__}.pickle'
    
    def __init__(self, **kwargs):
        self.keep = kwargs.get('keep', DEFAULT_KEEP)
        self.directory = kwargs.get('directory', DEFAULT_DIRECTORY)
        self.naming = kwargs.get('naming', DEFAULT_NAMING)
    
    def __call__(self, f):
        '''
        Use this object as a decorator, memoizing the function f.
        '''
        self.decorate(f)
    
    def get_filename(self, f):
        '''
        Gets the filename (path) for a gven function.
        '''
        return os.path.join(self.directory, self.naming.format(f))
    
    def load_memoized(self, filename):
        '''
        Loads the memoized results of a function from the given file. If the
        file doesn't exist or cannot be read, return an empty dictionary.
        '''
        try:
            file_obj = open(filename, 'rb')
            table = pickle.load(file_obj)
            file_obj.close()
            return table
        except:
            return {}
    
    def make_clear_function(self, table):
        '''
        Creates and returns a function which clears the memoized results of the
        given function. This operation cannot be undone.
        '''
        def clear():
            table.clear()
        
        return clear
    
    def make_dump_function(self, table, filename):
        '''
        Creates and returns a function which dumps the memoized results to the
        given file. The generated function is also registered to run before the
        pogram exits when it exits normally.
        '''
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
        
        return dump
    
    def decorate(self, f):
        '''
        Decorates the functon f, return a memoized version of the it.
        '''
        
        if self.keep:
            filename = self.get_filename(f)
            table = self.load_memoized(filename)
        
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
        
        if self.keep:
            new_f.clear = self.make_clear_function(table)
            new_f.dump = self.make_dump_function(table, filename)
        
        return new_f
