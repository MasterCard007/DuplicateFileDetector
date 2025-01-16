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
    return [f for f in directory.rglob('*') if f.is_file() and not f.name.startswith('.')]

def file_hash(file_path, chunk_size=131072):
    hasher = hashlib.blake2b()
    with file_path.open('rb') as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def compare_files(file1, file2, chunk_size=131072):
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
    return True

def find_duplicates(directory):
    files = get_all_files(directory)
    duplicates = []
    checked_files = {}

    def process_file(file1):
        file1_hash = file_hash(file1)
        local_duplicates = []

        if file1_hash in checked_files:
            for file2 in checked_files[file1_hash]:
                if compare_files(file1, file2):
                    local_duplicates.append((file1, file2))
        else:
            checked_files[file1_hash] = []

        checked_files[file1_hash].append(file1)
        return local_duplicates

    max_threads = os.cpu_count() // 2
    with concurrent.futures.ThreadPoolExecutor(max_threads) as executor:
        futures = {executor.submit(process_file, file1): file1 for file1 in files}
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Processing files"):
            duplicates.extend(future.result())

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
    """Convert file size to a human-readable format with 4 significant figures."""
    for unit in ["bytes", "KB", "MB", "GB"]:
        if size_in_bytes < 1024 or unit == "GB":
            return f"{size_in_bytes:.4g} {unit}"
        size_in_bytes /= 1024

def process_subfolders(main_folder):
    subfolders = [f for f in main_folder.iterdir() if f.is_dir()]
    for subfolder in subfolders:
        print(f"\033[92mScanning folder: {subfolder}\033[0m")  # Green for scanning folder
        duplicates = find_duplicates(subfolder)

        if duplicates:
            print("\033[93m\nDuplicate Files Found:\033[0m")  # Yellow for heading
            for index, row in generate_comparison_table(duplicates).iterrows():
                print(f"\033[91mFile 1: {row['File 1 Path']}\033[0m")  # Red for File 1
                print(f"\033[91mFile 2: {row['File 2 Path']}\033[0m")  # Red for File 2
                print(f"    \033[94mSize: {format_file_size(row['File Size (bytes)'])}\033[0m\n")  # Blue with formatted size
        else:
            print("\033[97mNo duplicate files found in the folder.\033[0m")  # White for no duplicates

if __name__ == "__main__":
    folder_path = get_folder_path("Enter the main folder path to check subfolders for duplicates: ")
    process_subfolders(folder_path)
