# Binaries

The sixth experiment is packaged with the executables that were used to conduct the experiment and post-process the results.  There are a number of minor supporting files, but only those necessary to understand the data are documented here.
- [test.py](#test) Executes a test
- [post1.py](#post1) Extracts calibrated current, voltage, resistance, and other parameters
- [post2.py](#post2) Plots standoff versus voltage
- [post3,py](#post3) Plots the amalgamated plots found in `./export`

## Test <a id='test'></a>

The `test.py` Python script prompts the user to enter a series of experimental parameters before calling the LConfig binaries to execute data acquisition (https://github.com/chmarti1/lconfig).  These values are embedded in the headers of the data files.

### Manual entry parameters
 **Cutting Oxygen (psig):** Expects the pressure set at the cutting oxygen regulator in psi gauge.
 **Initial standoff (in):** Expects the standoff (in inches) to which the torch was set prior to the start of the experiment.  For all future points, changes in the linear potentiometer will be used to establish the standoff.
 **Feed rate (ipm):** Expects the cut speed in inches per minute.
 **Plate thickness (in):** Expects the plate thickness in inches.

### Data acquisition process

First, the LConfig `lcburst` binary is called using the `flow.conf` configuration file to measure the preheat oxygen and fuel gas flow rates.  These results are stored in `../data/<data_dir>/flow.dat`.

Then, the `lcrun` binary is called using `lcrun.conf`.  This is designed to interact with a custom precision current/voltage driver documented in [shunt2.pdf](./shunt2.pdf).  The digital output settings (do4 - do7) are used to configure the mode of the amplifier to low-current measurement range and current output mode.  Only channel 0 (AIN10 and AIN11) of the two driver channels is used.

The resulting data are stored in `../data/<data_dir>/vis.dat` (VIS standing for voltage, current, and standoff).  

## Post 1 <a id='post1'></a>

The `post1.py` script creates a directory at `../data/<data_dir>/post1` which will contain its outputs.  It generates a series of figures and a single parameter file that describes the test conditions.

If `post1.py` is called with no arguments, will loop through all directories in the `../data` directory, and it will process every data set without an existing directory at `../data/<data_dir>/post1/`.  

The last argument provided to `post1.py` will always be interpreted as identifying the data set to process.  It may the full name of the `<data_dir>` or it may be any number of its trailing characters.  Since the data directories are the timestamp at which the test was taken, the last four digits will be quasirandom and highly likely to be a unique identifier for the data set.  For example,
```bash
$ ./post1.py 3817
```
will process the data set at `../data/20201118173817/`.

Users may optionally add flags `force` or `quiet` before the data set identifier.  When `force` is present, the analysis will overwrite any previous results.  When `quiet` is present, summary data will not be printed to the terminal.

### `post1.param`
The first post-processing step constructs a whitespace separated parameter file at `../data/<data_dir>/post1/post1.param` from the test parameters.  The file is arranged so that each line has a parameter name (containing no white space) sparated by a space from its numerical value.  It includes the following parameters:
- `soinit_in` The initial standoff in inches (manually specified)
- `somin_in` The minimum standoff encountered throughout the test
- `somax_in` The maximum standoff encoutnered throughout the test
- `plate_in` The plate thickness (manually specified)
- `preheat_sec` The time in the test when preheating is believed to begin (estimated automatically by watching the standoff sensor)
- `start_sec` The time in the test when cutting begins (set to zero by default so the user may manually specify a value)
- `stop_sec` The time in the test when cutting stops (set to the end-of-test by default so the user may manually specify a value)
- `fex_hz` The current excitation frequency in Hz (determined from the embedded configuration header)
- `fs_hz` Sample rate in Hz (determined from the embedded configuration header)
- `fg_scfh` Fuel gas flow rate in standard cubic feet per hour (determined from `flow.dat`)
- `o2_scfh` Preheat oxygen flow rate in standard cubic feet per hour (determined from `flow.dat`)
- `total_scfh` Total preheat flow in standard cubic feet per hour (`o2_scfh` + `fg_scfh`)
- `ratio_fto` Fuel/oxygen ratio (`fg_scfh` / `o2_scfh`)
- `cuto2_psig` Cutting oxygen pressure (manually specified)
- `feedrate_ipm` Cutting feed rate in inches per minute (manually specified)

### `vft.png` and `ift.png`

The `vft.png` and `ift.png` plots are waterfall diagrams of the voltage and current signals throughout the test.  Frequency is on the vertical axis and time is on the horizontal axis.  Bright pixels represent a window of time over which a strong frequency component was present.  Dark pixels represent weak frequency content.  These are used to evaluate the quality of the data.

Since the experiments were conducted in current command mode, there should be a strong horizontal line at the current excitation frequency in `ift.png`.  However, during preheat and when the torch was not over the plate, super-harmonics can be seen.  The resistance of the flame is taken to be the ratio of `vft.png` to `ift.png` at the excitation.

### `vt.png`

The `vt.png` plot shows the voltage frequency content at 0 Hz, at the excitation frequency, and at the first and second super-haromonics.  The flame resistance will be taken to be proportional to the voltage at the excitation frequency.  This plot is used to quantitatively assess the contribution of nonlinearities to error.  If the super-harmonics are large during cutting, then the measurement will not be good.

### `rst.png` and `rs.png`

The `rst.png` plot shows resistance (calculated as the ratio of voltage signal amplitude to current excitation amplitude) and the standoff plotted on two separate subplots.  This plot is useful for looking for unusual events that might explain features of the data.  For example, if the standoff probe hung on a piece of slag, it would be evident here.

`rs.png` shows the same data, but plotted as resistance versus standoff.

## Post 2 <a id='post2'></a>

The `post2.py` script accepts a single command-line argument that specifies the data set on which to operate.  It works just like `post1.py` in this regard.

The second post processing step is separated from the first so users have an opportunity to manually enter `start_sec` and `stop_sec` parameters to trim away the junk data during preheat and after the cut is complete.  The result is a single plot found at `../data/<data_dir>/post2/rs.png`.

Much like its counterpart produced by `post1.py`, this version of `rs.png` plots resistance against standoff, but it has been more highly refined by trimming away junk data, and second axes are added for alternate units.  

At the top of the `post2.py` script is a variable, `color`.  When it is set to `True`, the plot will be a colored line that begins dark and proceeds to lighten.  Since the data are noisy and will overlap substantially, this helps a reader distinguish between parts of the plot at the beginning and end of cut.

## Post 3 <a id='post3'></a>

Finally, `post3.py` is designed to produce publication-quality plots just like `post2.py`, but with multiple data sets represented on the same plot.  Just like `post2.py`, `post3.py` has a line where `color` may be set to `True` or `False` to alternate between the two modes of operation.

`post3.py` accepts any number of arguments that indicate which data sets are to be represented on the plot and labels that should be used to identify them in a legend.  For example,
```bash
$ ./post3.py 2146 "test 2146" 3657 "test 3657"
```
plots results from tests `20201028152146` and `20201028153657` and gives them appropriate labels in a legend.

The result is written to new files in `../export` with a new title so not to overwrite any previous results.  Two files are generated: `../export/<#>.png` and `../export/<#>.param`.  The former is the resulting plot and the latter is the command that was used to generate it. 
