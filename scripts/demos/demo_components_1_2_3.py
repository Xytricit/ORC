"""
ORC Components 1-2-3 Integration Demo
======================================

Demonstrates the complete pipeline:
1. Component 1: Index files (ParallelIndexer)
2. Component 3: Parse code (PythonParser, JavaScriptParser, TypeScriptParser)
3. Component 2: Store in database (GraphDB)

This shows how all 3 components work together in production.
"""

from pathlib import Path
import tempfile
import sys

# Import all 3 components
sys.path.insert(0, str(Path(__file__).parent / "component1_core_indexing"))
from orc.core.parallel_indexer import ParallelIndexer
from orc.storage.graph_db import GraphDB
from orc.parsers import PythonParser, JavaScriptParser, TypeScriptParser

print("=" * 80)
print("ORC COMPONENTS 1-2-3 INTEGRATION DEMO")
print("=" * 80)
print()

# Create sample files
print("Step 1: Creating sample project...")
print("-" * 80)

temp_dir = Path(tempfile.mkdtemp())
print(f"Project directory: {temp_dir}")

# Sample Python file
python_file = temp_dir / "calculator.py"
python_file.write_text("""
'''Calculator module with various operations.'''

def add(x, y):
    '''Add two numbers.'''
    return x + y

def multiply(x, y):
    '''Multiply two numbers.'''
    return x * y

class Calculator:
    '''Calculator class for complex operations.'''
    
    def __init__(self):
        self.history = []
    
    def calculate(self, operation, a, b):
        if operation == 'add':
            result = add(a, b)
        elif operation == 'multiply':
            result = multiply(a, b)
        else:
            result = 0
        
        self.history.append(result)
        return result

if __name__ == '__main__':
    calc = Calculator()
    print(calc.calculate('add', 5, 3))
""")

# Sample JavaScript file
js_file = temp_dir / "utils.js"
js_file.write_text("""
// Utility functions for the application

function formatNumber(num) {
    return num.toFixed(2);
}

const processData = async (data) => {
    const result = await fetch(data);
    return result.json();
};

class DataProcessor {
    constructor() {
        this.cache = {};
    }
    
    process(data) {
        return formatNumber(data);
    }
}

export { formatNumber, DataProcessor };
export default processData;
""")

# Sample TypeScript file
ts_file = temp_dir / "types.ts"
ts_file.write_text("""
// TypeScript type definitions

interface User {
    id: number;
    name: string;
    email: string;
}

type UserID = string | number;

enum UserRole {
    Admin,
    User,
    Guest
}

function getUser(id: UserID): User {
    return {
        id: 1,
        name: 'John',
        email: 'john@example.com'
    };
}

class UserManager {
    private users: User[] = [];
    
    addUser(user: User): void {
        this.users.push(user);
    }
}

export { User, UserManager };
""")

print(f"✅ Created 3 sample files:")
print(f"   - {python_file.name} (Python)")
print(f"   - {js_file.name} (JavaScript)")
print(f"   - {ts_file.name} (TypeScript)")
print()

# COMPONENT 1: Index files
print("Step 2: Component 1 - Indexing files with ParallelIndexer...")
print("-" * 80)

indexer = ParallelIndexer(
    root_path=temp_dir,
    max_workers=2,
    ignore_patterns=[]  # Don't ignore anything in demo
)

files = indexer._scan_files(extensions=['.py', '.js', '.ts'])
print(f"✅ Found {len(files)} files to parse")
for f in files:
    print(f"   - {f.name}")
print()

# COMPONENT 3: Parse files
print("Step 3: Component 3 - Parsing code with language parsers...")
print("-" * 80)

parsers = {
    '.py': PythonParser(),
    '.js': JavaScriptParser(),
    '.ts': TypeScriptParser()
}

