from typing import Dict


class RegistryHolder(type):
    """ a metaclass that automatically registers its conformers as a known loadable data session format.     
        
    Usage:
        from pyphocorehelpers.mixins.auto_registering import RegistryHolder, BaseRegisteredClass
        RegistryHolder.get_registry()
        
    Defining Custom RegistyHolder type:

    ```python    
        from typing import Dict

        class DisplayFunctionRegistryHolder(RegistryHolder):
            REGISTRY: Dict[str, "DisplayFunctionRegistryHolder"] = {}
            
        class BaseRegisteredDisplayClass(metaclass=DisplayFunctionRegistryHolder):
            pass

        class TestDisplayClass(BaseRegisteredDisplayClass):
            pass
        
        DisplayFunctionRegistryHolder.get_registry()
    ```

    """
    REGISTRY: Dict[str, "RegistryHolder"] = {}

    def __new__(cls, name, bases, attrs):
        new_cls = type.__new__(cls, name, bases, attrs)
        """
            Here the name of the class is used as key but it could be any class
            parameter.
        """
        cls.REGISTRY[new_cls.__name__] = new_cls
        return new_cls

    @classmethod
    def get_registry(cls):
        return dict(cls.REGISTRY)


class BaseRegisteredClass(metaclass=RegistryHolder):
    """
    Any class that will inherits from BaseRegisteredClass will be included
    inside the dict RegistryHolder.REGISTRY, the key being the name of the
    class and the associated value, the class itself.        
    """
    pass

