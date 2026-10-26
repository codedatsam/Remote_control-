# TCL Android TV Remote Control

Control a TCL Smart TV (BeyondTV4, Android 11) over ADB.

## Setup

```bash
# 1. ADB must be on your PATH (already installed)
adb devices

# 2. Connect to the TV (same Wi-Fi network)
adb connect 192.168.0.90:5555

# 3. Accept the pairing prompt on the TV
```

## CLI Usage

```bash
python remote.py power          # toggle power
python remote.py volume_up      # volume up
python remote.py home            # go home
python remote.py launch netflix  # open Netflix
python remote.py type_text "hi"  # type text
python remote.py tap 960 540     # tap centre of screen
python remote.py screenshot      # grab screenshot
python remote.py current_app     # show focused app
python remote.py is_awake        # check if screen is on
python remote.py apps            # list known apps
python remote.py keys            # list all key names
```

## Python API

```python
from remote import TVRemote

tv = TVRemote("192.168.0.90:5555")

tv.power()
tv.volume_up()
tv.launch_app("netflix")
tv.up()
tv.ok()
tv.type_text("hello")
tv.screenshot("screen.png")
print(tv.current_app())
```

## Key Map

| Key | Code | | Key | Code |
|---|---|---|---|---|
| power | 26 | | dpad_center | 23 |
| home | 3 | | volume_up | 24 |
| back | 4 | | volume_down | 25 |
| menu | 82 | | volume_mute | 164 |
| dpad_up | 19 | | channel_up | 166 |
| dpad_down | 20 | | channel_down | 167 |
| dpad_left | 21 | | play_pause | 85 |
| dpad_right | 22 | | | |

## Installed Apps

| App | Package |
|---|---|
| netflix | com.netflix.ninja |
| youtube | com.google.android.youtube.tv |
| disney | com.disney.disneyplus |
| prime | com.amazon.amazonvideo.livingroom |
| rakuten | tv.wuaki.apptv |
| bbc | uk.co.freeview.bbc |
| itv | uk.co.freeview.itv |
| channel4 | uk.co.freeview.ch4_vod |
| channel5 | uk.co.freeview.ch5 |
| stan | au.com.stan.and |
| youtube_music | com.google.android.youtube.tvmusic |
| launcher | com.google.android.tvlauncher |
| browser | com.tcl.browser |
| gallery | com.tcl.gallery |
| assistant | com.google.android.tv.assistant |

## TV Details

| Property | Value |
|---|---|
| IP | 192.168.0.90:5555 |
| Brand | TCL |
| Model | Smart TV (BeyondTV4) |
| Android | 11 (SDK 30) |
| Screen | 1920x1080 @ 320dpi |
| Chipset | Realtek rtd288o |