all_results = {}
for file_path in files:
    ext = file_path.suffix
    parser = parsers.get(ext)
    
    if parser:
        print(f"\nParsing {file_path.name} with {parser.__class__.__name__}...")
        result = parser.parse_file(file_path)
        all_results[str(file_path)] = result
        
        # Show what was extracted
        print(f"  ✅ Functions: {len(result['functions'])}")
        for func_id, func_data in result['functions'].items():
            complexity = func_data.get('complexity', 0)
            if complexity > 0:
                print(f"     - {func_data['name']} (complexity: {complexity})")
            else:
                print(f"     - {func_data['name']}")
        
        print(f"  ✅ Classes: {len(result['classes'])}")
        for class_id, class_data in result['classes'].items():
            print(f"     - {class_data['name']} ({len(class_data['methods'])} methods)")
        
        if 'interfaces' in result and result['interfaces']:
            print(f"  ✅ Interfaces: {len(result['interfaces'])}")
            for iface_id in result['interfaces']:
                print(f"     - {result['interfaces'][iface_id]['name']}")
        
        if 'enums' in result and result['enums']:
            print(f"  ✅ Enums: {len(result['enums'])}")

print()

# COMPONENT 2: Store in database
print("Step 4: Component 2 - Storing in GraphDB...")
print("-" * 80)

db = GraphDB(":memory:")  # Use in-memory database for demo

total_functions = 0
total_classes = 0

for file_path, result in all_results.items():
    # Store file metadata
    for fp, file_data in result['files'].items():
        db.store_file(fp, file_data['language'], file_data['loc'])
        print(f"✅ Stored file: {Path(fp).name} ({file_data['language']}, {file_data['loc']} LOC)")
    
    # Store functions
    for func_id, func_data in result['functions'].items():
        db.store_function(
            func_id,
            func_data['name'],
            func_data['file'],
            func_data['line_start'],
            func_data['line_end'],
            func_data.get('complexity', 0),
            func_data.get('code', ''),
            func_data.get('parameters', []),
            func_data.get('calls', []),
            func_data.get('is_exported', False)
        )
        total_functions += 1
    
    # Store classes
    for class_id, class_data in result['classes'].items():
        db.store_class(
            class_id,
            class_data['name'],
            class_data['file'],
            class_data['line_start'],
            class_data['line_end'],
            class_data.get('methods', []),
            class_data.get('base_classes', [])
        )
        total_classes += 1

print(f"\n✅ Stored {total_functions} functions and {total_classes} classes in database")
print()

# Query the database
print("Step 5: Querying the database...")
print("-" * 80)

stats = db.get_statistics()
print(f"✅ Database Statistics:")
print(f"   - Total files: {stats['total_files']}")
print(f"   - Total functions: {stats['total_functions']}")
print(f"   - Total classes: {stats['total_classes']}")
print(f"   - Average complexity: {stats['avg_complexity']}")
print(f"   - Average LOC per file: {stats['avg_loc_per_file']}")
print()

# Find complex functions
print("Finding complex functions (Python only)...")
complex_funcs = db.get_complex_functions(threshold=3)
if complex_funcs:
    print(f"✅ Found {len(complex_funcs)} complex functions:")
    for func in complex_funcs:
        print(f"   - {func['name']}: complexity {func['complexity']} ({Path(func['file']).name})")
else:
    print("   No complex functions found (threshold: 3)")
print()

# Query all functions
print("All functions in database:")
all_funcs = db.query_functions("%", limit=100)
for func in all_funcs:
    lang_marker = "🐍" if 'calculator.py' in func['file'] else "📜"
    print(f"   {lang_marker} {func['name']} ({Path(func['file']).name}:{func['line_start']})")
print()

# Summary
print("=" * 80)
print("INTEGRATION DEMO COMPLETE ✅")
print("=" * 80)
print()
print("Summary:")
print(f"  ✅ Component 1: Indexed {len(files)} files")
print(f"  ✅ Component 3: Parsed all files successfully")
print(f"  ✅ Component 2: Stored {total_functions} functions, {total_classes} classes")
print()
print("All 3 components working together successfully! 🎉")
print()

# Cleanup
db.close()
import shutil
shutil.rmtree(temp_dir, ignore_errors=True)
print("Cleaned up temporary files.")
