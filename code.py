import terminalio
import displayio
import adafruit_ili9341
import digitalio
import gc
import busio
import time
import board
from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font
import adafruit_connection_manager
import wifi
import socketpool
import adafruit_requests
import rtc_time_util
import rtc
from digitalio import DigitalInOut, Direction
import microcontroller
import watchdog
import random

# Setup WiFi and Timezone
WIFI_SSID = ''
WIFI_PASSWORD = ''
TIMEZONE = ''

# Define the repository name
REPO_NAME = "adafruit/circuitpython"

# Get count of open issues
issue_count_url = "https://api.github.com/search/issues?q=repo:" + REPO_NAME + "+is:issue+state:open&per_page=1"

# Get count of open pull requests
pr_count_url = "https://api.github.com/search/issues?q=repo:" + REPO_NAME + "+is:pull-request+state:open&per_page=1"

# Get details of latest activity
last_activity_url = "https://api.github.com/repos/" + REPO_NAME + "/activity?per_page=1"

# Get details of latest release
latest_release = "https://api.github.com/repos/" + REPO_NAME + "/releases?per_page=1&pages=1"

# Release any resources currently in use for the displays
displayio.release_displays()
TFT_WIDTH = 320
TFT_HEIGHT = 240
LANDSCAPE = 1
ORIENTATION = LANDSCAPE

# Time between updates
# 900 = 15 mins, 1800 = 30 mins, 3600 = 1 hour
sleep_time = 900

backlight = digitalio.DigitalInOut(board.LCD_BCKL)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = 1

spi = busio.SPI(board.LCD_SCK, MISO=board.LCD_MISO, MOSI=board.LCD_MOSI)
display_bus = displayio.FourWire(spi, command=board.LCD_DC, chip_select=board.LCD_CS)
display = adafruit_ili9341.ILI9341(display_bus, width=320, height=240)
#display = board.DISPLAY

if sleep_time < 60:
    sleep_time_conversion = "seconds"
    sleep_int = sleep_time
elif 60 <= sleep_time < 3600:
    sleep_int = sleep_time / 60
    sleep_time_conversion = "minutes"
elif sleep_time >= 3600:
    sleep_int = sleep_time / 60 / 60
    sleep_time_conversion = "hours"
else:
    sleep_int = sleep_time
    sleep_time_conversion = "seconds"

# Define text colours
text_red = 0xFF0000
text_green = 0x00FF00
text_yellow = 0xFFFF00
text_blue = 0x0000FF
text_magenta = 0xFF00FF
text_cyan = 0x00FFFF
text_white = 0xFFFFFF
text_black = 0x000000

# Define the date and time formatting
def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mday,
        datetime.tm_mon,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

def _format_date(datetime):
    return "{:02}/{:02}/{:02}".format(
        datetime.tm_year,
        datetime.tm_mon,
        datetime.tm_mday,
    )

