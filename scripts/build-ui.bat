pyside6-uic ..\design\rule_edit_window.ui > ..\src\ui\ui_rule_edit_window.py
pyside6-uic --from-imports ..\design\rules_window.ui -o ..\src\ui\ui_rules_window.py
pyside6-uic --from-imports ..\design\condition_dialog.ui -o ..\src\ui\ui_condition_dialog.py
pyside6-uic ..\design\list_dialog.ui > ..\src\ui\ui_list_dialog.py
pyside6-uic --from-imports ..\design\tagger_window.ui -o ..\src\ui\ui_tagger_window.py
pyside6-uic ..\design\settings_dialog.ui > ..\src\ui\ui_settings_dialog.py
pyside6-uic --from-imports ..\design\tags_dialog.ui -o ..\src\ui\ui_tags_dialog.py
pyside6-rcc ..\design\DeClutter.qrc > ..\src\ui\DeClutter_rc.py