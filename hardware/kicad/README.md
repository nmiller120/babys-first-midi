# Baby's First MIDI — KiCad

KiCad hardware design files for Baby's First MIDI.

The Rev A prototype board is routed on two copper layers, with a filled backside
ground zone. Open `babys-first-midi.kicad_pro` so KiCad loads the project rules and
the `BFM` footprint library from `fp-lib-table`.

## DRC repair, 2026-09-11

Starting from placement-only commit `f590c33`, this revision:

- Moves the RJ45 back to the left side, inside the board outline and clear of the
  MIDI jack; moves the MIDI jack away from the lower-right mounting hole.
- Rotates the five MOSFET footprints to provide separate gate, drain and source
  escape paths, then routes all required connections and refills ground copper.
- Preserves every pad number and net assignment from the starting board.
- Fixes silkscreen overlaps, puts hidden values on F.Fab, and stores all seven
  prototype footprint definitions in the project-local `BFM.pretty` library.
- Saves explicit minimum rules: 0.25 mm copper clearance, 0.25 mm track width,
  0.50 mm copper-to-edge clearance, and 0.15 mm silkscreen clearance. Routes use
  0.30 mm tracks. No DRC exclusions or severity suppressions were added.

Validated with KiCad 10.0.6: **0 violations and 0 unconnected items**.
The machine-readable report is `validation/drc.json`. Reproduce from this folder:

```powershell
kicad-cli pcb drc --refill-zones --format json --exit-code-violations --output validation/drc.json babys-first-midi.kicad_pcb
```

This remains the prototype experiment described in the earlier design work:
the connector footprints remain project-specific draft geometries. The clean
result verifies board geometry and connectivity against the PCB net assignments;
it does not certify the remaining connector fit, enclosure fit or schematic parity.

## Populated 3D view

In PCB Editor, use View > 3D Viewer (Alt+3). Models are attached to the board
and to the project footprint library. Resistors and MOSFETs use KiCad's standard
STEP models; install the KiCad 10 3D model library if these do not appear.
The RJ45 uses a drawing-based model. The WH148 pots and Tiny
2350 now use the bundled drawing-based replacement models. Their geometry,
source drawings and remaining estimates are documented in
`3dmodels/MECHANICAL_NOTES.md`.

The WH148 replacement changes the old 3 mm pitch to 5 mm, with 1.3 mm holes.
Pots mount directly, shafts parallel to the board toward the top edge. The Tiny
footprint's mirrored banks are corrected and the module is rotated and moved
to put USB at the right edge. Routing and ground fill are regenerated while
preserving all numbered pad-to-net assignments. KiCad 10.0.6 DRC reports zero
violations and zero unconnected items; see `validation/drc.json`.

J2 is now the uxcell PJ-320A, using a Keebio STEP model and adapted footprint.
The user-supplied pinout maps MIDI_TIP to pin 4 and MIDI_RING to pin 3; pins 1
(sleeve, as before) and 2 (ring2) are unconnected. The mouth faces the right
edge. See `3dmodels/MECHANICAL_NOTES.md` for source attribution and geometry
limits. The replacement is rerouted and passes DRC with no unconnected items.

J1 now uses BFM:RJ45_FMHXG_AssumedPinout and a drawing-based model, facing the
left edge. The 8 signal holes, 2 locating holes and 2 shield holes follow the
user-supplied drawing. Sequential 1-8 numbering is an explicit prototype
assumption approved by the user, not a verified vendor pinout. Existing numbered
signal nets are preserved; shield pads are unconnected. See
`RJ45_CONTINUITY_CHECK.md` for the precise mapping to check when the parts arrive.
Rerouting and ground refill pass KiCad 10.0.6 DRC: zero violations and zero
unconnected items.


## 2N7000 input buffers

Q1-Q5 now use through-hole 2N7000 MOSFETs with the onsemi 2N7000TA
TO-92 pinout: 1=source (GND), 2=gate (input resistor), 3=drain (GPIO/pull-up).
Datasheet: https://www.onsemi.com/download/data-sheet/pdf/2n7000ta-d.pdf
The local BFM:TO-92_2N7000_SGD footprint derives from KiCad's
TO-92_Inline_Wide footprint. Its 2.54 mm hole spacing requires spreading the
leads; match the flat face to the fabrication outline. The 3D model is the
standard KiCad 10 TO-92_Inline_Wide STEP model.

PCB nets and schematic connections were checked against the previous design
by gate/drain/source function, including the required pin-number remap.
KiCad 10.0.6 DRC reports zero violations and zero unconnected items.
This verifies layout connectivity, not operation with the toy's unmeasured
signal voltage. Verify input switching on the assembled prototype.
