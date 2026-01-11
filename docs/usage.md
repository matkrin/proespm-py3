# Usage

If you used [uv](https://docs.astral.sh/uv/) for installation, you can navigate
to the project root (the folder that contains the `pyproject.toml` file) and run
`proespm` with:

```sh
uv run src/proespm/main.py
```

You can then see the following graphical user interface that contains everything
for report creation:

![GUI](assets/gui.png)

With the <kbd>Browse</kbd> button you can choose the folder that contains your
data files from measurements. You can also enter the disired path in the input
field next to it.

If you used the button, the output path gets populated automatically with the
parent folder of the chosen folder. This is where the created report will be
saved. You can edit this path also directly in the input field or choose another
one with the <kbd>Save As</kbd> button.

Next, you can choose the colormap for Scanning Probe Microscopy (SPM) image
data. All
[matplotlib colormaps](https://matplotlib.org/stable/gallery/color/colormap_reference.html)
are available.

Finally, you can choose the color range that is used to create SPM images. If
you're not familiar with SPM, this basically allows to 'remove' outlier data
points from the color range.

You can then process your data and create a report by clicking the
<kbd>Start</kbd> button.

In the big area under the color range (log area), you will be presented with log
information about which files are processed at the moment. Under that, the
<kbd>Save Log</kbd> allows for saving this information to a file. This is
especially useful if any errors occur during processing. If you report any
errors, it is best to share a saved log file with the maintainers.

After the processing finished, you can open the created HTML report in a
browser.
