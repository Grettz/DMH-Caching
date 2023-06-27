import os
import re

class CacheAccounting:

    USER_DIR: str = os.path.expanduser('~')
    LOGS_DIR: str = os.path.join(USER_DIR, 'AppData\\Local\\FiveM\\FiveM.app\\logs')

    log_file_paths: list[str] = None
    username: str = None

    def __init__(self) -> None:
        self.log_file_paths = self._get_log_file_paths()
        self.username = self._get_username()
        print(f'Username: {self.username}')
        self.parse_log_files()

    def _get_log_file_paths(self) -> list[str]:
        return [
            os.path.join(self.LOGS_DIR, file)
            for file in os.listdir(self.LOGS_DIR)
            if file.endswith('.log')
        ]

    def _get_username(self) -> str:
        r = re.compile(r'Name set to (.*)')
        for file in self.log_file_paths:
            with open(file, 'r', encoding='utf-8') as log_file:
                if any(match := r.search(line) for line in log_file.readlines()):
                    return match.group(1)

    def parse_log_files(self) -> None:
        for file in self.log_file_paths:
            with open(file, 'r', encoding='utf-8') as log_file:
                # Filter for in-game chat messages, which contain 'Creating Stream Component:'
                chat_msgs = filter(
                    lambda s: 'Creating Stream Component:' in s,
                    log_file.readlines()
                )

                # Regex Notes:
                # -> Spaces can be on either side of the colour codes, as seen here:
                #    "Digiscanner<FONT COLOR='#F0F0F0'> ordered!"
                #    "Armor <FONT COLOR='#F0F0F0'>ordered!"
                #    so we have " ?" surrounding each colour code which matches 0 or 1 space char.
                # -> The "(?P<Item>.+)" group can contain a space at the end due to a
                #    greedy pattern ".+", therefore we add "[^ <]" to exclude the space
                #    from the match, if it exists.
                r = re.compile(
                    r'\[ *(?P<tick>\d+)\].+'        # Tick number
                    r'<.{20}>'                      # Colour code
                    r'(?P<quantity>\d+) ?'          # Purchase quantity
                    r'<.{20}> ?x ?<.{20}> ?'        # Colour codes
                    r'(?P<item>.+[^ <]) ?'          # Item name
                    r'<.{20}> ?'                    # Colour code
                    r'(, (?P<ammo>\d+) ammo, )?'    # Ammo count (if applicable)
                    r'ordered! ?<.{20}> ?'          # Colour codes
                    r'.(?P<totalCost>\d+)'          # Total cost of purchase
                )
                # Search all in-game messages for Cache purchases
                purchases = [
                    m.groupdict()
                    for m in [r.search(msg) for msg in chat_msgs]
                    if m is not None
                ]
                if purchases:
                    print(*('\n' + str(line) for line in purchases))
    
                # TODO: Fetch cache production complete msgs and attribute them to purchases (T-6min)
    
    # TODO: confirm no. of purchase messages against messages containing 'ordered!', or other unique identifying text

if __name__ == "__main__":
    cls = CacheAccounting()

# Armour:
# [    473797] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 1,<FONT COLOR='#8466E2'>10 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>Armor <FONT COLOR='#F0F0F0'>ordered! <FONT COLOR='#72CC72'>$0 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 10,false,false,0,2
# Weapons:
# [   3621766] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 3,<FONT COLOR='#8466E2'>10 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>AP Pistol<FONT COLOR='#F0F0F0'>, 250 ammo, ordered! <FONT COLOR='#72CC72'>$86000 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 30,false,false,0,2
# [   3828422] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 1,<FONT COLOR='#8466E2'>10 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>Heavy Rifle<FONT COLOR='#F0F0F0'>, 500 ammo, ordered! <FONT COLOR='#72CC72'>$205000 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 10,false,false,0,2
# [    215812] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 1,<FONT COLOR='#8466E2'>9 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>Service Carbine<FONT COLOR='#F0F0F0'>, 500 ammo, ordered! <FONT COLOR='#72CC72'>$276300 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 9,false,false,0,2
# Components:
# [    289063] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 6,<FONT COLOR='#8466E2'>10 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>Extended Clips <FONT COLOR='#F0F0F0'>ordered! <FONT COLOR='#72CC72'>$32000 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 30,false,false,0,2
# [   1104000] [b2802_GTAProce]               Render/ [HUD_TYPE] Creating Stream Component: 5,<FONT COLOR='#8466E2'>10 <FONT COLOR='#F0F0F0'>x <FONT COLOR='#8466E2'>Tracer Rounds Clips <FONT COLOR='#F0F0F0'>ordered! <FONT COLOR='#72CC72'>$32000 <FONT COLOR='#F0F0F0'>paid, <FONT COLOR='#FF8555'>items in production<FONT COLOR='#F0F0F0'>: 10,false,false,0,2

# File 5:
# [    719] --- BEGIN LOGGING AT Mon Jun 26 19:40:58 2023 ---
# [ 473797] [1] 10x Armour
# [ 474000] [1] 10x Armour
# [ 474204] [1] 10x Armour
# [ 612454] [2] 10x Armour
# [ 612657] [2] 10x Armour
# [ 612860] [2] 10x Armour
# [ 834282]((1)) Strawberry, Alta St finished (+485, +282, +78)
# [ 848750] [3] 10x Armour
# [ 848954] [3] 10x Armour
# [ 849157] [3] 10x Armour
# [ 973469]((2)) Strawberry, Strawberry Ave finished (+1015, +812, +609)
# [1101125] [4] 10x Extended Clips
# [1101329] [4] 10x Extended Clips
# [1101547] [4] 10x Extended Clips
# [1104000] [4] 10x Tracer Rounds Clips
# [1104219] [4] 10x Tracer Rounds Clips
# [1104422] [4] 10x Tracer Rounds Clips
# [1209860]((3)) Strawberry, Alta St finished (+1110, +906, +703)
# File 6:
# [    703] --- BEGIN LOGGING AT Mon Jun 26 20:04:39 2023 ---
# [ 280828]((?)) Strawberry, Power Street finished