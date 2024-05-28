# repomonitor  
Repository monitor using Sunton ESP32-2432S028R and CircuitPython in the style of Teletext - Ceefax, Oracle, etc  

Uses the following libraries:  
terminalio, displayio, adafruit_ili9341, digitalio, gc, busio, time, board, adafruit_display_text, adafruit_bitmap_font, adafruit_connection_manager, wifi, socketpool, adafruit_requests, rtc_time_util, rtc, digitalio, microcontroller, watchdog, random  

Edit code.py and set your SSID, password, TimeZone (ie Europe/London) and the Github repository to monitor (ie adafruit/circuitpython)  

TODO:  
Add logic checking to ensure required data is populated or ignored if not available.  
Add screenshot  

Original teletext font can be found here: https://galax.xyz/TELETEXT/  
