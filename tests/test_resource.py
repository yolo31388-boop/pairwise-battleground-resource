"""战场资源与占点系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from battleground.resource import BattlegroundResource, ResourcePoint

class TestCaptureByPower:
    def test_higher_power_captures_faster(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "mine")
        s1 = br.capture_speed("p1", attacker_power=100, defender_power=0)
        s1000 = br.capture_speed("p1", attacker_power=1000, defender_power=0)
        assert s1000 > s1  # bug1: 都是1.0

class TestResourceOutputByLevel:
    def test_higher_level_point_outputs_more(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "mine", level=1)
        br.points["p2"] = ResourcePoint("p2", "mine", level=10)
        o1 = br.get_resource_output("p1")
        o10 = br.get_resource_output("p2")
        assert o10 > o1  # bug2: 都是10

class TestDefenseBonus:
    def test_defenders_have_bonus(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "fort")
        assert br.get_defense_bonus("p1") > 1.0  # bug3: 1.0

class TestConnectionCheck:
    def test_disconnected_point_no_full_output(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "mine", connected=False)
        assert br.is_connected("p1", "base") == False  # bug4: True

class TestWinnerByMargin:
    def test_close_score_goes_to_overtime(self):
        br = BattlegroundResource()
        br.resources = {"A": 990, "B": 1000}
        # 接近的比分应该有加时，不是直接判B赢
        assert hasattr(br, "is_overtime_needed")
        assert br.is_overtime_needed() == True  # bug5: 直接判B赢

class TestGradualProgressReset:
    def test_progress_not_instantly_reset(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "mine", owner="A", progress=90)
        br.update_capture_progress("p1", "B", power=10)
        # 不应该瞬间清零
        assert br.points["p1"].progress > 0  # bug6: 瞬间变0

class TestEndSettlement:
    def test_in_progress_capture_settled_on_end(self):
        br = BattlegroundResource()
        br.points["p1"] = ResourcePoint("p1", "mine", owner="A", progress=80)
        result = br.settle_on_end()
        assert "p1" in result  # bug7: 空
