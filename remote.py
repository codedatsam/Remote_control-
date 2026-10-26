"""
TCL Android TV Remote Control via ADB
Sends key events, launches apps, takes screenshots, and reads TV state.
"""

import subprocess
import time
from pathlib import Path

# ── Key event codes (Android KeyEvent) ──────────────────────────────
KEYCODES = {
    "power": 26,
    "home": 3,
    "back": 4,
    "menu": 82,
    "volume_up": 24,
    "volume_down": 25,
    "volume_mute": 164,
    "dpad_up": 19,
    "dpad_down": 20,
    "dpad_left": 21,
    "dpad_right": 22,
    "dpad_center": 23,          # OK / Select
    "channel_up": 166,
    "channel_down": 167,
    "play_pause": 85,
    "play": 126,
    "pause": 127,
    "stop": 86,
    "next": 87,
    "previous": 88,
    "rewind": 89,
    "fast_forward": 90,
    "1": 8, "2": 9, "3": 10,
    "4": 11, "5": 12, "6": 13,
    "7": 14, "8": 15, "9": 16,
    "0": 7,
    "info": 165,                 # display info / EPG
    "guide": 172,               # EPG guide
    "red": 183,
    "green": 184,
    "yellow": 185,
    "blue": 186,
    "caption": 175,
    "settings": 176,
    "enter": 66,
    "del": 67,
    "space": 62,
}

# ── Installed apps on this TV ───────────────────────────────────────
APPS = {
    "netflix": "com.netflix.ninja",
    "youtube": "com.google.android.youtube.tv",
    "disney": "com.disney.disneyplus",
    "prime": "com.amazon.amazonvideo.livingroom",
    "rakuten": "tv.wuaki.apptv",
    "bbc": "uk.co.freeview.bbc",
    "itv": "uk.co.freeview.itv",
    "channel4": "uk.co.freeview.ch4_vod",
    "channel5": "uk.co.freeview.ch5",
    "uktv": "uk.co.freeview.uktv",
    "stan": "au.com.stan.and",
    "tv_settings": "com.android.tv.settings",
    "tcl_home": "com.tcl.tv.tclhome_passive",
    "tcl_tv": "com.tcl.tv",
    "launcher": "com.google.android.tvlauncher",
    "browser": "com.tcl.browser",
    "gallery": "com.tcl.gallery",
    "mediacenter": "com.tcl.ui_mediaCenter",
    "youtube_music": "com.google.android.youtube.tvmusic",
    "google_play": "com.android.vending",
    "assistant": "com.google.android.tv.assistant",
    "settings": "com.tcl.settings",
    "smartconnect": "com.google.android.apps.nbu.smartconnect.tv",
    "freeview_explore": "uk.co.freeview.explore",
    "bbc_sounds": "uk.co.freeview.bbc_sounds",
}


