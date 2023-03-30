import datetime, pystyle, threading
from colorama import Fore


class Console:
    def __init__(this, level):
        this.level = level
        this.color_map = {
            "INFO": (Fore.LIGHTBLUE_EX, "*"),
            "INFO2": (Fore.LIGHTCYAN_EX, "^"),
            "CAPTCHA": (Fore.LIGHTMAGENTA_EX, "C"),
            "ERROR": (Fore.LIGHTRED_EX, "!"),
            "SUCCESS": (Fore.LIGHTGREEN_EX, "$")
        }

    def log(this, *args, **kwargs):
        color, text = this.color_map.get(this.level, (Fore.LIGHTWHITE_EX, this.level))
        time_now = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-4]

        base = f"[{Fore.LIGHTBLACK_EX}{time_now}{Fore.RESET}] ({color}{text.upper()}{Fore.RESET})"
        for arg in args:
            if this.level == "SUCCESS":
                base += f" {pystyle.Colorate.Horizontal(pystyle.Colors.green_to_white, arg)}"
            else:
                base += f"{Fore.RESET} {arg}"
        if kwargs:
            base += f"{Fore.RESET} {arg}"
        with threading.Lock():
            print(base)
