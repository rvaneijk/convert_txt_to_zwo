# Claude Code Memory - TXT to ZWO Converter

This file provides essential context for Claude Code to work effectively with this project.

## Project Overview

**TXT to ZWO Converter** - A Python script that converts workout files from plain text format to Zwift ZWO format with PNG visualizations.

**Core Philosophy**: Intentionally simple script. Do not over-engineer it. Focus on reliable text-to-ZWO conversion with basic visualization capabilities.

## Environment Setup

### Prerequisites
- Python 3.9 or higher
- Virtual environment at `.venv/`

### Installation Commands
```bash
# Activate virtual environment (ALWAYS do this first)
source .venv/bin/activate

# Install runtime dependencies
pip install -e .

# Install with development tools
pip install -e '.[dev]'
```

### Key Dependencies
- **Runtime**: matplotlib (for PNG generation)
- **Development**: flake8, black, isort, mypy, bandit, pydocstyle

## Quality Assurance Commands

**ALWAYS run these quality checks before commits:**

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run all quality checks in sequence
isort convert_txt_to_zwo.py
black convert_txt_to_zwo.py
flake8 convert_txt_to_zwo.py --max-line-length=88 --max-complexity=10
mypy convert_txt_to_zwo.py
bandit convert_txt_to_zwo.py
pydocstyle convert_txt_to_zwo.py
```

## Project Structure

```
zwo-script/
├── queue/                  # Input: .txt workout files for batch processing
├── zwo/                    # Output: Generated .zwo and .png files (batch mode)
├── txt/                    # Archive: Processed .txt files moved here (batch mode)
├── convert_txt_to_zwo.py   # Main conversion script
├── pyproject.toml          # Project configuration and dependencies
├── requirements.txt        # Runtime dependencies only
└── CLAUDE.md               # This file
```

## Usage Modes

### Queue Mode (Default)
```bash
python3 convert_txt_to_zwo.py
```
- Processes all .txt files in queue/ directory
- Outputs to zwo/ directory
- Moves processed files to txt/ directory

### Single File Mode
```bash
python3 convert_txt_to_zwo.py workout.txt
python3 convert_txt_to_zwo.py path/to/workout.txt
```
- Processes specified file
- Outputs .zwo and .png to same directory as input file
- Original .txt file remains in place

## Code Quality Standards

### Recent Improvements (Completed)
- ✅ **Constants Extraction**: All magic numbers moved to named constants
- ✅ **Power Zone Configuration**: Centralized POWER_ZONES dictionary
- ✅ **Enhanced Error Handling**: User-friendly validation messages
- ✅ **Documentation**: Docstring examples for key functions
- ✅ **Regex Patterns**: Pre-compiled patterns with descriptive names

### Quality Metrics
- **Line length**: 88 characters maximum
- **Complexity**: Cyclomatic complexity ≤ 10
- **Functions**: 13 functions, 622 lines (reasonable size)
- **Type checking**: Full mypy compliance
- **Security**: Bandit security scanning passed

## Common Issues & Solutions

### Missing Dependencies
If you see `ModuleNotFoundError: No module named 'matplotlib'`:
```bash
source .venv/bin/activate
pip install -e .
```

### Quality Check Failures
If quality tools aren't found:
```bash
source .venv/bin/activate
pip install -e '.[dev]'
```

### Testing Functionality
Quick test with existing test file:
```bash
python3 convert_txt_to_zwo.py test_quality.txt
```

## Development Principles

### DO
- Keep it simple and focused
- Follow PEP8 standards
- Use the quality tools religiously
- Test with actual workout files
- Extract constants instead of magic numbers
- Provide clear error messages

### DON'T
- Over-engineer or add complexity
- Add unnecessary features (feature creep)
- Skip quality checks
- Create heavyweight frameworks
- Add database dependencies
- Implement web interfaces

## File Format Support

### Input (.txt files)
```
3min from 50 to 70% FTP
2min @ 60% FTP
4x 30sec @ 105rpm, 85% FTP,
30sec @ 90rpm, 65% FTP
3min free ride
```

### Output
- `.zwo` files (Zwift workout format)
- `.png` files (Power profile visualization)

## Performance Notes

- Processing time: ~1 second per workout file
- Bottleneck: PNG generation (matplotlib rendering ~90%)
- Text processing: Optimized with pre-compiled regex patterns
- File I/O: Efficient direct iteration

## Quick Reference

```bash
# Setup
source .venv/bin/activate

# Run quality checks
isort convert_txt_to_zwo.py && black convert_txt_to_zwo.py && flake8 convert_txt_to_zwo.py --max-line-length=88 --max-complexity=10 && mypy convert_txt_to_zwo.py && bandit convert_txt_to_zwo.py && pydocstyle convert_txt_to_zwo.py

# Test functionality
python3 convert_txt_to_zwo.py test_quality.txt

# Help
python3 convert_txt_to_zwo.py --help
```

---

*This file helps Claude Code understand the project context, setup requirements, and quality standards to avoid setup issues and maintain consistency.*