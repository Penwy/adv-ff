## Pyparsing troubleshooting

Adv-ff requires the [PyParsing](https://pypi.org/project/pyparsing/) python module to properly function. The script attempts to automatically install it if it isn't available, but that process is not infallible especially given the diversity of python installs and the quirks of obspython, and if you landed on this page, it's likely because it failed for you.

The first and obvious solution is to manually install that module yourself. That would typically be done with pip, `python -m pip install pyparsing`, however different setups might have different ways to do it (if you're on flatpak, check below).

A second solution is to give me information about your python install, so that I can tentatively modify the autoinstall code to work for your case (and any future users with the same setup).
To do that, follow the steps below :
- Download the `print_info.py` file at the top of this page.
- Add it as a script in OBS.
- Close OBS, reopen it.
- In OBS, click on Help > Log Files > Upload current log file, and copy the URL it gives you.
- [Create an issue](https://github.com/Penwy/adv-ff/issues) including that URL


### If you're on flatpak

Flatpak does not make it possible to install python modules to the version of python it uses. My solution to this is incredibly cursed, but it works and I found no other way.

In order for this script to recognise the pyparsing module on flatpak you need to :
- Have installed on the host the same minor version of python than the one the flatpak uses (adv-ff prints the version of python it runs on in the script log when it loads, check it there).
- Install pyparsing to that version of python, in `~/.local/lib/python<version>/site-packages/` (default user install).






