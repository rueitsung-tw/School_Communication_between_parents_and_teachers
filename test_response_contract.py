import pytest
import utils

def test_validate_parent_reply_valid_two_paragraphs():
    reply = (
        "小明媽媽您好，非常理解您看到小明換到後排座位的擔心。您一定是很關心他的視力狀況以及上課的專注度，這也是我非常重視的部分。\n\n"
        "關於座位的安排，班上是固定每四週會做一次調整，會參考孩子們的身高與視力狀況。這幾天我會特別留意小明看黑板和上課的情形，歡迎您隨時與我聯繫。"
    )
    errors = utils.validate_parent_reply(reply)
    assert errors == []

def test_validate_parent_reply_valid_three_paragraphs():
    reply = (
        "小明媽媽您好，非常理解您看到小明換到後排座位的擔心。您一定是很關心他的視力狀況以及上課的專注度，這也是我非常重視的部分。\n\n"
        "關於座位的安排，班上是固定每四週會做一次調整，會參考孩子們的身高、視力矯正狀況，讓每位孩子都能體驗不同的位置。小明目前有戴眼鏡矯正，安排時我有把這點考慮進去。\n\n"
        "為了讓您更放心，這幾天我會特別留意小明看黑板的情形。如果觀察一週之後您發現有影響，隨時歡迎與我約時間討論最適合小明的方式。"
    )
    errors = utils.validate_parent_reply(reply)
    assert errors == []

def test_validate_parent_reply_empty():
    assert utils.validate_parent_reply("") != []
    assert utils.validate_parent_reply("   \n\n  ") != []

def test_validate_parent_reply_single_paragraph():
    reply = "小明媽媽您好，非常理解您看到小明換到後排座位的擔心。我們班上座位固定每四週輪換一次，這幾天我會特別留意他的視力狀況，歡迎隨時與我聯繫。"
    errors = utils.validate_parent_reply(reply)
    assert len(errors) > 0
    assert any("段落" in err for err in errors)

def test_validate_parent_reply_four_paragraphs():
    reply = (
        "第一段：小明媽媽您好，非常理解您看到小明換到後排座位的擔心。\n\n"
        "第二段：關於座位的安排，班上是固定每四週會做一次調整。\n\n"
        "第三段：小明目前有戴眼鏡矯正，我有把這點考慮進去。\n\n"
        "第四段：這幾天我會特別留意小明看黑板的情形，隨時歡迎與我討論。"
    )
    errors = utils.validate_parent_reply(reply)
    assert len(errors) > 0
    assert any("段落" in err for err in errors)

def test_validate_parent_reply_visible_nvc_headers():
    reply = (
        "觀察：小明最近坐在第四排。\n\n"
        "感受：理解媽媽心疼與焦慮的心情。\n\n"
        "需要：回應學習受重視的需要。\n\n"
        "請求：邀請媽媽觀察一週。"
    )
    errors = utils.validate_parent_reply(reply)
    assert len(errors) > 0
    assert any("標題" in err or "NVC" in err for err in errors)

def test_validate_parent_reply_bullet_points_or_numbered_list():
    reply = (
        "小明媽媽您好，關於座位的安排說明如下：\n\n"
        "1. 每四週定期輪換座位。\n"
        "2. 參考身高與視力矯正狀況。\n\n"
        "這幾天我會特別留意小明看黑板的情形，隨時歡迎聯繫。"
    )
    errors = utils.validate_parent_reply(reply)
    assert len(errors) > 0
    assert any("條列" in err or "編號" in err for err in errors)
