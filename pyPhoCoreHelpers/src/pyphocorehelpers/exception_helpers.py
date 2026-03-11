import sys
import site # Required for StackTraceFormatting
from os.path import join, abspath # Required for StackTraceFormatting
from traceback import extract_tb, format_list, format_exception_only, format_exception # Required for StackTraceFormatting
from attrs import define, field, Factory
from contextlib import ContextDecorator

from typing import Callable, Tuple, List, Optional, Dict, Any

# ==================================================================================================================== #
# Exceptions and Error Handling                                                                                        #
# ==================================================================================================================== #
# @function_attributes(short_name=None, tags=['exception', 'exception-formatting', 'error-handling'], input_requires=[], output_provides=[], uses=[], used_by=['CapturedException.get_traceback_summary', 'ExceptionPrintingContext.print_formatted_exception'], creation_date='2024-10-30 13:10', related_items=[])
def format_sys_exc_info(exc_type, exc_value, traceback, include_func_name: bool=False) -> str:
    """ 
    The sys.exc_info() function returns a tuple (type, value, traceback):
        type: The exception type (BaseException subclass).
        value: The exception instance.
        traceback: A traceback object representing the call stack at the point where the exception was raised.
        
        
    Usage:
        exception_info = sys.exc_info()
        formatted_message: str = format_sys_exc_info(*exception_info)
    """
    # Add your custom formatting logic here.
    # print(f"An exception of type {exc_type.__name__} occurred. Arguments:\n{exc_value.args}")
    # Extract traceback details
    tb_formatted = format_exception(exc_type, exc_value, traceback)
    # Extract the last line of the traceback, which is the "Error" line.
    error_line = tb_formatted[-1]
    # Find the right part of the traceback information that includes the filename and line number.
    filename, line_number, func_name, line_text = extract_tb(traceback)[-1]
    # Generate the formatted string:
    formatted_message = f"{filename}:{line_number}" # "/tmp/ipykernel_92629/1788234204.py:3: ZeroDivisionError: division by zero"
    if (include_func_name and (len(func_name) > 0)):
        formatted_message = formatted_message + f"<fn: {func_name}>"
    formatted_message = formatted_message + f": {error_line.strip()}"
    return formatted_message




@define(slots=False, repr=False)
class CapturedException:
    """ Stores a captured exception in a try/catch block and its related info/context. Can also format its display.

    Info:
    
        The sys.exc_info() function returns a tuple (type, value, traceback):
            type: The exception type (BaseException subclass).
            value: The exception instance.
            traceback: A traceback object representing the call stack at the point where the exception was raised.


    Usage:
        import sys
        from pyphocorehelpers.exception_helpers import CapturedException

        # ...

        try:
            # *SOMETHING*
        except Exception as e:
            exception_info = sys.exc_info()
            e = CapturedException(e, exception_info)
            print(f'exception occured: {e}')
            if fail_on_exception:
                raise e
                
                
        

    """
    exc: BaseException = field()
    exc_info: Tuple = field()
    captured_result_state: Optional[object] = field(default=None) # additional state that you might want for debugging, but usually None
    
    """ An exception and its related info/context during the process of executing composed functions with error handling."""
    
    # def __repr__(self):
    #     # Don't print out captured_result_state (as it's huge and clogs the console)
    #     return f'!! {self.exc} ::::: {self.exc_info}'

    def __repr__(self):
        return f'CapturedException({self.exc}, traceback={self.get_traceback_summary()})'
    
    def get_traceback_summary(self) -> str:
        """Returns a formatted summary of the traceback."""
        exception_info = sys.exc_info()
        formatted_message: str = format_sys_exc_info(*self.exc_info, include_func_name=True)
        return formatted_message
        # tb = self.exc_info[2]
        # # Extract traceback information
        # tb_list = extract_tb(tb)
        # if tb_list:
        #     last_call = tb_list[-1]  # Get the last call in the traceback
        #     filename = last_call.filename
        #     lineno = last_call.lineno
        #     func_name = last_call.name
        #     line = last_call.line
        #     return f"{filename}, line {lineno}, in {func_name}\n    {line}"
        # else:
        #     return "No traceback available."
    
    def get_full_traceback(self) -> str:
        """Returns the full formatted traceback as a string."""
        return ''.join(format_exception(*self.exc_info))


    ## For serialization/pickling:
    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes (_mapping and _keys_at_init). Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        # Remove the unpicklable entries. 
        exc_info = state.pop('exc_info', None)

        state['exc_info'] = (exc_info[0], exc_info[1], None, )

        # del state['file']

        return state

    def __setstate__(self, state):
        # Restore instance attributes (i.e., _mapping and _keys_at_init).
        self.__dict__.update(state)
        



