# TXT to ZWO Converter

A Python script that converts workout files from plain text format to Zwift ZWO format.

> **⚠️ Important Note**: This is intentionally a simple script. Do not over-engineer it. The focus is on reliable text-to-ZWO conversion with basic visualization capabilities.

## Overview

This tool processes workout text files from a queue directory, converts them to ZWO (Zwift Workout) format, generates PNG visualizations, and organizes the files automatically.

## Setup (WSL/Ubuntu)

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Installation

1. Clone or download this repository
2. Navigate to the project directory
3. Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install the project with runtime dependencies
pip install -e .

# Or install with development dependencies (for code quality tools)
pip install -e '.[dev]'
```

**Installation Options:**
- `pip install -e .` - Installs runtime dependencies (matplotlib for PNG generation)
- `pip install -e '.[dev]'` - Includes development tools (black, flake8, mypy, etc.)
- `pip install -r requirements-dev.txt` - Legacy method (still supported)

## Directory Structure

```
zwo-script/
├── queue/                  # Place .txt workout files here for processing
├── zwo/                    # Generated .zwo and .png files are stored here
├── txt/                    # Processed .txt files are moved here
├── convert_txt_to_zwo.py   # Main conversion script
├── pyproject.toml          # Project configuration and dependencies
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies (legacy)
└── README.md               # This file
```

## Usage

### Command Line Options

```bash
# Show help and available options
python3 convert_txt_to_zwo.py --help

# Process all files in queue/ directory (queue mode)
python3 convert_txt_to_zwo.py

# Process a single file (single file mode)
python3 convert_txt_to_zwo.py workout.txt

# Process a single file with path
python3 convert_txt_to_zwo.py /path/to/workout.txt
```

## Basic Usage (Queue Mode)

Process multiple workout files automatically using the queue system:

1. Place your workout text files in the `queue/` directory
2. Run the conversion script:

```bash
python3 convert_txt_to_zwo.py
```

The script will:
- Process all `.txt` files in the `queue/` directory
- Generate corresponding `.zwo` files in the `zwo/` directory
- Generate PNG visualizations showing workout power profile
- Move processed text files to the `txt/` directory

## Basic Usage (Single File)

Process individual workout files directly:

```bash
# Process file in current directory
python3 convert_txt_to_zwo.py my-workout.txt

# Process file with full path
python3 convert_txt_to_zwo.py /home/user/workouts/interval-training.txt

# Process file in subdirectory
python3 convert_txt_to_zwo.py workouts/endurance-ride.txt
```

In single file mode:
- Output files (`.zwo` and `.png`) are created in the same directory as the input file
- If no path is specified, files are created in the current directory
- No file movement occurs (original `.txt` file remains in place)

### Input Format

Text files should contain workout instructions with the following format:

```
5min from 40 to 105% FTP
2min @ 50% FTP
5min free ride
4x 30sec @ 105rpm, 72% FTP,
30sec @ 90rpm, 65% FTP
40sec @ 95rpm, 72% FTP
6min @ 70rpm, 74% FTP
3min free ride
2min from 65 to 55% FTP
```

Supported patterns:
- **Duration**: `3min`, `30sec`, `40sec`
- **Power zones**: `72% FTP`, `65% FTP`
- **Cadence**: `105rpm`, `90rpm`
- **Intervals**: `4x 30sec @ 105rpm, 72% FTP`
- **Stepped ramps**: `5min from 40 to 105% FTP` (generates multiple power steps)
- **Free ride**: `3min free ride` (user-controlled power segments)

## Development

### Code Quality Tools

The project includes comprehensive code quality checking tools:

#### Install Development Dependencies

Install the project with all development dependencies:

```bash
source .venv/bin/activate
pip install -e '.[dev]'
```

Dependencies include:
- **Runtime**: matplotlib (for PNG generation)
- **Code quality tools**: flake8, black, isort, mccabe, mypy, bandit, pydocstyle

#### Code Quality Checks

The project maintains strict code quality standards while keeping things simple:

```bash
# Run all checks in sequence
isort convert_txt_to_zwo.py
black convert_txt_to_zwo.py
flake8 convert_txt_to_zwo.py --max-line-length=88 --max-complexity=10
mypy convert_txt_to_zwo.py
bandit convert_txt_to_zwo.py
pydocstyle convert_txt_to_zwo.py
```

**Quality Standards:**
- **Line length**: 88 characters (Black standard)
- **Complexity**: Maximum cyclomatic complexity of 10
- **Import sorting**: Alphabetical with proper grouping
- **Code formatting**: Black automatic formatting
- **Type checking**: Static type analysis with mypy
- **Security scanning**: Python security linting with bandit
- **Documentation**: PEP 257 docstring conventions

#### Individual Tool Usage

**Black (Code Formatting)**
```bash
# Check formatting
black --check convert_txt_to_zwo.py

