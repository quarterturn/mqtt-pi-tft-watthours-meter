# mqtt-pi-tft-watthours-meter
A python & pygame script to calculate and display electricity costs for the home.
Receives watthours data from an in-house broker via paho.mqtt library.
Calculates daily and monthly costs based on base rate and watthours costs from electric company.
Watthours info is gathered from the meter by reading an IR diode pulse. Each pulse is one watthour.

It is possible to read my particular meter via a DTV dongle, but some of the channels used are outside the tuning range, so somee readings would me missed. The IR diode method is more accurate.