class ExceptionPrintingContext(ContextDecorator):
    """ A context manager that prints any exceptions that occur in its body, optionally suppressing them by default
    
    #TODO 2024-07-05 09:27: - [ ] This class makes debugging much harder.
    

    Related Notebook:
    "2024-03-05 - Exception Handling and Formatting.ipynb"


    Usage:
        from pyphocorehelpers.exception_helpers import ExceptionPrintingContext

        # Example Suppressing Exception:
            with ExceptionPrintingContext():
                1 / 0  # This will raise a ZeroDivisionError, which will be handled within our context manager and suppressed

        >> prints "/tmp/ipykernel_92629/1788234204.py:3: ZeroDivisionError: division by zero"

        # Example Not Suppressing (re-raising) Exception:
            try:
                with ExceptionPrintingContext(suppress=False):
                    1 / 0  # This will raise a ZeroDivisionError, which will be handled within our context manager but re-raised because suppress=False
            except ZeroDivisionError:
                print("ZeroDivisionError caught in the outer try-except block.")

        >> prints "/tmp/ipykernel_92629/1788234204.py:3: ZeroDivisionError: division by zero"
            raise exception, printing "ZeroDivisionError caught in the outer try-except block."


        # Example with custom `exception_print_fn`:
            with ExceptionPrintingContext(suppress=True, exception_print_fn=(lambda formatted_exception_str: print(f'\ta_prefix: {formatted_exception_str}')))::
                1 / 0  # This will raise a ZeroDivisionError, which will be handled within our context manager and suppressed

        >> prints "a_prefix: /tmp/ipykernel_102148/4108766447.py:2: ZeroDivisionError: division by zero"

    Generated by ChatGPT:
        by returning True from the __exit__ method, you are telling Python to suppress the exception once it has been handled. If you want the exception to be propagated (i.e., to be thrown outside of the with block), you can either return False or not return anything explicitly from the __exit__ method. 

    """
    def __init__(self, suppress=True, exception_print_fn: Optional[Callable]=None):
        """

        exception_print_fn: accepts a callable that takes a single string, the formatted output or defaults to the print function

        """
        self.suppress = suppress
        self.exception_print_fn = exception_print_fn or print # use default print function
    
    def __enter__(self):
        # The __enter__ method is run when entering the context.
        # You can set up here if needed, but for this purpose, we don't need to do anything.
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ 
            The __exit__ method is run when exiting the context.
            It receives the exception type, value, and traceback if an exception has occurred
        """
        if exc_type is not None:
            # If an exception has been raised, handle it.
            self.print_formatted_exception(exc_type, exc_value, traceback)
            # Return True if you want to suppress the exception,
            # return False if you want it to be propagated.
            return self.suppress  # Return the value of self.suppress to determine whether to suppress the exception 
        # Return False if no exception occurred or if your intention is to propagate the exception.
        return False 

    def print_formatted_exception(self, exc_type, exc_value, traceback):
        """ prints the exception in a reasonable format        
        """
        exception_info = sys.exc_info()
        formatted_message: str = format_sys_exc_info(*exception_info)
        self.exception_print_fn(formatted_message)






# ==================================================================================================================== #
# Stack Trace Formatting                                                                                               #
# ==================================================================================================================== #

class StackTraceFormatting(object):
    """

    https://stackoverflow.com/questions/31949760/how-to-limit-python-traceback-to-specific-files
    vaultah answered Oct 9, 2015 at 15:43

    They both use the traceback.extract_tb.
    It returns "a list of “pre-processed” stack trace entries extracted from the traceback object"; all of them are instances of traceback.FrameSummary (a named tuple).
    Each traceback.FrameSummary object has a filename field which stores the absolute path of the corresponding file.
    We check if it starts with any of the directory paths provided as separate function arguments to determine if we'll need to exclude the entry (or keep it).

    """
    @classmethod
    def spotlight(cls, *show):
        ''' Return a function to be set as new sys.excepthook.
            It will SHOW traceback entries for files from these directories. 
            https://stackoverflow.com/questions/31949760/how-to-limit-python-traceback-to-specific-files
            vaultah answered Oct 9, 2015 at 15:43
        '''
        show = tuple(join(abspath(p), '') for p in show)

        def _check_file(name):
            return name and name.startswith(show)

        def _print(type, value, tb):
            show = (fs for fs in extract_tb(tb) if _check_file(fs.filename))
            fmt = format_list(show) + format_exception_only(type, value)
            print(''.join(fmt), end='', file=sys.stderr)

        return _print

    @classmethod
    def shadow(cls, *hide):
        ''' Return a function to be set as new sys.excepthook.
            It will HIDE traceback entries for files from these directories. 
            https://stackoverflow.com/questions/31949760/how-to-limit-python-traceback-to-specific-files
            vaultah answered Oct 9, 2015 at 15:43
        '''
        hide = tuple(join(abspath(p), '') for p in hide)

        def _check_file(name):
            print(f'shadow:\t name: {name}')
            return name and not name.startswith(hide)

        def _print(type, value, tb):
            print(f'shadow:\t tb: {tb}')
            show = (fs for fs in extract_tb(tb) if _check_file(fs.filename))
            fmt = format_list(show) + format_exception_only(type, value)
            print(''.join(fmt), end='', file=sys.stderr)

        return _print

    @classmethod
    def restore_default(cls):
        """ Restores the default sys.excepthook from sys.__excepthook__
        
        """
        sys.excepthook = sys.__excepthook__
        print(f'Restored the default sys.excepthook from sys.__excepthook__.')
        return sys.__excepthook__

    @classmethod
    def shadow_sitepackages(cls):
        # Gets the "sitepackges" library directories for exclusion from the stacktrace
        curr_sitepackages = site.getsitepackages()
        print(f'Excluding sitepackages (library) directories from stacktraces: {curr_sitepackages}')
        sys.excepthook = cls.shadow(*curr_sitepackages)
        return sys.excepthook


# """ Solution for long and convoluted stacktraces into libraries. Installs a sys.excepthook
# From:
#     https://stackoverflow.com/questions/2615414/python-eliminating-stack-traces-into-library-code/2616262#2616262

