from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

DEFAULT_LANGUAGE = "en"

LANGUAGES = {
    "zh_CN": "简体中文",
    "en": "English",
}

ACTIONS = [
    "Move",
    "Delete",
    "Send to Trash",
    "Rename",
    "Copy",
    "Tag",
    "Remove tags",
    "Clear all tags",
    "Move to subfolder",
]

CONDITION_SWITCHES = ["any", "all", "none"]
CONDITION_TYPES = ["name", "date", "size", "tags", "type"]
TAG_SWITCHES = ["any", "all", "none", "no tags", "any tags", "tags in group"]
NAME_SWITCHES = ["matches", "doesn't match"]
TYPE_SWITCHES = ["is", "is not"]
DATE_UNITS = ["days", "weeks", "months", "years"]
THEMES = ["System", "Light", "Dark"]
SOURCE_MODES = ["Folder", "Tagged"]
OVERWRITE_OPTIONS = ["increment name", "overwrite"]
FILE_TABLE_HEADERS = ["Name", "Size", "Type", "Date Modified", "Tags"]

TRANSLATIONS = {
    "en": {
        "app.rules_title": "DeClutter (beta) {version}",
        "app.tagger_title": "DeClutter (beta): Tagger",
        "app.tray_title": "DeClutter",
        "app.tray_rules": "Rules",
        "app.tray_tagger": "Tagger",
        "app.tray_settings": "Settings",
        "app.tray_quit": "Quit",
        "app.tray_tooltip": "DeClutter runs every {minutes} minute(s)",
        "app.processed": "Processed files and folders:\n{details}",
        "button.add": "Add",
        "button.add_file_type": "Add New",
        "button.add_folder": "Add Folder",
        "button.add_group": "Add Group",
        "button.add_tag": "Add Tag",
        "button.advanced": "Advanced...",
        "button.apply": "Apply",
        "button.browse": "Browse...",
        "button.cancel": "Cancel",
        "button.clear": "Clear",
        "button.delete": "Delete",
        "button.edit": "Edit",
        "button.keep_tags": "Keep tags",
        "button.load": "Load",
        "button.ok": "OK",
        "button.remove": "Remove",
        "button.save": "Save",
        "button.test": "Test",
        "column.action": "Action",
        "column.filemask": "Filemask",
        "column.name": "Name",
        "column.sources": "Source(s)",
        "column.status": "Status",
        "column.tags": "Tag(s)",
        "condition.dialog_title": "Condition",
        "condition.expression": "expression",
        "condition.file_age": "File age",
        "condition.file_has": "File has",
        "condition.file_name": "File name",
        "condition.file_size": "File size is",
        "condition.file_type": "File type",
        "condition.hint_masks": "You can use multiple comma-separated expressions",
        "condition.of_selected_tags": "of selected tags:",
        "condition.select_by": "Select files by",
        "condition.selected_tags": "Selected tags: {tags}",
        "condition.selected_tags_empty": "Selected tags:",
        "condition_summary.date": "Age is {switch} {age} {units}",
        "condition_summary.name": "Name {switch} {mask}",
        "condition_summary.size": "File size is {switch} {size}{units}",
        "condition_summary.tags_any": "Has {switch} of these tags: {tags}",
        "condition_summary.tags_group": "Has tags in group: {group}",
        "condition_summary.tags_simple": "Has {switch}",
        "condition_summary.type": "File type {switch} {file_type}",
        "dialog.about_title": "About DeClutter",
        "dialog.about_text": "DeClutter version {version}\nhttps://github.com/midnightdim/declutter\nAuthor: Dmitry Beloglazov\nTelegram: @beloglazov",
        "dialog.add_group_title": "Add new group",
        "dialog.add_tag_title": "Add new tag",
        "dialog.clear_log": "Are you sure you want to clear the log?",
        "dialog.create_folder_label": "Enter folder name:",
        "dialog.create_folder_title": "Create new folder",
        "dialog.delete_group": "You're about to delete this group:\n{group}\nWould you like to keep its tags (will be moved to Default group) or delete them all?",
        "dialog.delete_rules": "Are you sure you want to delete selected rules:\n{rules}\n?",
        "dialog.delete_tag": "Are you sure you want to delete this tag: \"{tag}\"?",
        "dialog.delete_tag_used": "Are you sure you want to delete this tag: \"{tag}\"?\nThis tag is used by {count} {files}.\nDeleting it will remove the tag from {target}.",
        "dialog.duplicate_file_type": "Duplicate format name, please change it",
        "dialog.duplicate_file_types": "Duplicate format name(s) detected, please remove duplicates",
        "dialog.duplicate_group": "Another group with this name already exists. Please choose a different name.",
        "dialog.duplicate_tag": "A tag named '{tag}' already exists.",
        "dialog.enable_rule": "The rule is not enabled, would you like to enable it before saving?",
        "dialog.enable_rule_title": "Enable rule?",
        "dialog.error": "Error",
        "dialog.file_exists": "File '{file}' already exists in the target folder.\nOverwrite?",
        "dialog.file_exists_title": "File exists",
        "dialog.group_note_default": "This is the default group",
        "dialog.input_group_name": "Enter group name:",
        "dialog.input_tag_name": "Enter tag name:",
        "dialog.keep_or_delete_tags_title": "Question",
        "dialog.new_version": "New version: {version}",
        "dialog.new_version_text": "There's a new version of DeClutter available. Download now?",
        "dialog.no_rule_selected": "Please select a rule first.",
        "dialog.no_rule_selected_title": "No rule selected",
        "dialog.rename_tag": "Enter new name:",
        "dialog.rename_tag_title": "Rename tag",
        "dialog.rule_executed": "Rule executed",
        "dialog.select_color": "Select color",
        "dialog.select_folder": "Select folder",
        "dialog.warning": "Warning",
        "dialog.cant_do_that": "Can't do that",
        "dialog.cant_create_folder": "Can't create this folder",
        "dialog.cant_delete_default_group": "You can't delete the default group, sorry.",
        "dialog.create_tag_failed": "Failed to create tag '{tag}': {error}",
        "dialog.merge_tag": "This tag already exists. Files tagged with '{old_tag}' ({count} {files}) will be tagged with '{new_tag}'.\nAre you sure you want to proceed?",
        "dialog.permanent_delete": "Permanently delete {count} item(s)? This cannot be undone.",
        "dialog.permanent_delete_title": "Delete files",
        "dialog.remove_file_type": "This will delete the format. Are you sure?{used}",
        "dialog.remove_file_type_used": "\nIt's used in {count} condition(s) (which won't be removed).",
        "error.filemask_empty": "Filemask can't be empty",
        "error.incorrect_age": "Incorrect Age value",
        "error.incorrect_size": "Incorrect Size value",
        "error.no_tags_selected": "You haven't selected any tags",
        "error.rule_name_missing": "Please enter the name",
        "error.rule_source_missing": "Please select at least one source",
        "error.rule_condition_missing": "Please add at least one condition",
        "error.rule_target_folder_missing": "Please specify the target folder",
        "error.rule_target_subfolder_missing": "Please specify the target subfolder",
        "error.rule_name_pattern_missing": "Please specify the name pattern",
        "error.rule_ignore_count_missing": "Please specify the number of files to ignore",
        "file_action.cleared_tags": "Cleared tags for {file}",
        "file_action.copied": "Copied {file} to {target}",
        "file_action.deleted": "Deleted {file}",
        "file_action.moved": "Moved {file} to {target}",
        "file_action.moved_subfolder": "Moved {file} to subfolder: {target}",
        "file_action.name_pattern_missing": "Error: name pattern is missing for rule {rule}",
        "file_action.renamed": "Renamed {file} to {target}",
        "file_action.replaced": "Replaced {target} with {file}",
        "file_action.same_size_skip": "File {file} already exists in the target location and has the same size, skipping",
        "file_action.sent_trash": "Sent to trash {file}",
        "file_action.tagged": "Tagged {file} with {tags}",
        "file_action.tags_copied": ", tags copied too",
        "file_action.tags_not_copied": ", tags not copied",
        "file_action.untagged": "Removed these tags from {file}: {tags}",
        "file_action.with_tags": ", with tags",
        "file_types.note": "To remove a format leave its name empty",
        "filters.clear": "Clear",
        "filters.label_suffix": "of these must be true:",
        "filters.title": "Filters",
        "group_dialog.combo": "Single value (combobox)",
        "group_dialog.checkboxes": "Multi-value (checkboxes)",
        "group_dialog.show_name": "Show group name",
        "group_dialog.title": "Edit Group",
        "label.default_group": "Default",
        "list.affected": "Affected files and folders:",
        "list.files_affected": "{count} file(s) affected by this rule:",
        "list.no_files_affected": "No files affected by this rule.",
        "media.preview": "Media Preview",
        "media.play": "Play",
        "menu.file": "File",
        "menu.help": "Help",
        "menu.options": "Options",
        "menu.recent_folders": "Recent folders",
        "menu.tools": "Tools",
        "menu.view": "View",
        "rules.add_edit_title": "Add/Edit Rule",
        "rules.all_tagged": "All tagged",
        "rules.do_following": "Do the following:",
        "rules.disabled": "Disabled",
        "rules.enabled": "Enabled",
        "rules.file_conflict": "If file with same name and different size exists:",
        "rules.ignore": "Ignore",
        "rules.keep_folder_structure": "keep folder structure",
        "rules.keep_tags": "keep tags",
        "rules.newest": "newest file(s) in every folder",
        "rules.recursive": "Recursive",
        "rules.rule_name": "Rule name",
        "rules.selected_tags": "Selected tags: {tags}",
        "rules.selected_tags_empty": "Selected tags:",
        "rules.sources": "Sources to process",
        "rules.when": "If",
        "rules.when_suffix": "of the conditions apply:",
        "rules.to_folder": "to folder",
        "settings.date_question": "Which date (from file metadata) should be used in rule conditions?",
        "settings.date_tab": "Date",
        "settings.date_title": "Date definition",
        "settings.file_types_tab": "File Types",
        "settings.language": "Language",
        "settings.launch_startup": "Launch at startup",
        "settings.main_tab": "Main",
        "settings.minutes": "minutes",
        "settings.process_interval": "Process rules every",
        "settings.style": "Style",
        "settings.theme": "Theme",
        "settings.title": "Settings",
        "status.deleted": "{count} item(s) deleted",
        "status.selected": "{count} item(s) selected",
        "status.trashed": "{count} item(s) sent to trash",
        "tagger.new_window": "New tagger window",
        "tagger.none": "None",
        "tags.manage": "Manage Tags",
        "tags.title": "Tags",
        "tooltip.path_tokens": "<html><head/><body><p>You can use the following tokens:</p><p>&lt;type&gt; will be replaced with file type</p><p>&lt;group:MyGroup&gt; will be replaced with the (first) tag of the file in MyGroup or 'None' if the file doesn't have tags from MyGroup</p></body></html>",
        "tooltip.rename_tokens": "<html><head/><body><p>You can use the following tokens:</p><p>&lt;filename&gt; will be replaced with file/folder name</p><p>&lt;folder&gt; will be replaced with the parent folder name</p><p>&lt;replace:ABC:XYZ&gt; will replace ABC with XYZ in file/folder name</p></body></html>",
        "action.Move": "Move",
        "action.Delete": "Delete",
        "action.Send to Trash": "Send to Trash",
        "action.Rename": "Rename",
        "action.Copy": "Copy",
        "action.Tag": "Tag",
        "action.Remove tags": "Remove tags",
        "action.Clear all tags": "Clear all tags",
        "action.Move to subfolder": "Move to subfolder",
        "action.clear_log_file": "Clear log file",
        "action.execute": "Execute",
        "action.move_down": "Move down",
        "action.move_up": "Move up",
        "action.open_log_file": "Open log file",
        "action.open_tagger": "Open Tagger",
        "condition_switch.any": "any",
        "condition_switch.all": "all",
        "condition_switch.none": "none",
        "condition_type.name": "name",
        "condition_type.date": "date",
        "condition_type.size": "size",
        "condition_type.tags": "tags",
        "condition_type.type": "type",
        "date_option.0": "earliest of modified && created (default)",
        "date_option.1": "modified",
        "date_option.2": "created",
        "date_option.3": "latest of modified && created",
        "date_option.4": "last access",
        "date_unit.days": "days",
        "date_unit.weeks": "weeks",
        "date_unit.months": "months",
        "date_unit.years": "years",
        "file_type.Audio": "Audio",
        "file_type.Document": "Document",
        "file_type.Image": "Image",
        "file_type.Other": "Other",
        "file_type.Video": "Video",
        "language.en": "English",
        "language.zh_CN": "简体中文",
        "name_switch.matches": "matches",
        "name_switch.doesn't match": "doesn't match",
        "overwrite.increment name": "increment name",
        "overwrite.overwrite": "overwrite",
        "report.copied": "copied",
        "report.moved": "moved",
        "report.moved to subfolder": "moved to subfolder",
        "report.deleted": "deleted",
        "report.trashed": "trashed",
        "report.tagged": "tagged",
        "report.untagged": "untagged",
        "report.cleared tags": "cleared tags",
        "report.renamed": "renamed",
        "source.Folder": "Folder",
        "source.Tagged": "Tagged",
        "tag_switch.any": "any",
        "tag_switch.all": "all",
        "tag_switch.none": "none",
        "tag_switch.no tags": "no tags",
        "tag_switch.any tags": "any tags",
        "tag_switch.tags in group": "tags in group",
        "theme.System": "System",
        "theme.Light": "Light",
        "theme.Dark": "Dark",
        "type_switch.is": "is",
        "type_switch.is not": "is not",
        "file_header.Name": "Name",
        "file_header.Size": "Size",
        "file_header.Type": "Type",
        "file_header.Date Modified": "Date Modified",
        "file_header.Tags": "Tags",
    },
    "zh_CN": {
        "app.rules_title": "DeClutter（测试版） {version}",
        "app.tagger_title": "DeClutter（测试版）：标签管理器",
        "app.tray_title": "DeClutter",
        "app.tray_rules": "规则",
        "app.tray_tagger": "标签管理器",
        "app.tray_settings": "设置",
        "app.tray_quit": "退出",
        "app.tray_tooltip": "DeClutter 每 {minutes} 分钟运行一次",
        "app.processed": "已处理文件和文件夹：\n{details}",
        "button.add": "添加",
        "button.add_file_type": "新增",
        "button.add_folder": "添加文件夹",
        "button.add_group": "添加分组",
        "button.add_tag": "添加标签",
        "button.advanced": "高级...",
        "button.apply": "应用",
        "button.browse": "浏览...",
        "button.cancel": "取消",
        "button.clear": "清空",
        "button.delete": "删除",
        "button.edit": "编辑",
        "button.keep_tags": "保留标签",
        "button.load": "加载",
        "button.ok": "确定",
        "button.remove": "移除",
        "button.save": "保存",
        "button.test": "测试",
        "column.action": "动作",
        "column.filemask": "文件匹配规则",
        "column.name": "名称",
        "column.sources": "来源",
        "column.status": "状态",
        "column.tags": "标签",
        "condition.dialog_title": "条件",
        "condition.expression": "表达式",
        "condition.file_age": "文件时间",
        "condition.file_has": "文件包含",
        "condition.file_name": "文件名",
        "condition.file_size": "文件大小",
        "condition.file_type": "文件类型",
        "condition.hint_masks": "可以使用多个用英文逗号分隔的表达式",
        "condition.of_selected_tags": "所选标签：",
        "condition.select_by": "按以下方式筛选文件",
        "condition.selected_tags": "已选择标签：{tags}",
        "condition.selected_tags_empty": "已选择标签：",
        "condition_summary.date": "文件时间 {switch} {age} {units}",
        "condition_summary.name": "名称 {switch} {mask}",
        "condition_summary.size": "文件大小 {switch} {size}{units}",
        "condition_summary.tags_any": "包含{switch}以下标签：{tags}",
        "condition_summary.tags_group": "包含分组中的标签：{group}",
        "condition_summary.tags_simple": "包含{switch}",
        "condition_summary.type": "文件类型 {switch} {file_type}",
        "dialog.about_title": "关于 DeClutter",
        "dialog.about_text": "DeClutter 版本 {version}\nhttps://github.com/midnightdim/declutter\n作者：Dmitry Beloglazov\nTelegram：@beloglazov",
        "dialog.add_group_title": "添加新分组",
        "dialog.add_tag_title": "添加新标签",
        "dialog.clear_log": "确定要清空日志吗？",
        "dialog.create_folder_label": "请输入文件夹名称：",
        "dialog.create_folder_title": "新建文件夹",
        "dialog.delete_group": "即将删除此分组：\n{group}\n要保留其中的标签（移动到默认分组）还是全部删除？",
        "dialog.delete_rules": "确定要删除选中的规则吗：\n{rules}\n？",
        "dialog.delete_tag": "确定要删除此标签：“{tag}”吗？",
        "dialog.delete_tag_used": "确定要删除此标签：“{tag}”吗？\n此标签正在被 {count} 个文件使用。\n删除后会从这些文件中移除此标签。",
        "dialog.duplicate_file_type": "格式名称重复，请修改",
        "dialog.duplicate_file_types": "检测到重复的格式名称，请移除重复项",
        "dialog.duplicate_group": "已有同名分组，请换一个名称。",
        "dialog.duplicate_tag": "已存在名为“{tag}”的标签。",
        "dialog.enable_rule": "此规则尚未启用，保存前是否启用？",
        "dialog.enable_rule_title": "启用规则？",
        "dialog.error": "错误",
        "dialog.file_exists": "目标文件夹中已存在文件“{file}”。\n是否覆盖？",
        "dialog.file_exists_title": "文件已存在",
        "dialog.group_note_default": "这是默认分组",
        "dialog.input_group_name": "请输入分组名称：",
        "dialog.input_tag_name": "请输入标签名称：",
        "dialog.keep_or_delete_tags_title": "确认",
        "dialog.new_version": "新版本：{version}",
        "dialog.new_version_text": "DeClutter 有新版本可用。现在下载吗？",
        "dialog.no_rule_selected": "请先选择一条规则。",
        "dialog.no_rule_selected_title": "未选择规则",
        "dialog.rename_tag": "请输入新名称：",
        "dialog.rename_tag_title": "重命名标签",
        "dialog.rule_executed": "规则已执行",
        "dialog.select_color": "选择颜色",
        "dialog.select_folder": "选择文件夹",
        "dialog.warning": "警告",
        "dialog.cant_do_that": "无法执行",
        "dialog.cant_create_folder": "无法创建此文件夹",
        "dialog.cant_delete_default_group": "不能删除默认分组。",
        "dialog.create_tag_failed": "创建标签“{tag}”失败：{error}",
        "dialog.merge_tag": "此标签已存在。标记为“{old_tag}”的 {count} 个文件将改为标记“{new_tag}”。\n确定继续吗？",
        "dialog.permanent_delete": "永久删除 {count} 个项目？此操作无法撤销。",
        "dialog.permanent_delete_title": "删除文件",
        "dialog.remove_file_type": "这会删除该格式。确定吗？{used}",
        "dialog.remove_file_type_used": "\n它被 {count} 条条件使用（这些条件不会被移除）。",
        "error.filemask_empty": "文件匹配规则不能为空",
        "error.incorrect_age": "文件时间数值不正确",
        "error.incorrect_size": "文件大小数值不正确",
        "error.no_tags_selected": "尚未选择任何标签",
        "error.rule_name_missing": "请输入规则名称",
        "error.rule_source_missing": "请选择至少一个来源",
        "error.rule_condition_missing": "请添加至少一个条件",
        "error.rule_target_folder_missing": "请指定目标文件夹",
        "error.rule_target_subfolder_missing": "请指定目标子文件夹",
        "error.rule_name_pattern_missing": "请指定命名模式",
        "error.rule_ignore_count_missing": "请指定要忽略的文件数量",
        "file_action.cleared_tags": "已清除 {file} 的标签",
        "file_action.copied": "已复制 {file} 到 {target}",
        "file_action.deleted": "已删除 {file}",
        "file_action.moved": "已移动 {file} 到 {target}",
        "file_action.moved_subfolder": "已移动 {file} 到子文件夹：{target}",
        "file_action.name_pattern_missing": "错误：规则“{rule}”缺少命名模式",
        "file_action.renamed": "已将 {file} 重命名为 {target}",
        "file_action.replaced": "已用 {file} 替换 {target}",
        "file_action.same_size_skip": "文件 {file} 已存在于目标位置且大小相同，已跳过",
        "file_action.sent_trash": "已移至回收站：{file}",
        "file_action.tagged": "已为 {file} 添加标签 {tags}",
        "file_action.tags_copied": "，标签也已复制",
        "file_action.tags_not_copied": "，标签未复制",
        "file_action.untagged": "已从 {file} 移除这些标签：{tags}",
        "file_action.with_tags": "，包含标签",
        "file_types.note": "要删除格式，请将名称留空",
        "filters.clear": "清空",
        "filters.label_suffix": "个条件必须满足：",
        "filters.title": "过滤器",
        "group_dialog.combo": "单选（下拉框）",
        "group_dialog.checkboxes": "多选（复选框）",
        "group_dialog.show_name": "显示分组名称",
        "group_dialog.title": "编辑分组",
        "label.default_group": "默认",
        "list.affected": "受影响的文件和文件夹：",
        "list.files_affected": "{count} 个文件/文件夹会受此规则影响：",
        "list.no_files_affected": "此规则不会影响任何文件。",
        "media.preview": "媒体预览",
        "media.play": "播放",
        "menu.file": "文件",
        "menu.help": "帮助",
        "menu.options": "选项",
        "menu.recent_folders": "最近文件夹",
        "menu.tools": "工具",
        "menu.view": "视图",
        "rules.add_edit_title": "添加/编辑规则",
        "rules.all_tagged": "所有已标记项目",
        "rules.do_following": "执行以下操作：",
        "rules.disabled": "禁用",
        "rules.enabled": "启用",
        "rules.file_conflict": "存在同名但大小不同的文件时：",
        "rules.ignore": "忽略",
        "rules.keep_folder_structure": "保留文件夹结构",
        "rules.keep_tags": "保留标签",
        "rules.newest": "每个文件夹中最新的文件",
        "rules.recursive": "递归",
        "rules.rule_name": "规则名称",
        "rules.selected_tags": "已选择标签：{tags}",
        "rules.selected_tags_empty": "已选择标签：",
        "rules.sources": "要处理的来源",
        "rules.when": "如果",
        "rules.when_suffix": "个条件满足：",
        "rules.to_folder": "到文件夹",
        "settings.date_question": "规则条件应使用文件元数据中的哪个日期？",
        "settings.date_tab": "日期",
        "settings.date_title": "日期定义",
        "settings.file_types_tab": "文件类型",
        "settings.language": "语言",
        "settings.launch_startup": "开机启动",
        "settings.main_tab": "主要",
        "settings.minutes": "分钟运行规则",
        "settings.process_interval": "每隔",
        "settings.style": "样式",
        "settings.theme": "主题",
        "settings.title": "设置",
        "status.deleted": "已删除 {count} 个项目",
        "status.selected": "已选择 {count} 个项目",
        "status.trashed": "已将 {count} 个项目移至回收站",
        "tagger.new_window": "新建标签管理器窗口",
        "tagger.none": "无",
        "tags.manage": "管理标签",
        "tags.title": "标签",
        "tooltip.path_tokens": "<html><head/><body><p>可以使用以下标记：</p><p>&lt;type&gt; 会替换为文件类型</p><p>&lt;group:MyGroup&gt; 会替换为该文件在 MyGroup 分组中的第一个标签；如果没有该分组标签，则替换为 None</p></body></html>",
        "tooltip.rename_tokens": "<html><head/><body><p>可以使用以下标记：</p><p>&lt;filename&gt; 会替换为文件/文件夹名称</p><p>&lt;folder&gt; 会替换为父文件夹名称</p><p>&lt;replace:ABC:XYZ&gt; 会把文件/文件夹名称中的 ABC 替换为 XYZ</p></body></html>",
        "action.Move": "移动",
        "action.Delete": "删除",
        "action.Send to Trash": "移至回收站",
        "action.Rename": "重命名",
        "action.Copy": "复制",
        "action.Tag": "添加标签",
        "action.Remove tags": "移除标签",
        "action.Clear all tags": "清除所有标签",
        "action.Move to subfolder": "移动到子文件夹",
        "action.clear_log_file": "清空日志",
        "action.execute": "执行",
        "action.move_down": "下移",
        "action.move_up": "上移",
        "action.open_log_file": "打开日志文件",
        "action.open_tagger": "打开标签管理器",
        "condition_switch.any": "任意",
        "condition_switch.all": "全部",
        "condition_switch.none": "都不",
        "condition_type.name": "名称",
        "condition_type.date": "日期",
        "condition_type.size": "大小",
        "condition_type.tags": "标签",
        "condition_type.type": "类型",
        "date_option.0": "修改时间和创建时间中较早者（默认）",
        "date_option.1": "修改时间",
        "date_option.2": "创建时间",
        "date_option.3": "修改时间和创建时间中较晚者",
        "date_option.4": "最后访问时间",
        "date_unit.days": "天",
        "date_unit.weeks": "周",
        "date_unit.months": "月",
        "date_unit.years": "年",
        "file_type.Audio": "音频",
        "file_type.Document": "文档",
        "file_type.Image": "图片",
        "file_type.Other": "其他",
        "file_type.Video": "视频",
        "language.en": "English",
        "language.zh_CN": "简体中文",
        "name_switch.matches": "匹配",
        "name_switch.doesn't match": "不匹配",
        "overwrite.increment name": "自动递增名称",
        "overwrite.overwrite": "覆盖",
        "report.copied": "已复制",
        "report.moved": "已移动",
        "report.moved to subfolder": "已移动到子文件夹",
        "report.deleted": "已删除",
        "report.trashed": "已移至回收站",
        "report.tagged": "已添加标签",
        "report.untagged": "已移除标签",
        "report.cleared tags": "已清除标签",
        "report.renamed": "已重命名",
        "source.Folder": "文件夹",
        "source.Tagged": "已标记",
        "tag_switch.any": "任意",
        "tag_switch.all": "全部",
        "tag_switch.none": "都不",
        "tag_switch.no tags": "无标签",
        "tag_switch.any tags": "任意标签",
        "tag_switch.tags in group": "分组中的标签",
        "theme.System": "跟随系统",
        "theme.Light": "浅色",
        "theme.Dark": "深色",
        "type_switch.is": "是",
        "type_switch.is not": "不是",
        "file_header.Name": "名称",
        "file_header.Size": "大小",
        "file_header.Type": "类型",
        "file_header.Date Modified": "修改日期",
        "file_header.Tags": "标签",
    },
}


