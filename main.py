from machine import Pin, I2C
import time

# --- Sensor1 on I2C0 (GP4/GP5) ---
i2c_sensor1 = I2C(0, sda=Pin(4), scl=Pin(5), freq=50000)

# --- LCD & sensor2 on I2C1 (GP2/GP3) ---
i2c_sensor2_lcd = I2C(1, sda=Pin(2), scl=Pin(3), freq=50000)

SENSOR_ADDR = 0x36 # Moisture sensors prints as 54 
LCD_ADDR = 0x27  # LCD prints as 39 

print("Sensor 1 bus 0 scan:", i2c_sensor1.scan())
print("Sensor 2 bus 1 scan", i2c_sensor2_lcd.scan())

# ---------------- LCD 1602 via PCF8574 ----------------
# Bitmapping for this 1602 I2C-backpack:
# P0=RS, P1=RW, P2=E, P3=Backlight, P4..P7=D4..D7
RS = 0x01
RW = 0x02
E  = 0x04
BL = 0x08

class LCD1602_I2C:
    def __init__(self, i2c, addr, cols=16, rows=2):
        self.i2c = i2c
        self.addr = addr
        self.cols = cols
        self.rows = rows
        self.backlight = BL
        self._init_lcd()

    def _write_byte(self, data):
        self.i2c.writeto(self.addr, bytes([data | self.backlight]))

    def _pulse_enable(self, data):
        self._write_byte(data | E)
        time.sleep_us(1)
        self._write_byte(data & ~E)
        time.sleep_us(50)

    def _write4bits(self, nibble, mode):
        data = (nibble & 0xF0) | self.backlight | mode
        self._write_byte(data)
        self._pulse_enable(data)

    def _send(self, value, mode):
        high = value & 0xF0
        low  = (value << 4) & 0xF0
        self._write4bits(high, mode)
        self._write4bits(low, mode)

    def command(self, cmd):
        self._send(cmd, 0)

    def write_char(self, ch):
        self._send(ch, RS)

    def clear(self):
        self.command(0x01)
        time.sleep_ms(2)

    def home(self):
        self.command(0x02)
        time.sleep_ms(2)

    def set_cursor(self, row, col):
        # rad 0: 0x00, rad 1: 0x40
        offsets = [0x00, 0x40, 0x14, 0x54]
        self.command(0x80 | (offsets[row] + col))

    def print(self, text):
        for c in text:
            self.write_char(ord(c))

    def _init_lcd(self):
        time.sleep_ms(50)

        # Init 4-bit mode
        self._write4bits(0x30, 0)
        time.sleep_ms(5)
        self._write4bits(0x30, 0)
        time.sleep_us(150)
        self._write4bits(0x30, 0)
        self._write4bits(0x20, 0)

        # Function set: 4-bit, 2 line, 5x8
        self.command(0x28)
        # Display on, cursor off, blink off
        self.command(0x0C)
        # Entry mode set: increment
        self.command(0x06)
        self.clear()

lcd = LCD1602_I2C(i2c_sensor2_lcd, LCD_ADDR)

def read_moisture(i2c_bus):
    i2c_bus.writeto(SENSOR_ADDR, bytes([0x0F, 0x10]))
    time.sleep_ms(50)
    d = i2c_bus.readfrom(SENSOR_ADDR, 2)
    return (d[0] << 8) | d[1]

def fmt5(n):
    s = str(n) + "     "
    return s[:5]

def get_status(m):
    if m < 500:
        return "Torr  "
    elif m < 800:
        return "OK  "
    else:
        return "Fuktig  "

# --- Plant 1 LEDs ---
p1_red = Pin(14, Pin.OUT)
p1_yellow = Pin(15, Pin.OUT)
p1_blue = Pin(16, Pin.OUT)

# --- Plant 2 LEDs ---
p2_red = Pin(17, Pin.OUT)
p2_yellow = Pin(18, Pin.OUT)
p2_blue = Pin(19, Pin.OUT)

buzzer = Pin(21, Pin.OUT)
 
def update_leds(m, red, yellow, blue):
    # Start as off
    red.off()
    yellow.off()
    blue.off()
    
    if m < 500:
        red.on()
        yellow.off()
        blue.off()
        #print("Red")
    elif m < 800:
        yellow.on()
        red.off()
        blue.off()
        #print("Yellow")
    else:
        blue.on()
        yellow.off()
        red.off()
        #print("Green")

# Turn all LED's OFF at once 
def leds_off():
    p1_red.off()
    p1_yellow.off()
    p1_blue.off()
    
    p2_red.off()
    p2_yellow.off()
    p2_blue.off()
    
# Turn all LED's ON at once
def leds_on():
    p1_red.on()
    p1_yellow.on()
    p1_blue.on()
    
    p2_red.on()
    p2_yellow.on()
    p2_blue.on()

# start the LED's as OFF
leds_off()
lcd.clear()
lcd.set_cursor(0, 0); lcd.print("Fuktsensorerna")
lcd.set_cursor(1, 0); lcd.print("startar upp...")
print("Starting LEDS...")
    
for x in range(5):
    buzzer.on()   # Buzzer sounds repeatedly on startup 
    time.sleep(0.2)
    buzzer.off()
    time.sleep(0.1)
    leds_on()
    time.sleep(0.2)
    leds_off()
    time.sleep(0.1)



# Layout one time
lcd.clear()
lcd.set_cursor(0, 0); lcd.print("Kruka 1:")
lcd.set_cursor(1, 0); lcd.print("Kruka 2:")

while True:
    try:
        # Read the sensors
        m1 = read_moisture(i2c_sensor1)
        m2 = read_moisture(i2c_sensor2_lcd)
        
        # Update LEDs
        update_leds(m1, p1_red, p1_yellow, p1_blue)
        update_leds(m2, p2_red, p2_yellow, p2_blue)
        
        # Print status on the LCD
        # --- Plant 1 ---
        lcd.set_cursor(0, 10)
        lcd.print(get_status(m1))
        
        # --- Plant 2 ---
        lcd.set_cursor(1, 10)
        lcd.print(get_status(m2))
        
        # Formated and columnadjusted printing with status (structured)
        print("P1:%4d %-3s | P2:%4d %-3s" %
              (m1, get_status(m1), m2, get_status(m2)))
        
    except OSError as e:
        print("I2C error:", e)
        lcd.clear()
        lcd.set_cursor(0, 0)
        lcd.print("I2C ERROR")
        lcd.set_cursor(1, 0)
        lcd.print("check addr/wire")

    time.sleep(2)
