import os

def generate_folder_map(folder_path_to_scan, use_tree_chars=True):
    """
    Generates a string representation of the folder structure.

    Args:
        folder_path_to_scan (str): The path to the folder to map.
        use_tree_chars (bool): If True, uses tree-like characters (├──, └──, │).
                               If False, uses simple spaces for indentation.

    Returns:
        str: A string containing the mapped folder structure, or an error message.
    """
    if not os.path.exists(folder_path_to_scan):
        return f"Error: Path '{folder_path_to_scan}' does not exist."
    if not os.path.isdir(folder_path_to_scan):
        return f"Error: Path '{folder_path_to_scan}' is not a directory."

    map_lines = []
    # Get the absolute path to ensure consistency and proper base name
    abs_scan_path = os.path.abspath(folder_path_to_scan)
    # The name of the folder we are starting with (will have 0 indent)
    root_display_name = os.path.basename(abs_scan_path)

    # Special prefixes for tree-like structure
    # These are determined dynamically based on whether an item is the last in its list.
    # The `prefixes` list will hold the appropriate prefix strings for each level.
    
    # Store (path, is_last_directory_in_parent) to help with tree characters
    dir_info_stack = []

    for current_dir_path, sub_dir_names, file_names in os.walk(abs_scan_path, topdown=True):
        # Sort for predictable order - helpful for consistent output and tree chars
        sub_dir_names.sort()
        file_names.sort()

        # Calculate depth relative to the initial scan path
        relative_path = os.path.relpath(current_dir_path, abs_scan_path)

        if relative_path == ".":  # This is the top-level directory itself
            depth = 0
            display_name = root_display_name
            map_lines.append(f"{display_name}/")
        else:
            depth = len(relative_path.split(os.sep))
            display_name = os.path.basename(current_dir_path)
            
            # Determine prefix for the directory itself
            # We need to look at the parent's dir_info_stack
            # This logic for perfect tree chars with os.walk can get complex.
            # For simplicity with os.walk, we might not get perfect '│' continuation
            # without more complex state management.
            # Let's simplify tree chars or use the simpler space indent.

            indent_str = ""
            if use_tree_chars:
                # Basic tree: find parent's last_status
                # This part is tricky with os.walk's flat iteration.
                # A recursive function is often easier for perfect tree chars.
                # For now, let's use a simpler approach for tree chars with os.walk
                if depth > 0:
                    # Simplified tree: assume '│   ' for intermediate, then '├──' or '└──'
                    indent_str = '│   ' * (depth - 1)
                    # To know if current_dir_path is the last in its parent's sub_dir_names,
                    # we'd need to know its parent and that parent's sub_dir_names list.
                    # This is not directly available in the current os.walk iteration.
                    # A common workaround is to check if it's the last one os.walk *would* process
                    # from its parent, but this requires foresight or post-processing.
                    #
                    # Alternative for simpler tree chars:
                    # Just use '└── ' or '├── ' based on whether it's the last *processed* at this depth.
                    # This won't be perfect. For a robust solution, a custom recursive walk is better.
                    #
                    # Let's keep it somewhat simple:
                    # We print dirs as they are encountered by os.walk.
                    # The `sub_dir_names` in the *parent's* iteration determined this.
                    # We don't have direct access to that "is_last" flag here easily.
                    # So, we'll use a generic connector for dirs.
                    indent_str += '└── ' # Or '├── ' -- hard to tell if it's last from parent
                map_lines.append(f"{indent_str}{display_name}/")
            else: # Simple space indentation
                indent_str = "    " * depth
                map_lines.append(f"{indent_str}{display_name}/")


        # Indentation for files/subdirs within this directory
        item_depth = depth + 1
        
        # Combine subdirectories and files to determine last item for tree chars
        all_items_count = len(sub_dir_names) + len(file_names)
        current_item_index = 0

        # Print subdirectories (os.walk will visit them, this is just for display planning)
        # Note: We are printing the *name* of the directory here. os.walk handles traversal.
        # The actual directory content (files, sub-subdirectories) will be printed when
        # os.walk makes that subdirectory the `current_dir_path`.
        # So, we should only print files under `current_dir_path`.
        # The subdirectories themselves will be printed when `os.walk` visits them.

        # Print files in this directory
        for i, f_name in enumerate(file_names):
            is_last_file = (i == len(file_names) - 1)
            
            file_indent_str = ""
            if use_tree_chars:
                file_indent_str = '│   ' * depth
                file_indent_str += '└── ' if is_last_file else '├── '
            else:
                file_indent_str = "    " * item_depth + "- " # Add a dash for files

            map_lines.append(f"{file_indent_str}{f_name}")
        
        # Add a visual separator (blank line with pipe) if this dir has files AND subdirs are coming
        if use_tree_chars and file_names and sub_dir_names:
            map_lines.append('│   ' * depth + '│')


    return "\n".join(map_lines)

