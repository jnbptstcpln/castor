
import importlib


class Library:
    @staticmethod
    def get(id):

        # Pour le type "*", on n'applique aucune forme de casting
        if id == "*":
            return lambda x:x

        builtin = {
            'int': int,
            'float': float,
            'string': str,
            'list': list,
            'dict': dict
        }

        try:
            return builtin[id]
        except KeyError:
            pass

        module_part = id.split(".")
        component_name = module_part.pop()
        module_id = ".".join(module_part)

        try:
            module = importlib.import_module(module_id)
        except ModuleNotFoundError:
            raise Exception("Aucun module nommé '"+module_id+"'")

        try:
            return getattr(module, component_name)
        except AttributeError:
            raise Exception("Aucun type de données nommé '"+component_name+"' au sein du module '"+module_id+"'")

    @staticmethod
    def default(id):

        # Pour le type "*", on n'applique aucune forme de casting
        if id == "*":
            return None

        builtin = {
            'int': 0,
            'float': 0.0,
            'string': "",
            'list': [],
            'dict': {}
        }

        try:
            return builtin[id]
        except KeyError:
            pass

        module_part = id.split(".")
        component_name = module_part.pop()
        module_id = ".".join(module_part)

        try:
            module = importlib.import_module(module_id)
        except ModuleNotFoundError:
            raise Exception("Aucun module nommé '"+module_id+"'")

        try:
            return getattr(module, component_name)
        except AttributeError:
            raise Exception("Aucun type de données nommé '"+component_name+"' au sein du module '"+module_id+"'")
