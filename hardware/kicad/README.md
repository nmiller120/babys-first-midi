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
The RJ45 and TRS jack still use illustrative models. The WH148 pots and Tiny
2350 now use the bundled drawing-based replacement models. Their geometry,
source drawings and remaining estimates are documented in
`3dmodels/MECHANICAL_NOTES.md`.

The WH148 replacement changes the old 3 mm pitch to 5 mm, with 1.3 mm holes.
Pots mount directly, shafts parallel to the board toward the top edge. The Tiny
footprint's mirrored banks are corrected and the module is rotated and moved
to put USB at the right edge. Routing and ground fill are regenerated while
preserving all numbered pad-to-net assignments. KiCad 10.0.6 DRC reports zero
violations and zero unconnected items; see `validation/drc.json`.
