# Drawing-based replacement models

The WH148 potentiometers and Tiny 2350 now use custom drawing-based models.
The RJ45 now uses a model and footprint built from the supplied mechanical
drawing. Its contact numbering is a user-approved prototype assumption pending
physical checking; see ../RJ45_CONTINUITY_CHECK.md.

## WH148 potentiometers

Source: user's mechanical drawing for the EEEEE kit, Amazon ASIN B0FGD497QN.
The drawing specifies 5 mm terminal pitch, 1.0 x 0.4 mm terminals, a 16.5 mm
housing, 17 mm front plate, 9.2 mm rear-to-shaft datum length, 15 +/- 0.5 mm
shaft length, 6 mm shaft diameter, 18 knurl teeth and an M7 x 0.75 bushing.

The new BFM:WH148_Horizontal_P5.00mm footprint uses 1.3 mm round finished holes
and 2.5 mm pads. These are chosen hole/pad sizes, not manufacturer land-pattern
recommendations. Pin numbers follow the supplied shaft-end view. All existing
pad-to-net assignments are preserved. Direct mounting puts the shafts parallel
to the board, pointing toward its top edge. Pots are 20 mm apart.

Model coordinates: middle terminal at X/Y zero, shaft toward +Y, carrier top
Z=0. A 0.5 mm substrate-to-board seating gap is assumed. Detailed metal tabs,
substrate contours and bends are approximate; thread crests are cosmetic rings.
Model clearances do not account for the user's knob size, enclosure or nuts.

## Tiny 2350

Sources:
- https://shop.pimoroni.com/products/tiny-2350
- https://cdn.shopify.com/s/files/1/0174/1800/files/tiny-2350-mechanical-diagram.pdf?v=1725452657
- https://cdn.shopify.com/s/files/1/0174/1800/files/tiny2350_pinout_diagram.pdf?v=1723124465

The model has an 18 x 21.3 mm PCB, 2.54 mm pitch and 15.24 mm header-bank spacing.
The carrier footprint's previously mirrored banks are corrected. With USB up,
GP0-GP7 run down the right bank, and VBUS/GND/3V3/A3/A2/A1/A0/GND down the left.
On this carrier the module is rotated with USB facing the right board edge.
The module center is (127.25,58) mm. The model includes switches, Qw/ST socket,
USB shell, castellations, labels and underside components.

The mounted model assumes 2.54 mm male header spacers and lifts the bare module
2.54 mm above the carrier. The PCB thickness, component heights, USB internals
and fine details absent from the drawing are visual estimates. This is custom
CAD, not a manufacturer-supplied STEP model or an enclosure-fit certification.

## PJ-320A MIDI jack

J2 now uses the Keebio PJ-320A STEP and a locally adapted footprint:
https://github.com/keebio/Keebio-Parts.pretty/blob/master/3dmodels/PJ-320A.step
https://github.com/keebio/Keebio-Parts.pretty/blob/master/TRRS-PJ-320A.kicad_mod
The MIT license is preserved in LICENSE-Keebio.txt.

The user's supplied uxcell pinout identifies sleeve=1, tip=4, ring1=3, ring2=2.
This overrides the tip/ring2 labels in the upstream footprint. Pin 4 carries
MIDI_TIP and pin 3 carries MIDI_RING. Ring2 (pin 2) is unused; sleeve (pin 1)
remains unconnected, preserving the old design's sleeve treatment. No claim
of complete MIDI electrical compliance or schematic parity is made here.

The footprint retains four plated slots and two locating holes from Keebio.
Its outline was adapted to clear solder mask and the board edge. The connector
faces right at (138,86) mm, with the mouth at the board edge. Its 3D geometry
and locating-hole dimensions come from the community model, not an uxcell
dimensional drawing. The supplied image establishes the electrical pinout.

## Validation

KiCad 10.0.6 loads the board and renders the bundled models. All 26 components
and all pad-to-net assignments outside J2 are preserved. J2's original tip/ring
nets are remapped by function to pins 4/3. The corrected pad geometry was
rerouted and ground copper refilled. validation/drc.json
reports zero violations and zero unconnected items. Schematic parity and the
remaining draft connector footprints are outside this verification.