def get_language() -> str:
    try:
        from declutter.config import DB_FILE
        from declutter.store import get_setting

        if not Path(DB_FILE).exists():
            return DEFAULT_LANGUAGE
        lang = get_setting("language", DEFAULT_LANGUAGE)
    except Exception:
        lang = DEFAULT_LANGUAGE
    return lang if lang in LANGUAGES else DEFAULT_LANGUAGE


def tr(key: str, **kwargs) -> str:
    lang = get_language()
    text = TRANSLATIONS.get(lang, {}).get(key)
    if text is None:
        text = TRANSLATIONS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text


def label(prefix: str, value) -> str:
    return tr(f"{prefix}.{value}")


def combo_value(combo) -> str:
    data = combo.currentData()
    return data if data is not None else combo.currentText()


def set_combo_value(combo, value: str):
    idx = combo.findData(value)
    if idx < 0:
        idx = combo.findText(value)
    if idx >= 0:
        combo.setCurrentIndex(idx)


def setup_combo(combo, values: Iterable[str], prefix: str, current: Optional[str] = None):
    current_value = current if current is not None else combo_value(combo)
    combo.blockSignals(True)
    combo.clear()
    for value in values:
        combo.addItem(label(prefix, value), value)
    set_combo_value(combo, current_value)
    combo.blockSignals(False)


