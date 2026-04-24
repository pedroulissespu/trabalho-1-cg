import random


# =====================================================
# Definição dos poderes temáticos
# =====================================================
# Cada poder: (id, nome, descrição, max_level, ícone_char, cor)
POWER_DEFS = {
    "cafe": {
        "name": "CAFE FORTE",
        "desc": [
            "VEL +15%",
            "VEL +30%",
            "VEL +45%",
            "VEL +60%",
            "VEL +75%",
        ],
        "max_level": 5,
        "icon": "C",
        "color": (180, 120, 50),
    },
    "grupo": {
        "name": "GRUPO DE ESTUDOS",
        "desc": [
            "+1 LAPIS",
            "+2 LAPIS",
            "+3 LAPIS",
        ],
        "max_level": 3,
        "icon": "G",
        "color": (80, 180, 80),
    },
    "cola": {
        "name": "COLA NA PROVA",
        "desc": [
            "DANO +25%",
            "DANO +50%",
            "DANO +75%",
            "DANO +100%",
            "DANO +125%",
        ],
        "max_level": 5,
        "icon": "!",
        "color": (220, 60, 60),
    },
    "monitoria": {
        "name": "MONITORIA",
        "desc": [
            "ALCANCE XP +50%",
            "ALCANCE XP +100%",
            "ALCANCE XP +150%",
            "ALCANCE XP +200%",
        ],
        "max_level": 4,
        "icon": "M",
        "color": (100, 100, 255),
    },
    "noitada": {
        "name": "NOITE DE ESTUDO",
        "desc": [
            "REGEN 1 HP/S",
            "REGEN 2 HP/S",
            "REGEN 3 HP/S",
        ],
        "max_level": 3,
        "icon": "N",
        "color": (180, 100, 220),
    },
}

ALL_POWER_IDS = list(POWER_DEFS.keys())


class PowerManager:
    """Gerencia os poderes do jogador."""

    def __init__(self):
        # power_id -> nível atual (0 = não adquirido)
        self.levels = {pid: 0 for pid in ALL_POWER_IDS}

    def get_level(self, power_id):
        return self.levels.get(power_id, 0)

    def upgrade(self, power_id):
        max_lvl = POWER_DEFS[power_id]["max_level"]
        if self.levels[power_id] < max_lvl:
            self.levels[power_id] += 1

    def get_upgradeable(self):
        """Retorna lista de power_ids que ainda podem evoluir."""
        return [
            pid for pid in ALL_POWER_IDS
            if self.levels[pid] < POWER_DEFS[pid]["max_level"]
        ]

    def pick_choices(self, count=3):
        """Escolhe até `count` poderes aleatórios para oferecer ao jogador."""
        available = self.get_upgradeable()
        if not available:
            return []
        return random.sample(available, min(count, len(available)))

    # --- Efeitos calculados ---
    def speed_mult(self):
        """Multiplicador de velocidade (Café Forte)."""
        lvl = self.levels["cafe"]
        return 1.0 + lvl * 0.15

    def extra_projectiles(self):
        """Projéteis extras (Grupo de Estudos)."""
        return self.levels["grupo"]

    def damage_mult(self):
        """Multiplicador de dano (Cola na Prova)."""
        lvl = self.levels["cola"]
        return 1.0 + lvl * 0.25

    def xp_range_mult(self):
        """Multiplicador de alcance de XP (Monitoria)."""
        lvl = self.levels["monitoria"]
        return 1.0 + lvl * 0.5

    def hp_regen_per_sec(self):
        """HP regenerado por segundo (Noite de Estudo)."""
        return self.levels["noitada"]

    def get_active(self):
        """Retorna lista de (power_id, level) dos poderes ativos."""
        return [(pid, lvl) for pid, lvl in self.levels.items() if lvl > 0]
