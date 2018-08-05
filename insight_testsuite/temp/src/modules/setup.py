from distutils.core import setup, Extension
from distutils.sysconfig import get_python_inc

query = Extension("query", ["query/Py_query_res.c"])  
sort = Extension("sort_map", ["sort/sort_map.c"])

setup(
    ext_modules=[query, sort],
    include_dirs=[get_python_inc(), "sort", "query", "utilites"]
)

