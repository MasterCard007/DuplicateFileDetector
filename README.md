Here's a draft for your `README.md` file based on the script you provided:

```markdown
# Duplicate File Detector

This Python script is a powerful and efficient tool designed to detect duplicate files within a specified folder and its subfolders. It uses multi-threading and cryptographic hashing to ensure reliable detection while minimizing resource usage.

---

## Features

- **Recursive Folder Scanning**: Scans the specified folder and all its subfolders.
- **Efficient File Comparison**: 
  - Uses cryptographic hashing (`BLAKE2b`) for file content comparison.
  - Verifies file size and content for precise results.
- **Multi-threading**: Leverages multiple CPU cores for fast processing.
- **Duplicate Reporting**:
  - Identifies duplicate files with detailed output.
  - Generates a comparison table of duplicate file pairs, including their file sizes.

---

## Installation

1. Clone this repository or download the script:
   ```bash
   git clone <repository-url>
   ```
2. Ensure you have Python 3.7 or higher installed.

3. Install the required dependencies:
   ```bash
   pip install pandas tqdm
   ```

---

## Usage

1. Run the script using the command line:
   ```bash
   python DuplicateFileDetector_8.py
   ```

2. Enter the path of the main folder you want to scan when prompted:
   ```
   Enter the main folder path to check subfolders for duplicates: /path/to/folder
   ```

3. The script will:
   - Scan each subfolder.
   - Report duplicate files with their paths and sizes.
   - Display results in a color-coded, human-readable format.

---

## Output

For each subfolder scanned:
- Duplicate files are listed with:
  - File paths.
  - File sizes (formatted for readability).
- If no duplicates are found, a message indicates the folder is clean.

### Example Output
```plaintext
Scanning folder: /path/to/folder/subfolder

Duplicate Files Found:
File 1: /path/to/folder/subfolder/file1.txt
File 2: /path/to/folder/subfolder/file2.txt
    Size: 15.3 KB

No duplicate files found in the folder.
```

---

## Functions

### Key Functions
1. **get_all_files(directory)**:
   - Retrieves all files from a directory (excluding hidden files).
2. **file_hash(file_path)**:
   - Computes the cryptographic hash of a file.
3. **compare_files(file1, file2)**:
   - Compares two files byte by byte if their sizes match.
4. **find_duplicates(directory)**:
   - Identifies duplicates in a given folder using hash comparisons.
5. **generate_comparison_table(duplicates)**:
   - Creates a tabular representation of duplicate files.
6. **process_subfolders(main_folder)**:
   - Processes subfolders recursively, reporting duplicates for each.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributions

Contributions are welcome! Please feel free to submit issues or pull requests to improve the script or add new features.

---

## Disclaimer

This script is provided as-is. Please review the results carefully before deleting files to avoid unintended data loss.
```

Feel free to customize it further to suit your project's needs! Let me know if you need more refinements.