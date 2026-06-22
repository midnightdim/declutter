from declutter import i18n


class FakeCombo:
    def __init__(self, text="Move", data=None):
        self.items = []
        self.index = 0
        self.blocked = False
        self._text = text
        self._data = data

    def currentData(self):
        if self.items:
            return self.items[self.index][1]
        return self._data

    def currentText(self):
        if self.items:
            return self.items[self.index][0]
        return self._text

    def blockSignals(self, blocked):
        self.blocked = blocked

    def clear(self):
        self.items = []
        self.index = 0

    def addItem(self, text, data=None):
        self.items.append((text, data))

    def findData(self, data):
        for index, item in enumerate(self.items):
            if item[1] == data:
                return index
        return -1

    def findText(self, text):
        for index, item in enumerate(self.items):
            if item[0] == text:
                return index
        return -1

    def setCurrentIndex(self, index):
        self.index = index


def test_action_combo_displays_chinese_but_keeps_internal_value(monkeypatch):
    monkeypatch.setattr(i18n, "get_language", lambda: "zh_CN")
    combo = FakeCombo(text="Move")

    i18n.setup_combo(combo, ["Move", "Copy"], "action")

    assert combo.currentText() == "移动"
    assert i18n.combo_value(combo) == "Move"


def test_condition_summary_uses_localized_labels(monkeypatch):
    monkeypatch.setattr(i18n, "get_language", lambda: "zh_CN")

    summary = i18n.summarize_condition(
        {"type": "name", "name_switch": "matches", "filemask": "*.pdf"}
    )

    assert "名称" in summary
    assert "匹配" in summary
    assert "*.pdf" in summary
