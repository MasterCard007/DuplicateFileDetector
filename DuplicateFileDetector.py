import os
import hashlib
from pathlib import Path
import pandas as pd
import concurrent.futures
from tqdm import tqdm

def get_folder_path(prompt):
    path = input(prompt)
    while not Path(path).is_dir():
        print("Invalid path. Please enter a valid folder path.")
        path = input(prompt)
    return Path(path)

def get_all_files(directory):
    files = []
    for file_path in directory.rglob('*'):
        try:
            if file_path.is_file() and not file_path.name.startswith('.'):
                files.append(file_path)
        except OSError:
            continue
    return files

def file_hash(file_path, chunk_size=131072):
    hasher = hashlib.blake2b()
    try:
        with file_path.open('rb') as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                hasher.update(data)
    except OSError:
        return None
    return hasher.hexdigest()

def compare_files(file1, file2, chunk_size=131072):
    try:
        if file1.stat().st_size != file2.stat().st_size:
            return False
        with file1.open('rb') as f1, file2.open('rb') as f2:
            while True:
                chunk1 = f1.read(chunk_size)
                chunk2 = f2.read(chunk_size)
                if not chunk1 and not chunk2:
                    break
                if chunk1 != chunk2:
                    return False
    except OSError:
        return False
    return True

def find_duplicates(directory):
    files = get_all_files(directory)
    duplicates = []

    size_groups = {}
    size_lookup = {}
    for file_path in files:
        try:
            size = file_path.stat().st_size
        except OSError:
            continue
        size_groups.setdefault(size, []).append(file_path)
        size_lookup[file_path] = size

    files_to_hash = [
        file_path
        for group in size_groups.values()
        if len(group) > 1
        for file_path in group
    ]

    max_threads = max(1, (os.cpu_count() or 1) // 2)
    hash_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(file_hash, file_path): file_path for file_path in files_to_hash}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing files"):
            file_path = futures[future]
            file_digest = future.result()
            if file_digest is None:
                continue
            key = (size_lookup[file_path], file_digest)
            hash_map.setdefault(key, []).append(file_path)

    for group in hash_map.values():
        if len(group) < 2:
            continue
        checked = []
        for file_path in group:
            for existing in checked:
                if compare_files(file_path, existing):
                    duplicates.append((file_path, existing))
            checked.append(file_path)

    return duplicates

def generate_comparison_table(duplicates):
    table_data = []
    for file1, file2 in duplicates:
        table_data.append({
            "File 1 Path": str(file1),
            "File 2 Path": str(file2),
            "File Size (bytes)": file1.stat().st_size
        })

    return pd.DataFrame(table_data)

def format_file_size(size_in_bytes):
    """Convert file size to a human-readable format with 4 significant figures (binary units)."""
    for unit in ["bytes", "KiB", "MiB", "GiB"]:
        if size_in_bytes < 1024 or unit == "GiB":
            return f"{size_in_bytes:.4g} {unit}"
        size_in_bytes /= 1024

def calculate_total_size(files):
    total_size = 0
    for file_path in files:
        try:
            total_size += file_path.stat().st_size
        except OSError:
            continue
    return total_size

def process_subfolders(main_folder):
    print(f"\033[92mScanning folder: {main_folder}\033[0m")  # Green for scanning folder
    duplicates = find_duplicates(main_folder)
    all_files = get_all_files(main_folder)
    total_size = calculate_total_size(all_files)
    duplicate_pairs = len(duplicates)
    duplicate_files = {file1 for file1, _ in duplicates}
    duplicate_bytes = 0
    for file1 in duplicate_files:
        try:
            duplicate_bytes += file1.stat().st_size
        except OSError:
            continue
    duplicate_percent = (duplicate_bytes / total_size * 100) if total_size else 0
    unique_size = total_size - duplicate_bytes

    if duplicates:
        print("\033[93m\nDuplicate Files Found:\033[0m")  # Yellow for heading
        table_rows = []
        for _, row in generate_comparison_table(duplicates).iterrows():
            file1 = Path(row["File 1 Path"]).relative_to(main_folder)
            file2 = Path(row["File 2 Path"]).relative_to(main_folder)
            table_rows.append(
                (
                    str(file1.parent) if str(file1.parent) != "." else "",
                    file1.name,
                    str(file2.parent) if str(file2.parent) != "." else "",
                    file2.name,
                    format_file_size(row["File Size (bytes)"]),
                )
            )

        unique_paths = sorted({row[0] for row in table_rows} | {row[2] for row in table_rows})

        def encode_path_index(index):
            letters = []
            while True:
                index, remainder = divmod(index, 26)
                letters.append(chr(ord("A") + remainder))
                if index == 0:
                    break
                index -= 1
            return "".join(reversed(letters))

        path_lookup = {path: encode_path_index(idx) for idx, path in enumerate(unique_paths)}
        print("\033[93mPath lookup:\033[0m")
        for path in unique_paths:
            label = path_lookup[path]
            display_path = path or "."
            print(f"{label}: {display_path}")
        print()

        headers = ("Path 1", "File 1 Name", "Path 2", "File 2 Name", "Size")
        col_widths = [
            max(len(headers[0]), *(len(path_lookup[row[0]]) for row in table_rows)),
            max(len(headers[1]), *(len(row[1]) for row in table_rows)),
            max(len(headers[2]), *(len(path_lookup[row[2]]) for row in table_rows)),
            max(len(headers[3]), *(len(row[3]) for row in table_rows)),
            max(len(headers[4]), *(len(row[4]) for row in table_rows)),
        ]

        header_line = " | ".join(header.ljust(width) for header, width in zip(headers, col_widths))
        separator_line = "-+-".join("-" * width for width in col_widths)
        print(header_line)
        print(separator_line)

        for path1, name1, path2, name2, size in table_rows:
            path1_label = path_lookup[path1]
            path2_label = path_lookup[path2]
            colored_path1 = f"\033[91m{path1_label.ljust(col_widths[0])}\033[0m"
            colored_name1 = f"\033[92m{name1.ljust(col_widths[1])}\033[0m"
            colored_path2 = f"\033[91m{path2_label.ljust(col_widths[2])}\033[0m"
            colored_name2 = f"\033[92m{name2.ljust(col_widths[3])}\033[0m"
            colored_size = f"\033[94m{size.ljust(col_widths[4])}\033[0m"
            print(" | ".join([colored_path1, colored_name1, colored_path2, colored_name2, colored_size]))
    else:
        print("\033[97mNo duplicate files found in the folder.\033[0m")  # White for no duplicates

    print("\033[92mSummary:\033[0m")
    print(f"\033[94mTotal folder size: {format_file_size(total_size)}\033[0m")
    print(f"\033[94mTotal size without duplicates: {format_file_size(unique_size)}\033[0m")
    print(f"\033[94mTotal duplicate size: {format_file_size(duplicate_bytes)}\033[0m")
    print(f"\033[94mTotal duplicate pairs: {duplicate_pairs}\033[0m")
    print(f"\033[94mDuplicate size percentage: {duplicate_percent:.2f}%\033[0m")

if __name__ == "__main__":
    folder_path = get_folder_path("Enter the main folder path to check subfolders for duplicates: ")
    process_subfolders(folder_path)