# Solution by Alex Martelli answered Apr 10, 2010 at 23:37

# """

# # def trimmedexceptions(type, value, tb, pylibdir=None, lev=None):
# #     """trim system packages from the exception printout"""
# #     if pylibdir is None:
# #         import traceback, distutils.sysconfig
# #         pylibdir = distutils.sysconfig.get_python_lib(1,1)
# #         nlev = trimmedexceptions(type, value, tb, pylibdir, 0)
# #         traceback.print_exception(type, value, tb, nlev)
# #     else:
# #         fn = tb.tb_frame.f_code.co_filename
# #         if tb.tb_next is None or fn.startswith(pylibdir):
# #             return lev
# #         else:
# #             return trimmedexceptions(type, value, tb.tb_next, pylibdir, lev+1)

# # import sys
# # sys.excepthook=trimmedexceptions
# # This one doesn't seem to change anything either.

# import sys
# from pyphocorehelpers.print_helpers import StackTraceFormatting

# # ## TODO: Investigate https://pymotw.com/2/sys/exceptions.html to try and figure out why my stacktrace handling isn't working
# # # StackTraceFormatting.shadow_sitepackages()

# sys.excepthook = StackTraceFormatting.restore_default()
# # sys.excepthook = StackTraceFormatting.shadow('~\miniconda3\envs\phoviz_ultimate\lib\site-packages')
