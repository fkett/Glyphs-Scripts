# About

This is a collection of Python scripts for the use with [Glyphs font editor](https://glyphsapp.com/).

# Installation

The scripts need to be in the `Scripts` folder inside the app’s `Application Support` folder.

1. Open `~/Library/Application Support/Glyphs/Scripts/`; either manually, or via *Script > Open Scripts Folder* (Cmd-Shift-Y). Place the scripts folder (or an alias) into that folder.
2. Reload Glyphs’ *Script* menu by holding down the Option (Alt) key and choosing *Script > Reload Scripts* (Cmd-Opt-Shift-Y). Now the scripts are visible in the *Script* menu.
3. For some of the scripts, you will also need to install Tal Leming's *Vanilla:* Go to *Glyphs > Preferences > Addons > Modules* and click the *Install Modules* button.

# About the scripts
## Font Info

* **Calculate avar table for CSS mapping:** Calculates the avar table required for mapping proprietary axis values to CSS compliant values. *Important* You must set Custom Parameters "Variation Font Origin" (*Font Info > Font*) and "Axis Location" (*Font Info > Masters* for extreme masters and "Variation Font Origin" master). The resulting table has to be manually inserted into the exported binary. *Requires Vanilla.*
* **Custom GASP table:** Allows setting custom sizes and values for the GASP table stored in the according Custom Parameter. *Important* Do not try to edit the Custom Parameter with the default dialogue (by double-clicking) afterwards, it will break the Custom Parameter. *Requires Vanilla.*

## Metrics

* **Change glyph width (symmetrically):** Changes the width of selected glyphs symmetrically by increasing sidebearings on both sides evenly. *Requires Vanilla.*
* **Round Kerning to nearest 5:** Round Kerning values of the selected Master to the nearest 5 (e.g. -7 > -10, 17 > 15, 23 > 25).

## Paths

* **Remove outside self-intertsections:** Finds self-intersections on the outside (mind the correct path direction) of the selected glyphs and removes them. Opens a tab with all changed glyphs.

# License

Copyright © 2020 Felix Kett.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use the software provided here except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>. See the License file included in this repository for further details.