def _format_time(datetime):
    return "{:02}:{:02}:{:02}".format(
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

# Load the font
font = bitmap_font.load_font("fonts/teletext_7.bdf", displayio.Bitmap)

# Define the line spacing in pixels
start_position = 24

# Individual customizable position labels
# https://learn.adafruit.com/circuitpython-display-support-using-displayio/text
# Labels and Data
date_label = label.Label(font)
date_label.anchor_point = (0.0, 0.0)
date_label.anchored_position = (168, 5)
date_label.scale = 1
date_label.color = text_green

time_label = label.Label(font)
time_label.anchor_point = (0.0, 0.0)
time_label.anchored_position = (256, 5)
time_label.scale = 1
time_label.color = text_green

page_data = label.Label(font)
page_data.anchor_point = (0.0, 0.0)
page_data.anchored_position = (5, 5)
page_data.scale = 1
page_data.color = text_white

title_data = label.Label(font)
title_data.anchor_point = (0.0, 0.0)
title_data.anchored_position = (64, 5)
title_data.scale = 1
title_data.color = text_yellow

page_rotator = label.Label(font)
page_rotator.anchor_point = (0.0, 0.0)
page_rotator.anchored_position = (117, 5)
page_rotator.scale = 1
page_rotator.color = text_white

repo_title = label.Label(font)
repo_title.anchor_point = (0.0, 0.0)
repo_title.anchored_position = (5, start_position)
repo_title.scale = 1
repo_title.color = text_blue

repo_data = label.Label(font)
repo_data.anchor_point = (0.0, 0.0)
repo_data.anchored_position = (117, start_position)
repo_data.scale = 1
repo_data.color = text_white

release_version_label = label.Label(font)
release_version_label.anchor_point = (0.0, 0.0)
release_version_label.anchored_position = (5, start_position * 2)
release_version_label.scale = 1
release_version_label.color = text_blue

release_version_data = label.Label(font)
release_version_data.anchor_point = (0.0, 0.0)
release_version_data.anchored_position = (117, start_position * 2)
release_version_data.scale = 1
release_version_data.color = text_white

release_date_label = label.Label(font)
release_date_label.anchor_point = (0.0, 0.0)
release_date_label.anchored_position = (5, start_position * 3)
release_date_label.scale = 1
release_date_label.color = text_blue

release_date_data = label.Label(font)
release_date_data.anchor_point = (0.0, 0.0)
release_date_data.anchored_position = (117, start_position * 3)
release_date_data.scale = 1
release_date_data.color = text_white

issue_title = label.Label(font)
issue_title.anchor_point = (0.0, 0.0)
issue_title.anchored_position = (5, start_position * 4)
issue_title.scale = 1
issue_title.color = text_blue

issue_data = label.Label(font)
issue_data.anchor_point = (0.0, 0.0)
issue_data.anchored_position = (117, start_position * 4)
issue_data.scale = 1
issue_data.color = text_green

pr_title = label.Label(font)
pr_title.anchor_point = (0.0, 0.0)
pr_title.anchored_position = (5, start_position * 5)
pr_title.scale = 1
pr_title.color = text_blue

pr_data = label.Label(font)
pr_data.anchor_point = (0.0, 0.0)
pr_data.anchored_position = (117, start_position * 5)
pr_data.scale = 1
pr_data.color = text_green

last_activity_time_title = label.Label(font)
last_activity_time_title.anchor_point = (0.0, 0.0)
last_activity_time_title.anchored_position = (5, start_position * 6)
last_activity_time_title.scale = 1
last_activity_time_title.color = text_blue

last_activity_time_data = label.Label(font)
last_activity_time_data.anchor_point = (0.0, 0.0)
last_activity_time_data.anchored_position = (117, start_position * 6)
last_activity_time_data.scale = 1
last_activity_time_data.color = text_white

last_actor_title = label.Label(font)
last_actor_title.anchor_point = (0.0, 0.0)
last_actor_title.anchored_position = (5, start_position * 7)
last_actor_title.scale = 1
last_actor_title.color = text_blue

last_actor_data = label.Label(font)
last_actor_data.anchor_point = (0.0, 0.0)
last_actor_data.anchored_position = (117, start_position * 7)
last_actor_data.scale = 1
last_actor_data.color = text_white

# Load Bitmap to tile grid first (Background layer)
DiskBMP = displayio.OnDiskBitmap("/images/background.bmp")
tile_grid = displayio.TileGrid(
    DiskBMP,
    pixel_shader=DiskBMP.pixel_shader,
    width=1,
    height=1,
    tile_width=320,
    tile_height=240
    )

# Create subgroups
text_group = displayio.Group()
text_group.append(tile_grid)
main_group = displayio.Group()

# Add subgroups to main display group
main_group.append(text_group)

# Label Display Group (foreground layer)
text_group.append(date_label)
text_group.append(time_label)
text_group.append(page_data)
text_group.append(title_data)
text_group.append(repo_title)
text_group.append(repo_data)
text_group.append(release_version_label)
text_group.append(release_version_data)
text_group.append(release_date_label)
text_group.append(release_date_data)
text_group.append(issue_title)
text_group.append(issue_data)
text_group.append(pr_title)
text_group.append(pr_data)
text_group.append(last_activity_time_title)
text_group.append(last_activity_time_data)
text_group.append(last_actor_title)
text_group.append(last_actor_data)
text_group.append(page_rotator)
display.root_group = main_group

# Connect to Wi-Fi
print("\n===============================")
print("Connecting to WiFi...")
pool = adafruit_connection_manager.get_radio_socketpool(wifi.radio)
ssl_context = adafruit_connection_manager.get_radio_ssl_context(wifi.radio)
requests = adafruit_requests.Session(pool, ssl_context)

while not wifi.radio.ipv4_address:
    try:
        wifi.radio.enabled = False
        wifi.radio.enabled = True
        wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
        print("Connected!\n")
    except ConnectionError as e:
        print("Connection Error:", e)
        print("Resetting in 10 seconds")
        time.sleep(10)
        microcontroller.reset()

# Get the NTP and commit to RTC
try:
    rtc_time_util.set_local_time_in_rtc(rtc, pool, ntp_server="192.168.0.80", timezone_offset=0)
except ConnectionError as e:
    print("Connection Error:", e)
    print("Resetting in 10 seconds")
    time.sleep(10)
    microcontroller.reset()

# Define the variables uses
time_last = 0
release_version = ''
release_date = ''
issue_count = 0
pr_count = 0
activity_time = ''
activity_name = ''
page_number_min = 100
page_number_max = 999

# Setup the watchdog
wdt = microcontroller.watchdog
wdt.timeout = 15
wdt.mode = watchdog.WatchDogMode.RESET

# Define the primary function
def do_main_update():
    gc.collect()
    global time_last, issue_count, pr_count, activity_time, activity_name, release_version, release_date
    try:
        print("Attempting to get data from github")
        print("\n===============================")
        issue_response = requests.get(issue_count_url).json()
        issue_count = issue_response['total_count']
        
        pr_response = requests.get(pr_count_url).json()
        pr_count = pr_response['total_count']
        
        activity_response = requests.get(last_activity_url).json()
        activity_time = activity_response[0]["timestamp"]
        activity_name = activity_response[0]["actor"]["login"]

        release_response = requests.get(latest_release).json()
        release_version = release_response[0]["tag_name"]
        release_date = release_response[0]["published_at"]
        
        time_last = time.monotonic()
        wdt.feed()

    except (ValueError, RuntimeError) as e:
        print("Failed to get data:", e)
        print("Resetting in 10 seconds")
        time.sleep(10)
        microcontroller.reset()

    except ConnectionError as e:
        print("Connection Error:", e)
        print("Resetting in 10 seconds")
        time.sleep(10)
        microcontroller.reset()

# The main loop
while True:
    gc.collect()
    if time_last == 0:
        print("running first time")
        do_main_update()
        page_data.text = "P100"
        title_data.text = "CPTEXT"
        repo_title.text = "GITHUB REPO:"
        repo_data.text = REPO_NAME
        release_version_label.text = "RELEASE VER:"
        release_version_data.text = release_version
        release_date_label.text = "RELEASE DATE:"
        release_date_data.text = release_date
        issue_title.text = "ISSUE COUNT:"
        issue_data.text = str(issue_count)
        pr_title.text = "PR COUNT:"
        pr_data.text = str(pr_count)
        last_activity_time_title.text = "ACTIVITY:"
        last_activity_time_data.text = activity_time
        last_actor_title.text = "UPDATE BY:"
        last_actor_data.text = activity_name
        page_rotator.text = "P" + str(random.randint(page_number_min, page_number_max))
    wdt.feed()
    if time.monotonic() > time_last + sleep_time:
        do_main_update()
        page_data.text = "P100"
        title_data.text = "CPTEXT"
        repo_title.text = "GITHUB REPO:"
        repo_data.text = REPO_NAME
        release_version_label.text = "RELEASE VER:"
        release_version_data.text = release_version
        release_date_label.text = "RELEASE DATE:"
        release_date_data.text = release_date
        issue_title.text = "ISSUE COUNT:"
        issue_data.text = issue_count
        pr_title.text = "PR COUNT:"
        pr_data.text = str(pr_count)
        last_activity_time_title.text = "ACTIVITY:"
        last_activity_time_data.text = activity_time
        last_actor_title.text = "UPDATE BY:"
        last_actor_data.text = activity_name
        page_rotator.text = "P" + str(random.randint(page_number_min, page_number_max))
    else:
        response = None
        page_data.text = "P100"
        title_data.text = "CPTEXT"
        repo_title.text = "GITHUB REPO:"
        issue_title.text = "ISSUE COUNT:"
        release_version_label.text = "RELEASE VER:"
        release_date_label.text = "RELEASE DATE:"
        pr_title.text = "PR COUNT:"
        last_activity_time_title.text = "ACTIVITY:"
        last_actor_title.text = "UPDATE BY:"
        page_rotator.text = "P" + str(random.randint(page_number_min, page_number_max))
        current_unix_time = rtc.RTC().datetime
        current_struct_time = time.struct_time(current_unix_time)
        current_date = "{}".format(_format_date(current_struct_time))
        current_time = "{}".format(_format_time(current_struct_time))
        date_label.text = current_date
        time_label.text = current_time
        wdt.feed()
