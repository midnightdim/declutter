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

## Technical Details

*   **Framework:** PySide6
*   **Database:** SQLite
*   **Platform:** Primarily tested on Windows, but also runs on macOS (with some limitations).

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue on GitHub.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.