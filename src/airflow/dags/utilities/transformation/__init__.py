import pkgutil
import logging

__path__ = pkgutil.extend_path(__path__, __name__)
for importer, modname, ispkg in pkgutil.walk_packages(path=__path__, prefix=__name__+'.'):
    try:
        __import__(modname)
    except Exception as ex:
        logging.critical(f"UNABLE TO IMPORT {modname}. Exiting")
        logging.critical(str(ex))
