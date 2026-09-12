# J1 prototype pinout assumption

Selected part: FMHXG RJ45NMCCFC-90D-10, Amazon B0BRQ2R8HW.
The user approved fitting and routing the connector before physical continuity
verification. Geometry follows the supplied component-side drawing. The related
CKMTW family is a reference, not proof of the FMHXG internal wiring.

Numbering is explicitly assumed sequentially across the staggered terminals:
component side viewed from above, connector mouth toward the TOP of this diagram.
This is not a pinout extracted from a verified FMHXG or CKMTW CAD library.

```text
                   MOUTH
       SH                       SH
           locating     locating

             2    4    6    8       nearer the mouth
          1    3    5    7          rear row
```

Coordinates in mm, origin at front mouth center, X right and Y toward rear:

| Assumed contact | X | Y | Board net |
|---|---:|---:|---|
| 1 | -4.445 | 16.79 | FPT_C |
| 2 | -3.175 | 14.25 | FPT_D |
| 3 | -1.905 | 16.79 | FPT_E |
| 4 | -0.635 | 14.25 | FPT_F |
| 5 | 0.635 | 16.79 | FPT_G |
| 6 | 1.905 | 14.25 | FPT_COMMON |
| 7 | 3.175 | 16.79 | Unconnected |
| 8 | 4.445 | 14.25 | Unconnected |

Both shield pads are unconnected. On the carrier the mouth faces LEFT; rotate
the diagram 90 degrees counterclockwise to match the board's top view.

Before PCB ordering, insert a numbered RJ45 breakout plug or known cable into
one loose jack. With a continuity meter, record which solder terminal connects
to each plug contact 1 through 8. Use the breakout's numbering; wire colors alone
can be misleading without knowing its wiring standard. Also check shield tabs
to metal shell, and test-fit the terminal, peg and shield-hole pattern at 1:1.
If the mapping differs, change the footprint numbering and reroute before
manufacture. The clean DRC report does not validate this physical assumption.
