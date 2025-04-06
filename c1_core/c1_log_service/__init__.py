"""Initialize the c1_log_service subpackage of c1_core package"""
# allow absolute import from the root folder
# whatever its name is.
import sys  # don't remove required for error handling
import os
import c1_core.c1_log_service.environment_tracing
import c1_core.c1_log_service.environment_logging

# Import from sibling directory ..\databricks_service
OS_NAME = os.name

sys.path.append("..")
if OS_NAME.lower() == "nt":
    print("c1_log_service: windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "\\..\\..\\..")))
else:
    print("c1_log_service: non windows")
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../..")))
    sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../../..")))


__all__ = ["environment_logging", "environment_tracing"]