def map_folder_recursively(current_path, indent_prefix="", is_last_item=False, use_tree_chars=True):
    """
    A recursive alternative for generating folder map, better for tree characters.
    """
    base_name = os.path.basename(current_path)
    lines = []

    if use_tree_chars:
        connector = "└── " if is_last_item else "├── "
        lines.append(f"{indent_prefix}{connector}{base_name}/")
        new_indent_prefix = indent_prefix + ("    " if is_last_item else "│   ")
    else:
        lines.append(f"{indent_prefix}{base_name}/")
        new_indent_prefix = indent_prefix + "    "

    try:
        entries = sorted(os.listdir(current_path))
    except PermissionError:
        lines.append(f"{new_indent_prefix}└── [Permission Denied]")
        return lines
    except FileNotFoundError:
         lines.append(f"{new_indent_prefix}└── [Not Found - Possibly a broken symlink]")
         return lines


    # Separate directories and files to process directories first (or files, as preferred)
    dirs = []
    files = []
    for entry in entries:
        entry_path = os.path.join(current_path, entry)
        if os.path.isdir(entry_path) and not os.path.islink(entry_path): # Exclude symlinks to dirs for this recursion
            dirs.append(entry)
        elif os.path.isfile(entry_path) or os.path.islink(entry_path): # Include symlinks to files
            files.append(entry)
    
    # Combined list for easier iteration for tree characters
    all_children = dirs + files 
    
    for i, item_name in enumerate(all_children):
        item_path = os.path.join(current_path, item_name)
        is_last_child = (i == len(all_children) - 1)

        if item_name in dirs: # It's a directory
            lines.extend(map_folder_recursively(item_path, new_indent_prefix, is_last_child, use_tree_chars))
        else: # It's a file or a symlink we treat as a file
            if use_tree_chars:
                file_connector = "└── " if is_last_child else "├── "
                lines.append(f"{new_indent_prefix}{file_connector}{item_name}")
            else:
                lines.append(f"{new_indent_prefix}- {item_name}")
    return lines


def generate_folder_map_recursive_wrapper(folder_path_to_scan, use_tree_chars=True):
    if not os.path.exists(folder_path_to_scan):
        return f"Error: Path '{folder_path_to_scan}' does not exist."
    if not os.path.isdir(folder_path_to_scan):
        return f"Error: Path '{folder_path_to_scan}' is not a directory."

    abs_scan_path = os.path.abspath(folder_path_to_scan)
    # The first line is just the root folder name, without tree prefixes
    initial_lines = [f"{os.path.basename(abs_scan_path)}/"]
    # Then recursively map its contents
    child_lines = map_folder_recursively(abs_scan_path, indent_prefix="", is_last_item=True, use_tree_chars=use_tree_chars)
    
    # The recursive function adds the folder name itself with a prefix. We want to adjust the first call's output.
    # The map_folder_recursively is designed to be called for *children*.
    # So, we'll call it for children of abs_scan_path.
    
    output_lines = [f"{os.path.basename(abs_scan_path)}/"] # Start with the root folder name

    try:
        entries = sorted(os.listdir(abs_scan_path))
    except PermissionError:
        output_lines.append("└── [Permission Denied]")
        return "\n".join(output_lines)
    except FileNotFoundError:
        output_lines.append("└── [Not Found - Possibly a broken symlink]")
        return "\n".join(output_lines)


    dirs = []
    files = []
    for entry in entries:
        entry_path = os.path.join(abs_scan_path, entry)
        if os.path.isdir(entry_path) and not os.path.islink(entry_path):
            dirs.append(entry)
        elif os.path.isfile(entry_path) or os.path.islink(entry_path):
            files.append(entry)
    
    all_children = dirs + files

    for i, item_name in enumerate(all_children):
        item_path = os.path.join(abs_scan_path, item_name)
        is_last_child = (i == len(all_children) - 1)
        
        # Initial indent_prefix for top-level children is empty
        indent_prefix_for_children = "" 

        if item_name in dirs:
            output_lines.extend(map_folder_recursively(item_path, indent_prefix_for_children, is_last_child, use_tree_chars))
        else: # File
            if use_tree_chars:
                file_connector = "└── " if is_last_child else "├── "
                output_lines.append(f"{indent_prefix_for_children}{file_connector}{item_name}")
            else:
                output_lines.append(f"{indent_prefix_for_children}    - {item_name}")

    return "\n".join(output_lines)


if __name__ == "__main__":
    folder_to_map = input("Enter the folder path to map: ")

    # Normalize the path (e.g., handles ~ on Unix-like systems)
    folder_to_map = os.path.expanduser(folder_to_map)
    folder_to_map = os.path.normpath(folder_to_map)
    
    print("\n--- Map using os.walk (simpler tree chars) ---")
    # map_string_walk = generate_folder_map(folder_to_map, use_tree_chars=True) # os.walk version
    # print(map_string_walk)
    # Using the simpler space indentation for os.walk as tree chars are hard:
    map_string_walk_simple = generate_folder_map(folder_to_map, use_tree_chars=False)
    print(map_string_walk_simple)


    print("\n--- Map using recursion (better tree chars) ---")
    map_string_recursive = generate_folder_map_recursive_wrapper(folder_to_map, use_tree_chars=True)
    print(map_string_recursive)
    
    print("\n--- Map using recursion (simple spaces) ---")
    map_string_recursive_simple = generate_folder_map_recursive_wrapper(folder_to_map, use_tree_chars=False)
    print(map_string_recursive_simple)


    save_option = input("\nDo you want to save this map to a file? (yes/no): ").strip().lower()
    if save_option == 'yes' or save_option == 'y':
        default_filename = f"{os.path.basename(os.path.abspath(folder_to_map))}_map.txt"
        output_filename = input(f"Enter filename to save (default: {default_filename}): ").strip()
        if not output_filename:
            output_filename = default_filename
        
        # You can choose which map version to save, e.g., the recursive one with tree chars
        map_to_save = map_string_recursive # Or map_string_walk

        try:
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(f"Folder Map for: {os.path.abspath(folder_to_map)}\n")
                f.write("=" * 40 + "\n")
                f.write(map_to_save)
            print(f"Map successfully saved to {output_filename}")
        except IOError as e:
            print(f"Error saving file: {e}")