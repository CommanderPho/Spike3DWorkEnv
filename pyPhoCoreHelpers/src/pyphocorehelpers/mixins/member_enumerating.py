import inspect # for getting the member function names


class AllFunctionEnumeratingMixin:
    """Implementors can enumerate their functions. """

    @classmethod
    def get_all_functions(cls, use_definition_order=True):
        """ lists all functions for a class optionally in the order they are definined in a file        
        return inspect.getmembers(cls, predicate=inspect.isfunction) # return the list of tuples for each function. The first element contains the function name, and the second element contains the function itself.

         use_definition_order: if True, the tuples are returned in the order they are defined in the file. Otherwise, in alphabetical order.
         all_function_tuples is a list of tuples for each function. The first element contains the function name, and the second element contains the function itself.
        """
        all_function_tuples = inspect.getmembers(cls, predicate=inspect.isfunction) # could use `inspect.isroutine`? NO! This does not return the functions
        
        if use_definition_order:
            # members = []
            member_line_numbers = []
            for name, obj in all_function_tuples:
                source, start_line = inspect.getsourcelines(obj) # get the line number for the function
                # members.append([name, obj, start_line])
                member_line_numbers.append(start_line)
            # returns the ordered result
            return [x for _, x in sorted(zip(member_line_numbers, all_function_tuples))] # sort the returned function tuples by line number
        else:
            return all_function_tuples
        
    @classmethod
    def get_all_function_names(cls, use_definition_order=True):
        all_fcn_tuples = list(cls.get_all_functions(use_definition_order=use_definition_order))
        return [a_name for (a_name, a_fn) in all_fcn_tuples] # returns the list of names
        

    

# NOT YET IMPLEMENTED
class AllCallableEnumeratingMixin:
    """Implementors can enumerate their callable members.
    
    #TODO 2023-06-14 19:33: - [ ] NOT YET IMPLEMENTED. There is an issue with this approach and it returns a bunch of things that I wasn't expecting. Debug with a callable class and a function in `pyphoplacecellanalysis.General.Pipeline.Stages.DisplayFunctions.MultiContextComparingDisplayFunctions.MultiContextComparingDisplayFunctions.MultiContextComparingDisplayFunctions`.
    
    """

    @classmethod
    def get_all_callables(cls, use_definition_order=True):
        """Lists all callable members for a class, optionally in the order they are defined in a file.

        Args:
            use_definition_order (bool): If True, the callables are returned in the order they are defined in the file.
                                         Otherwise, they are returned in alphabetical order.

        Returns:
            list: A list of tuples for each callable member. The first element contains the member name,
                  and the second element contains the member itself.
        """
        all_member_tuples = inspect.getmembers(cls) # , predicate=inspect.isroutine inspect.getmembers is used without a predicate, so it returns all members of the class. Then, during the sorting or filtering process, the callable function is used to exclude non-callable members and include callable classes as well.
        
        if use_definition_order:
            member_line_numbers = []
            for name, obj in all_member_tuples:
                try:
                    source, start_line = inspect.getsourcelines(obj) # get the line number for the function
                    member_line_numbers.append(start_line)
                except Exception as e:
                    raise e
                else:
                    pass
                
            # returns the ordered result
            return [x for _, x in sorted(zip(member_line_numbers, all_member_tuples)) if callable(x[1])] # sort the returned function tuples by line number
        else:
            return [(name, member) for name, member in all_member_tuples if callable(member)]

    @classmethod
    def get_all_callable_names(cls, use_definition_order=True):
        all_callable_tuples = list(cls.get_all_callables(use_definition_order=use_definition_order))
        return [name for (name, member) in all_callable_tuples] # returns the list of names


    # # ==================================================================================================================== #
    # # Compatibility functions with `AllFunctionEnumeratingMixin`                                                           #
    # # ==================================================================================================================== #
    # # Note that they return callables, not just functions, so the output will differ from the actual `AllFunctionEnumeratingMixin` outputs.
    # @classmethod
    # def get_all_functions(cls, use_definition_order=True):
    #     return cls.get_all_callables(use_definition_order=use_definition_order)

    # @classmethod
    # def get_all_function_names(cls, use_definition_order=True):
    #     return cls.get_all_callable_names(use_definition_order=use_definition_order)