# Script modifications for Creality K1

I have a Creality K1 3D printer.

I'm also both impatient and obsessed with experimenting and improving things via mods.

This repository documents my efforts to change the custom macro files and script files on the K1 to improve things in a few ways.

Currently I've done the following:

* Add more useful log messages.
* Override the G28 bed probe temperature. This will reduce/eliminate the need to cool down the extruder at the start of each print.
  * TODO: Just run G28 prior to even heating the extruder.
  * Or even better, heat to G28 temperature BEFORE heating to printing temp.
  * Right now it's sort of a mess, I'm just using `PRINT_PREPARED` to skip the entire heated `G28` process and then screwing with `CX_PRINT_DRAW_ONE_LINE` to get it to set the extruder and bed temps. Not idea. Fix.
* Set the cooling fan speed to half after printing, so it won't be as loud/obnoxious. Will take longer to cooldown but that's fine.

This is also where I'll experiment with different techniques to improve the printer, such as:

* Retract filament a tiny bit after drawing the purge line to reduce oozing.