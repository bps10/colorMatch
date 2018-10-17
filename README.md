# colorMatch

A program for making color matches in an Oz vision display.

## Install

colorMatch depends on [Psychopy](http://www.psychopy.org/) to generate stimuli, [PySimpleGUI27](https://pypi.org/project/PySimpleGUI27/) for the parameters gui, [inputs](https://pypi.org/project/inputs/) for collecting user responses and [Numpy](http://www.numpy.org/) for mathematical computing. To install the dependencies, use:

```
sudo pip install Psychopy PySimpleGUI27 inputs numpy
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

## Program behavior

The colorMatch program creates a fixation dot and two background fields. One superimposes over the AO imaging / leak raster. The second is for matching.

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
| `down arrow`     | `X`             | decrease [hue, width, x position]            |
| `left arrow`     | `A`             | decrease [saturation, height, y position]    |
| `right arrow`    | `B`             | increase [saturation, height, y position]    |
| `enter`          | `right trigger` | increase [brightness]                        |
| `shift`          | `left trigger`  | decrease [brightness]                        |
| `control`        | `bottom trigger`| take large step sizes (applies to all above) |
| `space`          | `left gamepad`  | accept match                                 |
| `1`              | `START`         | step forward in experiment (see above)       |
| `2`              | `BACK`          | step backward in experiment (see above)      |
| `q` **or** `esc` | `center button` | end the experiment and save                  |


## Calibration

PR-650

## Hardware

* [Bits#](https://www.crsltd.com/tools-for-vision-science/visual-stimulation/bits-sharp-visual-stimulus-processor/)

* [Logitech F310 gamepad](https://www.logitechg.com/en-us/products/gamepads/f310-gamepad.html). This is optional. The keyboard works just fine as well.

* [TI lightcrafter](http://www.ti.com/tool/DLPLCR4500EVM)
