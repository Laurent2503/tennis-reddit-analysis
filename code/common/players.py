"""Player name / nickname dictionary shared by the EDA and NLP code.

Each player maps to a list of regex alternatives. They are matched case-insensitively
with word boundaries, so "fed" matches "Fed" but not "federal". Ambiguous bare surnames
("Murray", "Williams", "Zverev") are left out or restricted; see the proposal's risks.
"""

PLAYERS = {
    # name: (tour, big3, [patterns])
    "Federer": ("ATP", True, [r"federer", r"fed(?! up)", r"roger", r"rf", r"fedex", r"goat federer"]),
    "Nadal": ("ATP", True, [r"nadal", r"rafa", r"rafael nadal"]),
    "Djokovic": ("ATP", True, [r"djokovic", r"nole", r"djoker", r"novak", r"djoko"]),
    "Andy Murray": ("ATP", False, [r"andy murray", r"muzza", r"murray"]),
    "Wawrinka": ("ATP", False, [r"wawrinka", r"stan", r"stanimal", r"stanislas"]),
    "Del Potro": ("ATP", False, [r"del ?potro", r"delpo", r"delpotro", r"jmdp"]),
    "Nishikori": ("ATP", False, [r"nishikori", r"kei"]),
    "Kyrgios": ("ATP", False, [r"kyrgios"]),
    "Thiem": ("ATP", False, [r"thiem"]),
    "A. Zverev": ("ATP", False, [r"sascha", r"alexander zverev", r"a\. ?zverev"]),
    "Cilic": ("ATP", False, [r"cilic"]),
    "Raonic": ("ATP", False, [r"raonic"]),
    "Dimitrov": ("ATP", False, [r"dimitrov", r"baby fed"]),
    "Serena Williams": ("WTA", False, [r"serena"]),
    "Venus Williams": ("WTA", False, [r"venus"]),
    "Sharapova": ("WTA", False, [r"sharapova", r"masha"]),
    "Osaka": ("WTA", False, [r"osaka", r"naomi"]),
    "Halep": ("WTA", False, [r"halep", r"simona"]),
    "Kerber": ("WTA", False, [r"kerber", r"angie"]),
    "Wozniacki": ("WTA", False, [r"wozniacki", r"woz", r"caro"]),
    "Muguruza": ("WTA", False, [r"muguruza", r"garbine"]),
    "Kvitova": ("WTA", False, [r"kvitova", r"petra"]),
    "Azarenka": ("WTA", False, [r"azarenka", r"vika"]),
    "Ostapenko": ("WTA", False, [r"ostapenko", r"jelena"]),
    "Stephens": ("WTA", False, [r"sloane"]),
}

BIG3 = [name for name, (_, big3, _) in PLAYERS.items() if big3]


def pattern(name):
    """Case-insensitive, word-bounded regex (works in Python `re` and Spark `rlike`)."""
    alts = "|".join(PLAYERS[name][2])
    return rf"(?i)\b({alts})\b"
