# Data

Raw data files are contained in subdirectories of the `data` directory.  Each directory contains one data set representing a single cut.  The name of the data set's directory is the timestamp for the start of the test in the format `YYYYMMDDHHmmSS`.  

The data acquisition process controlled by [test.py](bin.md#test) creates two data files in each directory.  The `flow.dat` file contains raw voltage measurements from thermal mass flow meters on the preheat fuel and oxygen gases and the meta data required to calculate calibrated flow rates.  The `vis.dat` file contains voltage, current, and standoff measurements from the test and the meta data required to interpret the results.  For a detailed description of the data file formats or tools to work with them, visit (https://github.com/chmarti1/lconfig).  For more information on the meta data, read the [binary](bin.md) documentation.

If they are present, post-processing results produced by the [post1](bin.md#post1) and [post2](bin.md#post2) binaries are contained in sub-directories `data/<data_dir>/post1/` and `data/<data_dir>/post2/`.
