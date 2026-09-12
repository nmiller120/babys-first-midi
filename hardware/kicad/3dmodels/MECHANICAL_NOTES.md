# Drawing-based replacement models

The WH148 potentiometers and Tiny 2350 now use custom drawing-based models.
RJ45 and TRS models remain illustrative placeholders; their footprints still
require checking against the actual purchased parts.

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

## Validation

KiCad 10.0.6 loads the board and renders the bundled models. All 26 components
and every existing numbered pad's net assignment are preserved. The corrected
pad geometry was rerouted and ground copper refilled. validation/drc.json
reports zero violations and zero unconnected items. Schematic parity and the
remaining draft connector footprints are outside this verification.
