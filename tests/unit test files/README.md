Every file in this directory should be a complete SED2 document with inputs and outputs.  Any external files such as models or data will be found up one directory in the 'resources/' folder (sed/tests/resources/).

Canonical output, when available, will be present in the outputs/ directory.  The filenames for reports will be:
  [SED base name]_[SED report id].csv

The filenames for plots will be:
  [SED base name]_[SED plot id].png

The simplest 'complete' SED2 file is 'ode_simulation.json'.  It loads a model, runs a simulation, and reports the output.

The other tests:
* constant_*.json:  These files all declare a constant, then ask for that constant in an output report.  Use these tests to check to make sure constants are being declared properly, and that reports can report the different kinds of output.
* model_import.json:  This file imports a model, then asks for elements of that model as an output report.
* model_full_output.json:  This file imports a model, then asks for 'the model' as an output report.  This should be the same as the output for a dictionary: a