# Format code
black convert_txt_to_zwo.py
```

**isort (Import Sorting)**
```bash
# Check import order
isort --check-only --diff convert_txt_to_zwo.py

# Sort imports
isort convert_txt_to_zwo.py
```

**flake8 (Linting & Style)**
```bash
# Full check with complexity
flake8 convert_txt_to_zwo.py --max-line-length=88 --max-complexity=10
```

**mypy (Type Checking)**
```bash
# Static type analysis
mypy convert_txt_to_zwo.py
```

**bandit (Security Scanning)**
```bash
# Security linting
bandit convert_txt_to_zwo.py
```

**pydocstyle (Documentation)**
```bash
# Docstring convention checking
pydocstyle convert_txt_to_zwo.py
```

### PEP8 Compliance

The code follows PEP8 standards with these configurations:
- Maximum line length: 88 characters
- Maximum cyclomatic complexity: 10
- Automatic code formatting with Black
- Sorted imports with isort
- Comprehensive linting with flake8


## Contributing

**Key Principles:**
1. **Keep it simple** - This is a focused utility script, not a complex application
2. **Follow PEP8 standards** - Use the included quality tools
3. **Test thoroughly** - Verify with actual workout files
4. **No feature creep** - Resist adding unnecessary complexity

**Before submitting changes:**
```bash
# Run all quality checks
isort convert_txt_to_zwo.py
black convert_txt_to_zwo.py  
flake8 convert_txt_to_zwo.py --max-line-length=88 --max-complexity=10
mypy convert_txt_to_zwo.py
bandit convert_txt_to_zwo.py
pydocstyle convert_txt_to_zwo.py

# Test functionality
python3 convert_txt_to_zwo.py  # with test files in queue/
```

**What NOT to add:**
- Complex configuration systems
- Database dependencies
- Web interfaces
- Advanced parsing beyond the current format
- Heavyweight frameworks

The goal is a reliable, maintainable script that does one thing well: convert text workouts to ZWO format with basic visualizations.

## Performance & Optimization

This script has been analyzed for performance optimization opportunities while maintaining the core philosophy of intentional simplicity.

### What We Optimized

**Pre-compiled Regex Patterns**: All regex patterns are compiled once at startup and stored in a central `REGEX_PATTERNS` dictionary. This improves code readability by giving patterns descriptive names (`'duration'`, `'power_ftp'`, `'rpm'`) and makes maintenance easier by centralizing pattern definitions.

**File I/O Operations**: Changed from `f.readlines()` to direct file iteration for more idiomatic Python and slightly better memory efficiency.

### What We Didn't Optimize (And Why)

**PNG Generation**: Matplotlib rendering accounts for ~90% of execution time, but we kept it unchanged because:
- The current implementation produces professional-quality visualizations
- Optimization would require significant complexity for minimal real-world benefit
- Typical workout files process in ~1 second, which is already fast enough

**Complex Data Structures**: We avoided micro-optimizations like changing dictionaries to if-elif chains because:
- The performance gain is negligible for typical file sizes
- The original code is more readable and maintainable
- Premature optimization contradicts the simplicity philosophy

**Batch Processing**: We didn't add complex batching or parallel processing because:
- Single-file processing is already fast enough
- Added complexity would make the tool harder to understand and maintain
- The simple file-based workflow is more reliable and user-friendly

### Performance Results

For typical workout files (5-25 lines), processing time is ~1 second regardless of optimization level. The bottleneck is PNG visualization rendering, not text processing. The optimizations we implemented improve code quality without sacrificing simplicity.

## Code Quality & Maintainability Improvements

The script has been enhanced for better readability, maintainability, and code quality while preserving its intentional simplicity. These improvements make the code easier to understand, modify, and debug without adding unnecessary complexity.

### Implemented Improvements

**Constants Extraction**: All magic numbers and hardcoded values have been extracted into named constants at the top of the file:

```python
# Workout processing constants
DEFAULT_RECOVERY_POWER = 0.6
RAMP_SEGMENT_DURATION = 15  # seconds per step in ramps
PERCENTAGE_TO_DECIMAL = 100.0
MINUTES_TO_SECONDS = 60

