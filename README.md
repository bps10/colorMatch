# colorMatch

A program for making color matches in an Oz vision display.

## Install

colorMatch depends on [Psychopy](http://www.psychopy.org/) to generate stimuli, [PySimpleGUI27](https://pypi.org/project/PySimpleGUI27/) for the parameters gui, [inputs](https://pypi.org/project/inputs/) for collecting user responses and [Numpy](http://www.numpy.org/) for mathematical computing. To install the dependencies, use:

```
pip install --user Psychopy PySimpleGUI27 inputs numpy
```

To install the program:

```
git clone https://github.com/bps10/colorMatch
```

## Quick start

From outside of the colorMatch directory run:

```
python colorMatch
```

A parameter gui will ask for information about the subject and experimental parameters. When 

*Note: If using a Windows 10 machine, make sure that Game Bar is disabled.* To disable: `settings > gaming > gamebar`

## Program behavior

The colorMatch program creates a fixation dot and two background fields. One is superimposed over the AO imaging / leak raster, the second is for matching. 

### Procedure

1. Set the position of the fixation relative to the imaging raster.
2. Center the AO background.
3. Adjust the size of the AO background to perfectly fill the imaging raster.
4. Adjust the hue, saturation and brightness of the fellow field.
5. Make color matches.

### Active keys:

| keyboard         | gamepad         | reaction                                     |
|:---------------- | --------------- | -------------------------------------------- |
| `up arrow`       | `Y`             | increase [hue, width, x position]            |
| `down arrow`     | `A`             | decrease [hue, width, x position]            |
| `left arrow`     | `X`             | decrease [saturation, height, y position]    |
| `right arrow`    | `B`             | increase [saturation, height, y position]    |
| `enter`          | `right trigger` | increase [brightness]                        |
| `shift`          | `left trigger`  | decrease [brightness]                        |
| `control`        | `bottom trigger`| take large step sizes (applies to all above) |
| `space`          | `left gamepad`  | accept match                                 |
| `1`              | `START`         | step forward in experiment (see above)       |
| `2`              | `BACK`          | step backward in experiment (see above)      |
| `q` **or** `esc` | `center button` | end the experiment and save                  |


### Offline mode

Color matches can be practiced in "offline" mode. In this configuration, two test and reference squares are displayed. After each match, each square is randomly updated with a new color. The subject's task is to adjust the test square until it matches the reference. This mode is intended for practice and baseline measurements. Offline mode can be selected with the radio button in the configuration gui that begins each session.

## Calibration

Monitor calibration should be done with a spectraradiometer, such as the [PR-650](https://pypi.org/project/PySimpleGUI27/).

## Hardware

* [Bits#](https://www.crsltd.com/tools-for-vision-science/visual-stimulation/bits-sharp-visual-stimulus-processor/): A stimulus processor from Cambridge Research Systems. Bits# is basically a graphics card designed for vision science experiments. It provides display calibration solutions, precise timing and increase color bit depth (up to 14 bit per channel). Bits# is not necessary to run the program.

* [Logitech F310 gamepad](https://www.logitechg.com/en-us/products/gamepads/f310-gamepad.html) for user responses. This is optional. The keyboard works just fine as well.

* [TI lightcrafter](http://www.ti.com/tool/DLPLCR4500EVM) is the display currently used in the Roorda Lab. Any color display will run with this program.