class TVRemote:
    """Control a TCL Android TV over ADB (network or USB)."""

    def __init__(self, device: str = "192.168.0.90:5555", adb_path: str = "adb"):
        self.device = device
        self.adb = adb_path

    # ── low-level ───────────────────────────────────────────────────
    def _shell(self, cmd: str, timeout: int = 10) -> str:
        """Run a shell command on the TV and return stdout."""
        full = [self.adb, "-s", self.device, "shell", cmd]
        r = subprocess.run(full, capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise RuntimeError(f"ADB error: {r.stderr.strip()}")
        return r.stdout.strip()

    def _keyevent(self, code: int):
        """Send a single key event."""
        self._shell(f"input keyevent {code}")

    # ── power / navigation ──────────────────────────────────────────
    def power(self):
        """Toggle power (standby)."""
        self._keyevent(KEYCODES["power"])

    def home(self):
        self._keyevent(KEYCODES["home"])

    def back(self):
        self._keyevent(KEYCODES["back"])

    def menu(self):
        self._keyevent(KEYCODES["menu"])

    def ok(self):
        """DPAD center / Select."""
        self._keyevent(KEYCODES["dpad_center"])

    def up(self):
        self._keyevent(KEYCODES["dpad_up"])

    def down(self):
        self._keyevent(KEYCODES["dpad_down"])

    def left(self):
        self._keyevent(KEYCODES["dpad_left"])

    def right(self):
        self._keyevent(KEYCODES["dpad_right"])

    # ── volume ──────────────────────────────────────────────────────
    def volume_up(self):
        self._keyevent(KEYCODES["volume_up"])

    def volume_down(self):
        self._keyevent(KEYCODES["volume_down"])

    def mute(self):
        self._keyevent(KEYCODES["volume_mute"])

    # ── channels ────────────────────────────────────────────────────
    def channel_up(self):
        self._keyevent(KEYCODES["channel_up"])

    def channel_down(self):
        self._keyevent(KEYCODES["channel_down"])

    # ── media playback ──────────────────────────────────────────────
    def play_pause(self):
        self._keyevent(KEYCODES["play_pause"])

    def play(self):
        self._keyevent(KEYCODES["play"])

    def pause(self):
        self._keyevent(KEYCODES["pause"])

    def stop(self):
        self._keyevent(KEYCODES["stop"])

    def next_track(self):
        self._keyevent(KEYCODES["next"])

    def prev_track(self):
        self._keyevent(KEYCODES["previous"])

    def rewind(self):
        self._keyevent(KEYCODES["rewind"])

    def fast_forward(self):
        self._keyevent(KEYCODES["fast_forward"])

    # ── colour buttons ──────────────────────────────────────────────
    def red(self):
        self._keyevent(KEYCODES["red"])

    def green(self):
        self._keyevent(KEYCODES["green"])

    def yellow(self):
        self._keyevent(KEYCODES["yellow"])

    def blue(self):
        self._keyevent(KEYCODES["blue"])

    # ── text input ──────────────────────────────────────────────────
    def type_text(self, text: str):
        """Type a string into the focused field."""
        # Escape spaces and special chars for shell
        safe = text.replace(" ", "%s").replace("&", "\\&").replace("<", "\\<").replace(">", "\\>")
        self._shell(f"input text {safe}")

    # ── touch / swipe ───────────────────────────────────────────────
    def tap(self, x: int, y: int):
        """Tap at screen coordinates."""
        self._shell(f"input tap {x} {y}")

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300):
        """Swipe from one point to another."""
        self._shell(f"input swipe {x1} {y1} {x2} {y2} {duration_ms}")

    # ── number pad ──────────────────────────────────────────────────
    def number(self, n: int):
        """Send a digit 0-9."""
        if 0 <= n <= 9:
            self._keyevent(KEYCODES[str(n)])

    # ── apps ────────────────────────────────────────────────────────
    def launch_app(self, name: str):
        """Launch an app by short name (see APPS) or full package name."""
        pkg = APPS.get(name.lower(), name)
        # Resolve the leanback launcher activity for this package
        out = self._shell(
            f"cmd package resolve-activity --brief "
            f"-c android.intent.category.LEANBACK_LAUNCHER {pkg}"
        )
        # Last line is "package/ActivityClass"
        component = out.strip().splitlines()[-1].strip()
        self._shell(
            f"am start -a android.intent.action.MAIN "
            f"-c android.intent.category.LEANBACK_LAUNCHER "
            f"-n {component}"
        )

    def launch(self, name: str):
        """Alias for launch_app."""
        self.launch_app(name)

    def kill_app(self, package: str):
        """Force stop an app."""
        self._shell(f"am force-stop {package}")

    def list_apps(self) -> dict:
        """Return the known app dictionary."""
        return dict(APPS)

    # ── state ───────────────────────────────────────────────────────
    def current_app(self) -> str:
        """Return the currently focused window."""
        out = self._shell("dumpsys window | grep mCurrentFocus")
        return out

    def is_awake(self) -> bool:
        """Check if the TV screen is awake."""
        out = self._shell("dumpsys power | grep mWakefulness")
        return "Awake" in out

    def screen_size(self) -> str:
        """Return screen resolution."""
        return self._shell("wm size")

    def screenshot(self, save_path: str = "screenshot.png"):
        """Take a screenshot and pull it to the local machine."""
        remote = "/sdcard/screenshot.png"
        self._shell(f"screencap -p {remote}")
        subprocess.run(
            [self.adb, "-s", self.device, "pull", remote, save_path],
            capture_output=True, text=True, timeout=15
        )
        self._shell(f"rm {remote}")
        return save_path

    # ── convenience ────────────────────────────────────────────────
    def wait(self, seconds: float):
        """Sleep between commands."""
        time.sleep(seconds)

    def send_key(self, name: str):
        """Send a key by name from KEYCODES."""
        code = KEYCODES.get(name.lower())
        if code is None:
            raise ValueError(f"Unknown key: {name}. Available: {list(KEYCODES.keys())}")
        self._keyevent(code)

    def list_keys(self) -> list:
        """Return all available key names."""
        return list(KEYCODES.keys())

    # ── launcher management ────────────────────────────────────────
    KNOWN_LAUNCHERS = {
        "Google TV Launcher": "com.google.android.tvlauncher",
        "FLauncher": "me.efesser.flauncher",
        "Projectivy Launcher": "com.spocky.projengmenu",
        "ATV Launcher Pro": "ca.dstudio.atvlauncher.pro",
        "HALauncher": "net.i.akihiro.halauncher",
    }

    def list_launchers(self) -> list:
        """Return installed launchers with their state (enabled/disabled)."""
        results = []
        for label, pkg in self.KNOWN_LAUNCHERS.items():
            # Check if installed
            check = self._shell(f"pm list packages {pkg}")
            if not check.strip():
                continue
            # Check enabled/disabled state
            state = self._shell(f"dumpsys package {pkg} | grep 'enabled='")
            enabled = "enabled=0" not in state and "disabled" not in state.lower()
            # Check if it's the current default home
            home = self._shell(
                "cmd package resolve-activity -a android.intent.action.MAIN "
                "-c android.intent.category.HOME"
            )
            is_default = pkg in home
            results.append({
                "label": label,
                "package": pkg,
                "enabled": enabled,
                "default": is_default,
            })
        return results

    def set_launcher(self, package: str):
        """Set a launcher as the default home by disabling all others."""
        # Enable the target
        self._shell(f"pm enable {package}")
        # Disable all other launchers
        for label, pkg in self.KNOWN_LAUNCHERS.items():
            if pkg != package:
                try:
                    self._shell(f"pm disable-user --user 0 {pkg}")
                except RuntimeError:
                    pass  # may not be installed
        # Press home to trigger the new launcher
        self._keyevent(KEYCODES["home"])


