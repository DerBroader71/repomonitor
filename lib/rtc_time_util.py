import time
import adafruit_ntp

# Define your timezone offset and BST rules for the UK
timezone_offset = 0  # GMT offset
bst_start_month = 3  # BST starts in March
bst_end_month = 10  # BST ends in October

def should_use_bst(year, month, day):
    # Check if the given date is within the BST period
    if month > bst_start_month and month < bst_end_month:
        return True
    elif month == bst_start_month and month == bst_end_month:
        # BST starts on the last Sunday in March and ends on the last Sunday in October
        # Calculate the last Sunday in March and October
        last_sunday_march = 31 - (time.localtime(time.mktime((year, month, 31, 0, 0, 0, 0, 0, -1)))[6])
        last_sunday_october = 31 - (time.localtime(time.mktime((year, month, 31, 0, 0, 0, 0, 0, -1)))[6])

        if (month == bst_start_month and day >= last_sunday_march) or (month == bst_end_month and day < last_sunday_october):
            return True

    return False

def set_local_time_in_rtc(rtc, pool, ntp_server="pool.ntp.org", timezone_offset=0):
    # Create an NTP client
    #ntp = adafruit_ntp.NTP(pool, ntp_server, tz_offset=0)
    ntp = adafruit_ntp.NTP(pool, server='uk.pool.ntp.org', tz_offset=0)

    # Get the current UTC time from the NTP server
    #utc_time = ntp.datetime
    utc_time = time.struct_time(ntp.datetime)
    
    # Get the current year, month, day
    year, month, day, _, _, _, _, _, _ = utc_time

    # Calculate whether to use BST
    use_bst = should_use_bst(year, month, day)

    # Apply timezone offset and BST if necessary
    local_time = time.mktime(utc_time) + (timezone_offset * 3600)
    if use_bst:
        local_time += 3600  # Add 1 hour for BST

    # Set the local time and BST flag in the RTC
    rtc.RTC().datetime = time.struct_time(time.localtime(local_time))

def get_local_time_from_rtc(rtc):
    # Read the local time from the RTC
    rtc_time = rtc.datetime
    return time.mktime(rtc_time)
