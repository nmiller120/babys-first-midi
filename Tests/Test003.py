"""SSD1306 128x64 I2C OLED bench test for the Pimoroni Tiny 2350.

Wire by the display's printed labels (header order can vary):
GND -> GND, VCC -> 3V3, SDA -> GP6, SCL -> GP7.
Copy the bundled ssd1306.py to the Tiny's /lib directory, then run this
file in Thonny. Press Ctrl+C to stop and blank the display.
"""

from machine import SoftI2C, Pin
from time import sleep_ms

try:
    from ssd1306 import SSD1306_I2C
except ImportError:
    raise ImportError("Copy Tests/ssd1306.py to /lib/ssd1306.py on the Tiny first.")

WIDTH = 128
HEIGHT = 64
SDA_PIN = 6
SCL_PIN = 7
I2C_FREQ = 100_000


def main():
    print("Test003: SSD1306 OLED (SoftI2C) on GP6 (SDA), GP7 (SCL)")
    i2c = SoftI2C(sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=I2C_FREQ)
    sleep_ms(100)
    devices = i2c.scan()
    print("I2C addresses:", [hex(address) for address in devices])
    addresses = [address for address in (0x3C, 0x3D) if address in devices]
    if not addresses:
        print("No OLED found at 0x3C or 0x3D.")
        print("Check 3V3, GND, SDA -> GP6 and SCL -> GP7, then run again.")
        return

    address = addresses[0]
    if len(addresses) > 1:
        print("Both OLED addresses respond; using 0x3C.")
    oled = SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=address)
    oled.contrast(128)
    print("OLED responding at", hex(address))
    print("Look for Hello world! and a changing count. Ctrl+C stops the test.")

    count = 0
    try:
        while True:
            oled.fill(0)
            oled.text("Hello world!", 0, 0)
            oled.text("Baby's First", 0, 16)
            oled.text("MIDI - Test003", 0, 26)
            oled.text("I2C: " + hex(address), 0, 40)
            oled.text("Count: {}".format(count), 0, 54)
            oled.show()
            count = (count + 1) % 1000000
            sleep_ms(1000)
    except KeyboardInterrupt:
        oled.fill(0)
        oled.show()
        print("OLED test stopped.")


if __name__ == "__main__":
    main()