# ── CLI ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    tv = TVRemote()

    if len(sys.argv) < 2:
        print("Usage: python remote.py <command> [args...]")
        print(f"\nKeys: {', '.join(tv.list_keys())}")
        print(f"\nApps: {', '.join(tv.list_apps().keys())}")
        print("\nExamples:")
        print("  python remote.py power")
        print("  python remote.py volume_up")
        print("  python remote.py launch netflix")
        print("  python remote.py type_text 'hello world'")
        print("  python remote.py tap 960 540")
        print("  python remote.py screenshot")
        print("  python remote.py current_app")
        sys.exit(0)

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd in tv.list_keys():
        tv.send_key(cmd)
        print(f"Sent: {cmd}")
    elif cmd == "launch" and args:
        tv.launch_app(args[0])
        print(f"Launched: {args[0]}")
    elif cmd == "kill" and args:
        tv.kill_app(args[0])
        print(f"Killed: {args[0]}")
    elif cmd == "type_text" and args:
        tv.type_text(" ".join(args))
        print(f"Typed: {' '.join(args)}")
    elif cmd == "tap" and len(args) >= 2:
        tv.tap(int(args[0]), int(args[1]))
        print(f"Tapped: {args[0]}, {args[1]}")
    elif cmd == "swipe" and len(args) >= 4:
        tv.swipe(int(args[0]), int(args[1]), int(args[2]), int(args[3]))
        print(f"Swiped: {args}")
    elif cmd == "screenshot":
        path = tv.screenshot()
        print(f"Saved: {path}")
    elif cmd == "current_app":
        print(tv.current_app())
    elif cmd == "is_awake":
        print("Awake" if tv.is_awake() else "Asleep")
    elif cmd == "screen_size":
        print(tv.screen_size())
    elif cmd == "apps":
        for name, pkg in tv.list_apps().items():
            print(f"  {name:20s} -> {pkg}")
    elif cmd == "keys":
        for k in tv.list_keys():
            print(f"  {k}")
    else:
        print(f"Unknown command: {cmd}")
        print(f"Keys: {', '.join(tv.list_keys())}")
        print(f"Apps: {', '.join(tv.list_apps().keys())}")
