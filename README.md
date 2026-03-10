# Dual Plant Soil Moisture Monitoring System (Raspberry Pi Pico W)

## System Overview

![20260305_155508](https://github.com/user-attachments/assets/2142b0f3-5f3c-4b55-b210-5049b058822e)

This project monitors the soil moisture of two plant pots using capacitive soil sensors connected to a Raspberry Pi Pico W.

Each plant has a status indicator using LEDs and the system displays the current moisture state on an LCD screen.

## Soil Moisture Sensor

![20260305_155458](https://github.com/user-attachments/assets/edf72077-3222-46b8-adb7-d6e0d2812bef)

Capacitive soil moisture sensor placed in the plant pot to measure the moisture level of the soil.

## LCD Status Display

![20260305_155516](https://github.com/user-attachments/assets/83e991e1-e834-4ecd-8eda-55b7aaeaf841)

The LCD screen displays the current soil moisture status for both plant pots. The system categorizes the soil as Dry, OK, or Wet.

## Electronics Close Up

![20260307_134032](https://github.com/user-attachments/assets/14eb76ff-42b9-467f-aef0-59a027cf580c)

Close-up of the electronics on the breadboard including wiring of the two sensors, LCD,
Raspberry Pi Pico W, LEDs and the buzzer.

## Software 

The project is written in MicroPython and runs on the Raspberry Pi Pico W.

Main features:

- Reads soil moisture from the two capacitive I2C sensors
- Displays plant status on the LCD screen
- Indicates soil condition using the LEDs
- Triggers a buzzer when the soil becomes too dry
- Prints sensor data to the serial terminal for debugging

## Hardware

The system is built using the following components:

- Raspberry Pi Pico W 
- 2x Capacitive Soil Moisture Sensors (Seesaw I2C)
- 2x Adaptercable 4-pol JST-PH to 4x dupont female 200mm
- 16x2 LCD Display with I2C backpack
- 6x LEDs (status indicators), RED= DRY, YELLOW = OK, BLUE = WET
- 1x Active buzzer
- 1x Breadboard
- 26x Jumper wires
- 1x USB-cable A-male to micro B male

## Wiring Diagram

<img width="1024" height="576" alt="Raspberry_pi_pico_w_pinout-1-1024x576" src="https://github.com/user-attachments/assets/91dd4b81-a0a1-4fae-92fb-ebea0b97bd56" />

<img width="3012" height="1740" alt="moisture_tracking_system_bb" src="https://github.com/user-attachments/assets/6fa65e25-7c38-4559-8b72-c534a8eefbc4" />

This image demonstrates how the components are connected to the Raspberry Pi Pico W. The LCD and one soil moisture sensor share the same SDA and SCL pins because they operate on the same I2C bus, while the second sensor runs on a separate I2C bus. I noticed that both of the sensors cannot be running on the same bus, otherwise their addresses will collide with each other. I also included an image of the GPIO's for the Pico W that you can use as navigation when connecting the hardware, follow the steps bellow: 

### Power the Pico W

Computer -> USB Micro Male -> Pico W

### Soil Moisture Sensor 1

(I2C-bus 0)

Sensor Pin	    Pico W Pin

- VCC	    ->     3.3V
- GND	    ->     GND
- SDA	    ->     GP4
- SCL	    ->     GP5

#### Soil Moisture Sensor 2

(I2C-bus 1)

Sensor Pin	   Pico W Pin

- VCC	   ->     3.3V
- GND	   ->     GND
- SDA	   ->     GP2
- SCL      ->  	  GP3

### LCD 16x2 (I2C)

LCD shares with the second sensor on bus 1.

LCD Pin	       Pico W Pin

- VCC	   ->     3.3V
- GND	   ->     GND
- SDA	   ->     GP2
- SCL	   ->     GP3

### LED Status Indicators

Every pot has three LEDs.

Plant 1 LEDs

LED Color	       Pico Pin

- Red (Dry)	     ->   GP14
- Yellow (OK)	 ->   GP15
- Blue (Wet)	 ->   GP16

Plant 2 LEDs

LED Color	       Pico Pin

- Red (Dry)      ->	   GP17
- Yellow (OK)	 ->    GP18
- Blue (Wet)	 ->    GP19

### ⚠️ Obs! dont forget

Every LED should be connected like this:

GPIO → resistor (220–330Ω) → LED → GND

Short leg of the LED → GND

### Connect the Buzzer

Buzzer Pin	  Pico Pin

 -   +	     ->    GP21
 -   -      ->    GND

### I2C Buses 

Bus	       GPIO

- I2C0	->   GP4 (SDA), GP5 (SCL)
- I2C1	->   GP2 (SDA), GP3 (SCL)

## Get Started

Clone the repository:

```bash
git clone https://github.com/Gabbemannen00/soil-moisture-tracking-system.git
cd soil-moisture-tracking-system
```
Install MicroPython on the Raspberry Pi Pico W

1. Download the MicroPython firmware from: https://micropython.org/download/RPI_PICO_W/
2. Hold the BOOTSEL button before connecting the Pico W to your computer
3. When Pico W is connected copy the .uf2 file to the Pico W storage device

Install the IDE and configure the Raspberry Pi Pico W

1. Download Thonny from here: https://thonny.org/
2. Click on "interpreter" and choose "MicroPython (Raspberry Pi Pico)"
3. Select the current port that your Pico W is connected to, for example COM5, if the port is not visible try click on "try to detect port automatically"
4. Upload the file "main.py" to the Raspberry Pi Pico W

Run the system 

Once powered, the system will:
* Blink LED's and sound buzzer on startup
* Read soil moisture from both sensors
* Display the moisture status on the LCD
* Show soil condition using LEDs
* Trigger a buzzer warning if soil becomes too dry





