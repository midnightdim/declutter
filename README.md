# DeClutter

DeClutter is a desktop application built on PySide6 that helps you manage and organize your files. It provides a set of tools to automate file processing and a simple file manager with tagging capabilities.

## Features

*   **Automated File Processing:** Create rules to automatically process your files.
    *   **Sources:** Specify which folders or tagged files to process.
    *   **Conditions:** Filter files based on name, size, date, tags, and type.
    *   **Actions:** Delete, trash, copy, move, rename, and tag files.
*   **File Tagger:** A simple file manager with tagging capabilities.
    *   **Tag files and folders:** Organize your files with user-defined tags.
    *   **Tag groups:** Create groups of tags where only one tag from the group can be applied to a file.
    *   **Filter by tags:** Easily find files with specific tags.
    *   **Media preview:** Preview audio, video, and image files directly in the tagger.
*   **Drag and Drop:** Drag and drop files between DeClutter and your file explorer.

## Use Cases

*   Automatically delete old files in your "Downloads" folder.
*   Organize your "Downloads" folder by automatically moving files to subfolders based on their type, date, or other criteria.
*   Set an "expiration time" for files using tags, and DeClutter will automatically delete them when they expire.
*   If you work on a project that saves new versions with incremental numbers (like FL Studio or Reaper), you can automatically move older versions of project files to a subfolder, keeping only the N most recent versions.
*   Quickly navigate your files using tags, which can be more intuitive than navigating a folder tree.

## Advanced Rules

### Target Path Patterns (Move, Copy, Move to Subfolder)
When specifying a target folder for **Move**, **Copy**, or **Move to Subfolder** actions, you can use dynamic patterns:

*   `<type>` — Replaced with the file's type (e.g. `Document`, `Image`, `Video`), as defined in Settings → File Types.
*   `<group:GROUP_NAME>` — Replaced with the file's first tag from the specified tag group. If the file has no tags in that group, it is replaced with `None`.

**Examples:**

| Target Folder | File | Resolved Path |
| :--- | :--- | :--- |
| `D:\Sorted\<type>` | `photo.jpg` (Image) | `D:\Sorted\Image` |
| `D:\Sorted\<type>` | `report.pdf` (Document) | `D:\Sorted\Document` |
| `D:\Projects\<group:Client>` | file tagged `Acme` in group `Client` | `D:\Projects\Acme` |
| `D:\Archive\<type>\<group:Year>` | `invoice.pdf` tagged `2024` in group `Year` | `D:\Archive\Document\2024` |

### Rename Patterns
When using the **Rename** action, you can use patterns to dynamically construct the new filename:

*   `<filename>` — The original filename (including extension).
*   `<folder>` — The name of the parent folder.
*   `<replace:SEARCH:REPLACEMENT>` — Replaces text in the filename. Leave REPLACEMENT empty to remove text.

**Examples:**

| Pattern | Original File | New Filename |
| :--- | :--- | :--- |
| `backup_<filename>` | `document.txt` | `backup_document.txt` |
| `<folder> - <filename>` | `Work/budget.xls` | `Work - budget.xls` |
| `<filename><replace: [draft]:>` | `report [draft].doc` | `report.doc` |
| `<filename><replace:-:_>` | `my-file-name.txt` | `my_file_name.txt` |

## Technical Details

*   **Framework:** PySide6
*   **Database:** SQLite
*   **Platform:** Primarily tested on Windows, but also runs on macOS (with some limitations).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.