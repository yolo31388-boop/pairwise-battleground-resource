"""战场资源与占点系统 - 含7个bug"""
from dataclasses import dataclass, field

@dataclass
class ResourcePoint:
    rid: str
    name: str
    owner: str = ""
    level: int = 1
    progress: float = 0  # 0-100
    connected: bool = True
    x: int = 0
    y: int = 0

class BattlegroundResource:
    def __init__(self):
        self.points: dict[str, ResourcePoint] = {}
        self.resources: dict[str, int] = {"A": 0, "B": 0}
        self.kills: dict[str, int] = {"A": 0, "B": 0}

    def capture_speed(self, rid: str, attacker_power: float, defender_power: float) -> float:
        # bug1: 只看人数不看战力
        return 1.0

    def get_resource_output(self, rid: str) -> int:
        # bug2: 固定产出
        return 10

    def get_defense_bonus(self, rid: str) -> float:
        # bug3: 无防守加成
        return 1.0

    def is_connected(self, rid: str, base_id: str) -> bool:
        # bug4: 不检查连接
        return True

    def determine_winner(self) -> str:
        # bug5: 只看最终比分
        if self.resources["A"] > self.resources["B"]:
            return "A"
        return "B"

    def update_capture_progress(self, rid: str, attacker: str, power: float):
        # bug6: 瞬间重置
        point = self.points[rid]
        if point.owner != attacker:
            point.progress = 0  # 瞬间清零
        point.progress += power

    def settle_on_end(self) -> dict:
        # bug7: 不结算正在占的点
        return {}
