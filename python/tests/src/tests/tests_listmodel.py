import pkgutil
import importlib
import inspect
from pathlib import Path
from PySide6.QtCore import QObject, QAbstractListModel
from enums import Roles

class TestsListModel(QAbstractListModel):
    
    __cache = []

    def __init__(self, parent:QObject):
        super().__init__(parent)

        self.__update_cache()

    def __update_cache(self):
        """ The cache contains all tests automatically discovered """
        app_root_path = Path(__file__).parent
        packages_path = app_root_path / "TestPackages"
        print(f"Look for test packages into {packages_path}")

        for _, package_name, _ in pkgutil.iter_modules([packages_path]):
            print(f"Module {package_name} discovered")

            #package_path = packages_path / package_name
            package = importlib.import_module(f"TestPackages.{package_name}")

            tests = []
            for _, module_name, _ in pkgutil.iter_modules(package.__path__):
                print(f"Test file {module_name} discovered")
                #module = importlib.import_module(module_name)
                for nom, class_ in inspect.getmembers(module_name, inspect.isclass):
                    print(nom, type(nom).__name__)
            

    def rowCount(self, /, parent = ...):
        return super().rowCount(parent)
    
    def columnCount(self, parent):
        return super().columnCount(parent)
    
    def data(self, index, /, role = ...):
        return super().data(index, role)
    
    def roleNames(self) -> dict:
        roles = {
            Roles.RoleProgress: b'progress',
            Roles.RolePackage: b'package',
            Roles.RoleTest: b'test'
        }
        return roles