def setup_language_combo(combo, current: Optional[str] = None):
    current_value = current or get_language()
    combo.blockSignals(True)
    combo.clear()
    for code in LANGUAGES:
        combo.addItem(tr(f"language.{code}"), code)
    set_combo_value(combo, current_value)
    combo.blockSignals(False)


def localized_action(action: str) -> str:
    return label("action", action)


def localized_file_type(file_type: str) -> str:
    return label("file_type", file_type)


def localized_source(source: str) -> str:
    try:
        from declutter.config import ALL_TAGGED_TEXT

        if source == ALL_TAGGED_TEXT:
            return tr("rules.all_tagged")
    except Exception:
        pass
    return source


def localized_group_name(name: str, payload: Optional[dict] = None) -> str:
    if (payload and payload.get("id") == 1) or name == "Default":
        return tr("label.default_group")
    return name


def summarize_condition(condition: dict) -> str:
    ctype = condition.get("type", "")
    if ctype == "tags":
        tag_switch = condition.get("tag_switch", "")
        if tag_switch == "tags in group":
            return tr("condition_summary.tags_group", group=condition.get("tag_group", ""))
        if tag_switch in ("no tags", "any tags"):
            return tr("condition_summary.tags_simple", switch=label("tag_switch", tag_switch))
        return tr(
            "condition_summary.tags_any",
            switch=label("tag_switch", tag_switch),
            tags=", ".join(condition.get("tags", [])),
        )
    if ctype == "date":
        return tr(
            "condition_summary.date",
            switch=condition.get("age_switch", ""),
            age=condition.get("age", ""),
            units=label("date_unit", condition.get("age_units", "")),
        )
    if ctype == "name":
        return tr(
            "condition_summary.name",
            switch=label("name_switch", condition.get("name_switch", "matches")),
            mask=condition.get("filemask", ""),
        )
    if ctype == "size":
        return tr(
            "condition_summary.size",
            switch=condition.get("size_switch", ""),
            size=condition.get("size", ""),
            units=condition.get("size_units", ""),
        )
    if ctype == "type":
        return tr(
            "condition_summary.type",
            switch=label("type_switch", condition.get("file_type_switch", "")),
            file_type=localized_file_type(condition.get("file_type", "")),
        )
    return str(condition)
