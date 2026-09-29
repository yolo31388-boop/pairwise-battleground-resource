"""战场资源与占点系统"""
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
    hold_ticks: int = 0  # 占领时长

# 胜负判定的资源差阈值，差值小于该比例视为接近，需要加时
OVERTIME_MARGIN = 0.05
# 被切断连接的资源点产出系数
DISCONNECTED_OUTPUT_FACTOR = 0.5

class BattlegroundResource:
    def __init__(self):
        self.points: dict[str, ResourcePoint] = {}
        self.resources: dict[str, int] = {"A": 0, "B": 0}
        self.kills: dict[str, int] = {"A": 0, "B": 0}

    def capture_speed(self, rid: str, attacker_power: float, defender_power: float) -> float:
        # 占点速度按双方战力对比计算：防守方有加成，攻方需要战力优势
        effective_defense = defender_power * self.get_defense_bonus(rid)
        advantage = attacker_power - effective_defense
        if advantage <= 0:
            return 0.0
        return advantage / 10.0

    def get_resource_output(self, rid: str) -> int:
        # 产出按点的等级和占领时长计算，被切断的点减半
        point = self.points[rid]
        output = point.level * 10 * (1 + point.hold_ticks // 10)
        if not point.connected:
            output = int(output * DISCONNECTED_OUTPUT_FACTOR)
        return output

    def get_defense_bonus(self, rid: str) -> float:
        # 防守方有地形和工事加成
        return 1.5

    def is_connected(self, rid: str, base_id: str) -> bool:
        # 资源点需要和己方基地有连接路径
        return self.points[rid].connected

    def determine_winner(self) -> str:
        if self.is_overtime_needed():
            return "overtime"
        if self.resources["A"] > self.resources["B"]:
            return "A"
        if self.resources["B"] > self.resources["A"]:
            return "B"
        return "draw"

    def is_overtime_needed(self) -> bool:
        # 接近的比分（差值小于阈值）需要加时
        a, b = self.resources["A"], self.resources["B"]
        if a == b:
            return True
        return abs(a - b) < max(a, b) * OVERTIME_MARGIN

    def update_capture_progress(self, rid: str, attacker: str, power: float):
        # 进度按速率变化：争夺阶段先削减对方进度，清零后才积累己方进度
        point = self.points[rid]
        if point.owner != attacker:
            point.progress = max(0.0, point.progress - power)
            if point.progress == 0.0:
                point.owner = ""
        else:
            point.progress = min(100.0, point.progress + power)
            if point.progress >= 100.0:
                point.hold_ticks += 1

    def settle_on_end(self) -> dict:
        # 结算缓冲：时间到时把正在进行的占点按当前进度结算
        settled = {}
        for rid, point in self.points.items():
            if point.owner and point.progress > 0:
                gain = int(self.get_resource_output(rid) * point.progress / 100)
                self.resources[point.owner] += gain
                settled[rid] = {"owner": point.owner, "progress": point.progress, "gain": gain}
        return settled
