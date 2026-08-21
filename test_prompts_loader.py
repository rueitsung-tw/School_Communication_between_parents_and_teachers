import os
import utils

def test_load_all_prompts():
    prompts_dir = "prompts"
    assert os.path.exists(prompts_dir), f"Prompts directory {prompts_dir} does not exist"

    prompts_db = utils.load_all_prompts(prompts_dir)
    print(f"Total prompt files loaded: {len(prompts_db)}")

    expected_themes = [
        "00_通用",
        "01_座位安排與班級經營",
        "02_成績評量與學習表現",
        "03_同儕衝突與霸凌處理",
        "04_管教方式與獎懲制度",
        "05_作業量與課業壓力",
        "06_特殊生權益與融合教育",
        "07_校園安全與意外事故",
        "08_生活照顧與責任邊界",
        "09_班費使用與行政事務",
        "10_LINE群組溝通禮儀與界線"
    ]

    missing_themes = []
    for theme in expected_themes:
        has_prompts = utils.theme_has_prompts(theme, prompts_db)
        print(f"Theme '{theme}': has_prompts={has_prompts}")
        if not has_prompts:
            missing_themes.append(theme)

    assert not missing_themes, f"The following themes failed to load Type A/B prompts: {missing_themes}"

    # Verify 00_通用_TypeA_家長訊息分析器 is not truncated
    type_a_00_key = "00_通用_TypeA_家長訊息分析器"
    assert type_a_00_key in prompts_db, f"Key {type_a_00_key} missing from prompts_db"
    prompt_a_00 = prompts_db[type_a_00_key].get("Type A")
    assert prompt_a_00 is not None, "00_TypeA prompt is None!"
    print(f"00_TypeA prompt character length: {len(prompt_a_00)}")
    assert len(prompt_a_00) >= 4000, f"00_TypeA prompt seems truncated! Length is only {len(prompt_a_00)}"

    # Verify 07_校園安全與意外事故 has both Type A and Type B
    type_07_key = "07_校園安全與意外事故"
    assert type_07_key in prompts_db, f"Key {type_07_key} missing from prompts_db"
    assert prompts_db[type_07_key].get("Type A") is not None, "07 Type A prompt is None!"
    assert prompts_db[type_07_key].get("Type B") is not None, "07 Type B prompt is None!"

    print("\n[OK] SUCCESS: All 11 prompt themes loaded successfully without truncation!")

if __name__ == "__main__":
    test_load_all_prompts()
