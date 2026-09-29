"""战场资源与占点系统"""
from dataclasses import dataclass, field

# 胜负判定:资源差小于该阈值视为接近,进入加时
OVERTIME_MARGIN = 50
# 结算缓冲:进度达到该值的在占点视为完成占领
SETTLE_PROGRESS_THRESHOLD = 50.0


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
    occupied_ticks: int = 0  # 当前占领方已持有时长


class BattlegroundResource:
    def __init__(self):
        self.points: dict[str, ResourcePoint] = {}
        self.resources: dict[str, int] = {"A": 0, "B": 0}
        self.kills: dict[str, int] = {"A": 0, "B": 0}

    def capture_speed(self, rid: str, attacker_power: float, defender_power: float) -> float:
        # 占点速度按双方战力对比计算:战力越高占得越快,
        # 防守方有加成,攻方需要战力优势才能快速夺点
        if attacker_power <= 0:
            return 0.0
        effective_defense = defender_power * self.get_defense_bonus(rid)
        ratio = attacker_power / (attacker_power + effective_defense)
        scale = attacker_power / (100.0 + attacker_power)
        return 2.0 * ratio * scale

    def get_resource_output(self, rid: str) -> int:
        # 产出按点的等级和占领时长计算;被切断连接的点产出减半
        point = self.points[rid]
        output = 10 * point.level
        output = int(output * (1.0 + 0.1 * min(point.occupied_ticks, 10)))
        if not self.is_connected(rid, ""):
            output //= 2
        return output

    def get_defense_bonus(self, rid: str) -> float:
        # 防守方有地形和工事加成,等级越高工事越强
        point = self.points.get(rid)
        level = point.level if point else 1
        return 1.5 + 0.1 * (level - 1)

    def is_connected(self, rid: str, base_id: str) -> bool:
        # 资源点需要和己方基地有连接路径
        point = self.points.get(rid)
        if point is None:
            return False
        return point.connected

    def is_overtime_needed(self) -> bool:
        # 资源差接近时进入加时,不直接判定胜负
        return abs(self.resources["A"] - self.resources["B"]) < OVERTIME_MARGIN

    def determine_winner(self) -> str:
        # 胜负按资源差阈值综合判定,接近的比分进入加时
        if self.is_overtime_needed():
            return "overtime"
        if self.resources["A"] > self.resources["B"]:
            return "A"
        return "B"

    def update_capture_progress(self, rid: str, attacker: str, power: float):
        # 进度按速率变化:争夺阶段先抵消对方进度,不瞬间清零
        point = self.points[rid]
        if point.owner and point.owner != attacker:
            # 争夺阶段:攻方战力先削减守方进度
            point.progress = max(0.0, point.progress - power)
            if point.progress == 0.0:
                point.owner = ""
                point.occupied_ticks = 0
        else:
            point.progress = min(100.0, point.progress + power)
            if point.progress >= 100.0:
                point.owner = attacker
                point.occupied_ticks = 0

    def settle_on_end(self) -> dict:
        # 结算缓冲:战场结束时正在进行的占点按进度结算后再判定
        settled = {}
        for rid, point in self.points.items():
            if point.progress > 0:
                settled[rid] = {
                    "owner": point.owner,
                    "progress": point.progress,
                    "completed": point.progress >= SETTLE_PROGRESS_THRESHOLD,
                }
        return settled