# PNG generation constants
FIGURE_SIZE = (12, 6)
PNG_DPI = 300
FONT_SIZE_AXIS = 12
```

This eliminates scattered magic numbers throughout the code and makes configuration changes much easier.

**Centralized Power Zone Configuration**: Power zones are now defined in a single, comprehensive data structure:

```python
POWER_ZONES: Dict[str, Dict[str, Union[Tuple[float, float], str]]] = {
    "recovery": {"range": (0, 0.55), "color": "#4A90E2", "name": "Recovery"},
    "endurance": {"range": (0.55, 0.75), "color": "#7ED321", "name": "Endurance"},
    "tempo": {"range": (0.75, 0.90), "color": "#F5A623", "name": "Tempo"},
    # ... additional zones
}
```

This makes it easy to modify training zones, colors, or add new zones without hunting through the codebase.

**Enhanced Error Handling**: Added a dedicated validation function with user-friendly error messages:

```python
def validate_workout_file(file_path: Path) -> None:
    if not file_path.exists():
        print(f"Error: Workout file '{file_path}' not found.")
        print("Please check the file path and try again.")
        sys.exit(1)
```

Users now receive clear, actionable error messages instead of cryptic Python exceptions.

**Comprehensive Documentation**: Added docstring examples to key parsing functions:

```python
def parse_duration_to_seconds(duration_str: str) -> int:
    """Convert duration string like '3min', '30sec' to seconds.
    
    Examples:
        >>> parse_duration_to_seconds('3min')
        180
        >>> parse_duration_to_seconds('90sec')
        90
    """
```

This makes the code self-documenting and easier for new contributors to understand.

**Pre-compiled Regex Patterns**: All regex patterns are compiled once and stored with descriptive names:

```python
REGEX_PATTERNS = {
    "duration": re.compile(r"(\d+)(min|sec)"),
    "power_ftp": re.compile(r"(\d+)%\s*FTP"),
    "cadence": re.compile(r"(\d+)rpm"),
}
```

This improves both performance and code readability by giving patterns meaningful names.

### Quality Benefits

These improvements provide several key benefits:

- **Maintainability**: Constants and centralized configuration make future changes easier
- **Readability**: Self-documenting code with clear naming and examples
- **Debugging**: Better error messages help users resolve issues quickly
- **Consistency**: Standardized patterns throughout the codebase
- **Testing**: Clearer functions with examples make testing more straightforward

### What We Avoided

In keeping with the simplicity philosophy, we deliberately avoided:

- **Over-abstraction**: No unnecessary classes or complex inheritance hierarchies
- **Configuration bloat**: Simple constants instead of complex config systems  
- **Premature optimization**: Focus on clarity over micro-optimizations
- **Feature creep**: Improvements enhance existing functionality without adding scope

The result is code that's significantly more maintainable and readable while remaining true to the project's core principle of intentional simplicity.