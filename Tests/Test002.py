from machine import ADC
from time import sleep_ms

# Tiny 2350 analog inputs:
# A0 = GP26 / ADC0
# A1 = GP27 / ADC1
a0 = ADC(26)
a1 = ADC(27)

PRINT_INTERVAL_MS = 250


def voltage(raw):
    # MicroPython read_u16() scales the ADC result to 0..65535.
    # The Tiny 2350 ADC reference is nominally 3.3 V.
    return raw * 3.3 / 65535


print("Potentiometer test started")
print("Turn A0 and A1. Press Ctrl+C to stop.")
print()

while True:
    a0_raw = a0.read_u16()
    a1_raw = a1.read_u16()

    print(
        "A0: {:5d} ({:.2f} V)    A1: {:5d} ({:.2f} V)".format(
            a0_raw,
            voltage(a0_raw),
            a1_raw,
            voltage(a1_raw),
        )
    )

    sleep_ms(PRINT_INTERVAL_MS)
