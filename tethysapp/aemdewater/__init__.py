# import sys
# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

# matplotlib in this app is used as a backend, non-interactive plotter
# to prevent matplotlib from attempting to produce images on the server
# the backend plotter needs to be selected as a type that is by default non-interactive

import matplotlib
matplotlib.use('Agg')
