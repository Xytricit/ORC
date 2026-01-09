"""
File modification utilities for ORC - handles safe code modifications like
deleting dead code, refactoring, etc.
"""
import ast
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class FileModifier:
    """Utility class for modifying source code files safely."""

    @staticmethod
    def remove_function_from_file(file_path: str, function_name: str) -> bool:
        """
        Remove a function from a Python file.
        
        Args:
            file_path: Path to the Python file
            function_name: Name of the function to remove
            
        Returns:
            True if function was successfully removed, False otherwise
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Find the function definition
            lines = content.splitlines(keepends=True)
            func_node = None
            for node in ast.walk(tree):
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and 
                    node.name == function_name):
                    func_node = node
                    break
            
            if not func_node:
                print(f"Function '{function_name}' not found in {file_path}")
                return False
            
            # Get the start and end line numbers (1-indexed)
            start_line = func_node.lineno - 1  # Convert to 0-indexed
            end_line = getattr(func_node, 'end_lineno', func_node.lineno)  # May not be available in older Python
            
            # If end_lineno is not available, we need to find it differently
            if end_line is None:
                # Find the next function/class definition or end of file
                current_pos = func_node.end_lineno if hasattr(func_node, 'end_lineno') else func_node.lineno
                for next_node in tree.body:
                    if hasattr(next_node, 'lineno') and next_node.lineno > func_node.lineno:
                        end_line = next_node.lineno - 1
                        break
                else:
                    end_line = len(lines)
            else:
                end_line -= 1  # Convert to 0-indexed
            
            # Create new content without the function
            new_lines = lines[:start_line] + lines[end_line + 1:]
            new_content = ''.join(new_lines)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Successfully removed function '{function_name}' from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error removing function '{function_name}' from {file_path}: {e}")
            return False

    @staticmethod
    def remove_class_from_file(file_path: str, class_name: str) -> bool:
        """
        Remove a class from a Python file.
        
        Args:
            file_path: Path to the Python file
            class_name: Name of the class to remove
            
        Returns:
            True if class was successfully removed, False otherwise
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the AST
            tree = ast.parse(content)
            
            # Find the class definition
            lines = content.splitlines(keepends=True)
            class_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == class_name:
                    class_node = node
                    break
            
            if not class_node:
                print(f"Class '{class_name}' not found in {file_path}")
                return False
            
            # Get the start and end line numbers (1-indexed)
            start_line = class_node.lineno - 1  # Convert to 0-indexed
            end_line = getattr(class_node, 'end_lineno', class_node.lineno) - 1  # Convert to 0-indexed
            
            # Create new content without the class
            new_lines = lines[:start_line] + lines[end_line + 1:]
            new_content = ''.join(new_lines)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Successfully removed class '{class_name}' from {file_path}")
            return True
            
        except Exception as e:
            print(f"Error removing class '{class_name}' from {file_path}: {e}")
            return False

    @staticmethod
    def remove_entire_file(file_path: str) -> bool:
        """
        Safely remove an entire file (with confirmation).
        
        Args:
            file_path: Path to the file to remove
            
        Returns:
            True if file was successfully removed, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"File {file_path} does not exist")
                return False
            
            # Confirm deletion
            response = input(f"Are you sure you want to delete {file_path}? (y/N): ")
            if response.lower() != 'y':
                print("Deletion cancelled")
                return False
                
            path.unlink()
            print(f"Successfully removed file {file_path}")
            return True
            
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            return False

    @staticmethod
    def backup_file(file_path: str) -> str:
        """
        Create a backup of the file before modification.
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to the backup file
        """
        original_path = Path(file_path)
        backup_path = original_path.with_suffix(original_path.suffix + '.backup')
        
        # Copy content to backup
        backup_path.write_text(original_path.read_text(encoding='utf-8'), encoding='utf-8')
        print(f"Created backup: {backup_path}")
        return str(backup_path)

    @staticmethod
    def remove_multiple_functions(file_path: str, function_names: List[str]) -> Dict[str, bool]:
        """
        Remove multiple functions from a file.
        
        Args:
            file_path: Path to the Python file
            function_names: List of function names to remove
            
        Returns:
            Dictionary mapping function names to success status
        """
        results = {}
        for func_name in function_names:
            # Create backup only for the first modification
            if not any(results.values()):  # If no successful modifications yet
                FileModifier.backup_file(file_path)
                
            results[func_name] = FileModifier.remove_function_from_file(file_path, func_name)
        
        return results

    @staticmethod
    def remove_unused_imports(file_path: str) -> bool:
        """
        Remove unused imports from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            True if modifications were made, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Parse the AST to identify used names
            tree = ast.parse(original_content)
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Handle attribute access like obj.method
                    if isinstance(node.value, ast.Name):
                        used_names.add(node.value.id)
            
            # Split content into lines
            lines = original_content.splitlines(keepends=True)
            
            # Identify import lines
            import_pattern = re.compile(r'^\s*(import|from\s+\w+)\s+')
            lines_to_remove = set()
            
            for i, line in enumerate(lines):
                if import_pattern.match(line):
                    # Check if this import is actually used
                    # This is a simplified check - a full implementation would be more complex
                    import_match = re.search(r'(?:import|from)\s+([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)*)', line)
                    if import_match:
                        imported_name = import_match.group(1).split('.')[0]
                        if imported_name not in used_names:
                            lines_to_remove.add(i)
            
            # Create new content without unused imports
            new_lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
            new_content = ''.join(new_lines)
            
            # Only write if content changed
            if new_content != original_content:
                FileModifier.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Removed unused imports from {file_path}")
                return True
            else:
                print(f"No unused imports found in {file_path}")
                return False
                
        except Exception as e:
            print(f"Error removing unused imports from {file_path}: {e}")
            return False