#!/usr/bin/env python3
"""
Convert workout text files to Zwift ZWO format with PNG visualization.

Author: Blaeu Privacy Response Team
Copyright: Copyright © 2019 - 2025 Team Blaeu. All Rights Reserved.
License: CC BY 4.0
"""

import argparse
import re
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import matplotlib.patches as patches
import matplotlib.pyplot as plt

# Suppress numpy warnings in WSL environments
warnings.filterwarnings("ignore", message=".*does not match any known type.*")

# Pre-compiled regex patterns for better readability and maintainability
REGEX_PATTERNS = {
    "digits": re.compile(r"\d+"),
    "duration": re.compile(r"(\d+)(min|sec)"),
    "power_ftp": re.compile(r"(\d+)%\s*FTP"),
    "from_power": re.compile(r"from\s+(\d+)"),
    "to_power": re.compile(r"to\s+(\d+)%"),
    "percentage": re.compile(r"(\d+)%"),
    "rpm": re.compile(r"(\d+)rpm"),
    "repeat": re.compile(r"(\d+)x\s+"),
}

# Workout processing constants
DEFAULT_RECOVERY_POWER = 0.6
DEFAULT_INTERVAL_OFF_POWER = 0.55
RAMP_SEGMENT_DURATION = 15  # seconds per step in ramps
FREE_RIDE_VISUALIZATION_POWER = 0.65
PERCENTAGE_TO_DECIMAL = 100.0
MINUTES_TO_SECONDS = 60

# PNG generation constants
FIGURE_SIZE = (12, 6)
MAX_POWER_DISPLAY = 1.5  # 150% FTP
PNG_DPI = 300
LONG_WORKOUT_THRESHOLD = 600  # seconds (10 minutes)
SHORT_WORKOUT_TICK_INTERVAL = 60  # Every minute
LONG_WORKOUT_TICK_INTERVAL = 300  # Every 5 minutes

# PNG styling constants
FREE_RIDE_ALPHA = 0.6
STEADY_STATE_ALPHA = 0.8
GRID_ALPHA = 0.3
RECT_LINEWIDTH = 1
FREE_RIDE_LINEWIDTH = 2
FONT_SIZE_AXIS = 12
FONT_SIZE_TITLE = 14
FONT_SIZE_LEGEND = 9
FONT_SIZE_FREE_RIDE_TEXT = 8

# Power zone configuration
POWER_ZONES: Dict[str, Dict[str, Union[Tuple[float, float], str]]] = {
    "recovery": {"range": (0, 0.55), "color": "#4A90E2", "name": "Recovery"},
    "endurance": {"range": (0.55, 0.75), "color": "#7ED321", "name": "Endurance"},
    "tempo": {"range": (0.75, 0.90), "color": "#F5A623", "name": "Tempo"},
    "threshold": {"range": (0.90, 1.05), "color": "#D0021B", "name": "Threshold"},
    "vo2max": {"range": (1.05, 1.20), "color": "#9013FE", "name": "VO2Max"},
    "neuromuscular": {
        "range": (1.20, 2.0),
        "color": "#BD10E0",
        "name": "Neuromuscular",
    },
}
DEFAULT_HIGH_POWER_COLOR = "#50E3C2"  # Teal for very high power


def validate_workout_file(file_path: Path) -> None:
    """Validate workout file exists and has correct extension.

    Args:
        file_path: Path to the workout file to validate

    Raises:
        SystemExit: If file doesn't exist or has wrong extension
    """
    if not file_path.exists():
        print(f"Error: Workout file '{file_path}' not found.")
        print("Please check the file path and try again.")
        sys.exit(1)

    if file_path.suffix.lower() != ".txt":
        print(f"Error: Expected .txt file, got '{file_path.suffix}'")
        print("Workout files must have .txt extension.")
        sys.exit(1)


def parse_duration_to_seconds(duration_str: str) -> int:
    """Convert duration string like '3min', '30sec' to seconds.

    Args:
        duration_str: Duration string like '3min', '30sec', '90sec'

    Returns:
        Duration in seconds

    Examples:
        >>> parse_duration_to_seconds('3min')
        180
        >>> parse_duration_to_seconds('90sec')
        90
        >>> parse_duration_to_seconds('5min')
        300
    """
    if "min" in duration_str:
        match = REGEX_PATTERNS["digits"].search(duration_str)
        return int(match.group()) * MINUTES_TO_SECONDS if match else 0
    elif "sec" in duration_str:
        match = REGEX_PATTERNS["digits"].search(duration_str)
        return int(match.group()) if match else 0
    return 0


def parse_power_percentage(power_str: str) -> float:
    """Convert power percentage like '72% FTP' to decimal like 0.72.

    Args:
        power_str: Power string containing percentage like '85% FTP', '120% FTP'

    Returns:
        Power as decimal (e.g., 0.85 for 85%)

    Examples:
        >>> parse_power_percentage('85% FTP')
        0.85
        >>> parse_power_percentage('120% FTP')
        1.2
        >>> parse_power_percentage('invalid')
        0.6
    """
    match = REGEX_PATTERNS["percentage"].search(power_str)
    if match:
        return int(match.group(1)) / PERCENTAGE_TO_DECIMAL
    return DEFAULT_RECOVERY_POWER


def parse_cadence(line: str) -> Optional[int]:
    """Extract cadence from line like '@ 105rpm'.

    Args:
        line: Workout line that may contain cadence specification

    Returns:
        Cadence in RPM if found, None otherwise

    Examples:
        >>> parse_cadence('4x 30sec @ 105rpm, 85% FTP')
        105
        >>> parse_cadence('5min @ 90rpm, 70% FTP')
        90
        >>> parse_cadence('3min @ 85% FTP')
        None
    """
    match = REGEX_PATTERNS["rpm"].search(line)
    if match:
        return int(match.group(1))
    return None


def create_zwo_header(workout_name: str) -> List[str]:
    """Create ZWO file header."""
    return [
        "<workout_file>",
        "    <author>Converted from TXT</author>",
        f"    <name>{workout_name}</name>",
        "    <description>Auto-converted workout from text format</description>",
        "    <sportType>bike</sportType>",
        "    <tags/>",
        "    <workout>",
    ]


def process_workout_line(line: str) -> Optional[str]:
    """Process a single workout line and return ZWO element."""
    if not line:
        return None

    duration_match = REGEX_PATTERNS["duration"].search(line)
    if not duration_match:
        return None

    duration = parse_duration_to_seconds(duration_match.group(0))
    cadence = parse_cadence(line)
    cadence_attr = f' Cadence="{cadence}"' if cadence else ""

    # Check for free ride first
    if "free ride" in line.lower():
        return f'        <FreeRide Duration="{duration}"{cadence_attr} />'

    # Check if we have power percentage for other segment types
    power_match = REGEX_PATTERNS["power_ftp"].search(line)
    if not power_match:
        return None

    # Check for ramp first (before parsing general power)
    if "from" in line and "to" in line:
        # Ramp element - create stepped intervals to match PNG visualization
        from_power_match = REGEX_PATTERNS["from_power"].search(line)
        to_power_match = REGEX_PATTERNS["to_power"].search(line)
        if from_power_match and to_power_match:
            from_power = int(from_power_match.group(1)) / PERCENTAGE_TO_DECIMAL
            to_power = int(to_power_match.group(1)) / PERCENTAGE_TO_DECIMAL

            # Create stepped ramp with consistent segment duration (matching PNG logic)
            segment_duration = RAMP_SEGMENT_DURATION
            steps = max(1, duration // segment_duration)
            step_duration = duration / steps

            # Generate multiple SteadyState intervals for stepped ramp
            ramp_elements = []
            for i in range(steps):
                # Linear interpolation between from_power and to_power
                if steps == 1:
                    power = (from_power + to_power) / 2  # Average if only one step
                else:
                    power = from_power + (to_power - from_power) * (i / (steps - 1))

                ramp_elements.append(
                    f'        <SteadyState Duration="{int(step_duration)}" '
                    f'Power="{power:.3f}"{cadence_attr} />'
                )

            return "\n".join(ramp_elements)

    # Parse power for non-ramp elements
    power = parse_power_percentage(line)

    repeat_match = REGEX_PATTERNS["repeat"].search(line)
    if repeat_match:
        # Interval element
        repeat_count = int(repeat_match.group(1))
        return (
            f'        <IntervalsT Repeat="{repeat_count}" '
            f'OnDuration="{duration}" OffDuration="{duration}" '
            f'OnPower="{power}" OffPower="{DEFAULT_INTERVAL_OFF_POWER}"'
            f"{cadence_attr} />"
        )

    # Steady state element
    return (
        f'        <SteadyState Duration="{duration}" '
        f'Power="{power}"{cadence_attr} />'
    )


def convert_txt_to_zwo(
    txt_file_path: Path, output_dir: Path, generate_png: bool = True
) -> Tuple[Path, Optional[Path]]:
    """Convert a single txt workout file to zwo format and optionally generate PNG."""
    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    workout_name = Path(txt_file_path).stem
    zwo_content = create_zwo_header(workout_name)

    # Process each line
    for line in lines:
        element = process_workout_line(line)
        if element:
            zwo_content.append(element)

    zwo_content.extend(["    </workout>", "</workout_file>"])

    # Write ZWO file
    output_file = Path(output_dir) / f"{workout_name}.zwo"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(zwo_content))

    # Generate PNG if requested
    png_file = None
    if generate_png:
        try:
            workout_segments = parse_workout_segments(lines)
            png_file = generate_workout_png(workout_segments, workout_name, output_dir)
        except Exception as e:
            print(f"Warning: Could not generate PNG for {workout_name}: {e}")

    return output_file, png_file


def generate_workout_png(
    workout_data: List[Dict[str, Any]], workout_name: str, output_dir: Path
) -> Path:
    """Generate a PNG visualization of the workout."""
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # Set up the plot
    ax.set_xlim(0, sum(segment["duration"] for segment in workout_data))
    ax.set_ylim(0, MAX_POWER_DISPLAY)

    def get_power_color(power: float) -> str:
        """Get color for power level based on training zones."""
        for zone_data in POWER_ZONES.values():
            min_power, max_power = zone_data["range"]  # type: ignore
            if min_power <= power < max_power:
                return str(zone_data["color"])
        return DEFAULT_HIGH_POWER_COLOR

    current_time = 0

    for segment in workout_data:
        duration = segment["duration"]
        segment_type = segment.get("type", "steady")
        power_low = segment.get(
            "power_low", segment.get("power", DEFAULT_RECOVERY_POWER)
        )
        power_high = segment.get(
            "power_high", segment.get("power", DEFAULT_RECOVERY_POWER)
        )

        if segment_type == "free_ride":
            # Free ride segment with distinct styling
            rect = patches.Rectangle(
                (current_time, 0),
                duration,
                power_low,  # Use the neutral power for height
                linewidth=FREE_RIDE_LINEWIDTH,
                edgecolor="black",
                facecolor="lightgray",
                alpha=FREE_RIDE_ALPHA,
                hatch="///",  # Diagonal lines pattern
            )
            ax.add_patch(rect)
            # Add "FREE RIDE" text in the middle of the segment
            ax.text(
                current_time + duration / 2,
                power_low / 2,
                "FREE RIDE",
                ha="center",
                va="center",
                fontsize=FONT_SIZE_FREE_RIDE_TEXT,
                fontweight="bold",
                color="black",
            )
        elif power_low == power_high:
            # Steady state segment
            color = get_power_color(power_low)
            rect = patches.Rectangle(
                (current_time, 0),
                duration,
                power_low,
                linewidth=RECT_LINEWIDTH,
                edgecolor="white",
                facecolor=color,
                alpha=STEADY_STATE_ALPHA,
            )
            ax.add_patch(rect)
        else:
            # Ramp segment (warmup/cooldown)
            # Create stepped ramp effect with consistent segments
            segment_duration = RAMP_SEGMENT_DURATION
            steps = max(1, duration // segment_duration)
            step_duration = duration / steps

            for i in range(steps):
                step_time = current_time + i * step_duration
                # Linear interpolation between power_low and power_high
                power = power_low + (power_high - power_low) * (i / (steps - 1))
                color = get_power_color(power)

                rect = patches.Rectangle(
                    (step_time, 0),
                    step_duration,
                    power,
                    linewidth=RECT_LINEWIDTH,
                    edgecolor="white",
                    facecolor=color,
                    alpha=STEADY_STATE_ALPHA,
                )
                ax.add_patch(rect)

        current_time += duration

    # Formatting
    ax.set_xlabel("Time (seconds)", fontsize=FONT_SIZE_AXIS)
    ax.set_ylabel("Power (% FTP)", fontsize=FONT_SIZE_AXIS)
    ax.set_title(
        f"Workout: {workout_name}", fontsize=FONT_SIZE_TITLE, fontweight="bold"
    )

    # Convert y-axis to percentage
    ax.set_ylim(0, MAX_POWER_DISPLAY)
    y_ticks = [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5]
    y_labels = [f"{int(y*100)}%" for y in y_ticks]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)

    # Format x-axis to show time in minutes
    total_seconds = sum(segment["duration"] for segment in workout_data)
    if total_seconds > LONG_WORKOUT_THRESHOLD:
        x_ticks = range(0, int(total_seconds) + 1, LONG_WORKOUT_TICK_INTERVAL)
        x_labels = [f"{x//60}m" for x in x_ticks]
    else:
        x_ticks = range(0, int(total_seconds) + 1, SHORT_WORKOUT_TICK_INTERVAL)
        x_labels = [f"{x//60}m" for x in x_ticks]

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_labels)

    # Grid and styling
    ax.grid(True, alpha=GRID_ALPHA)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Add power zone legend
    legend_elements = []
    for zone_data in POWER_ZONES.values():
        min_power, max_power = zone_data["range"]  # type: ignore
        min_percent = int(min_power * 100)
        max_percent = int(max_power * 100) if max_power < 2.0 else "120+"
        label = f"{str(zone_data['name'])} ({min_percent}-{max_percent}%)"
        legend_elements.append(
            patches.Patch(color=str(zone_data["color"]), label=label)
        )

    ax.legend(handles=legend_elements, loc="upper right", fontsize=FONT_SIZE_LEGEND)

    # Save the plot
    plt.tight_layout()
    png_file = Path(output_dir) / f"{workout_name}.png"
    plt.savefig(png_file, dpi=PNG_DPI, bbox_inches="tight", facecolor="white")
    plt.close()

    return png_file


def parse_workout_segments(lines: List[str]) -> List[Dict[str, Any]]:
    """Parse workout lines and return structured data for visualization."""
    segments = []

    for line in lines:
        if not line:
            continue

        duration_match = REGEX_PATTERNS["duration"].search(line)
        if not duration_match:
            continue

        duration = parse_duration_to_seconds(duration_match.group(0))
        cadence = parse_cadence(line)

        # Check for free ride first
        if "free ride" in line.lower():
            segments.append(
                {
                    "duration": duration,
                    "power": FREE_RIDE_VISUALIZATION_POWER,  # Neutral power
                    "cadence": cadence,
                    "type": "free_ride",
                }
            )
            continue

        power_match = REGEX_PATTERNS["power_ftp"].search(line)
        if duration_match and power_match:
            duration = parse_duration_to_seconds(duration_match.group(0))
            power = parse_power_percentage(line)
            cadence = parse_cadence(line)

            repeat_match = REGEX_PATTERNS["repeat"].search(line)
            if repeat_match:
                # Interval segment
                repeat_count = int(repeat_match.group(1))
                on_duration = duration
                off_duration = duration  # Simplified assumption
                on_power = power
                off_power = DEFAULT_INTERVAL_OFF_POWER

                # Add on/off segments for each repeat
                for _ in range(repeat_count):
                    segments.append(
                        {
                            "duration": on_duration,
                            "power": on_power,
                            "cadence": cadence,
                            "type": "interval_on",
                        }
                    )
                    segments.append(
                        {
                            "duration": off_duration,
                            "power": off_power,
                            "cadence": None,
                            "type": "interval_off",
                        }
                    )
            else:
                if "from" in line and "to" in line:
                    # Ramp segment
                    from_power_match = REGEX_PATTERNS["from_power"].search(line)
                    to_power_match = REGEX_PATTERNS["to_power"].search(line)
                    if from_power_match and to_power_match:
                        from_power = (
                            int(from_power_match.group(1)) / PERCENTAGE_TO_DECIMAL
                        )
                        to_power = int(to_power_match.group(1)) / PERCENTAGE_TO_DECIMAL

                        segments.append(
                            {
                                "duration": duration,
                                "power_low": from_power,
                                "power_high": to_power,
                                "cadence": cadence,
                                "type": "ramp",
                            }
                        )
                else:
                    # Steady state segment
                    segments.append(
                        {
                            "duration": duration,
                            "power": power,
                            "cadence": cadence,
                            "type": "steady",
                        }
                    )

    return segments


def process_single_file(file_path: str) -> None:
    """Process a single txt file specified by path."""
    txt_file = Path(file_path)

    # Validate file exists and has .txt extension
    validate_workout_file(txt_file)

    # Determine output directory (same as input file, or current dir if no path)
    if txt_file.parent == Path("."):
        # File is in current directory or just filename provided
        output_dir = Path(".")
    else:
        # File has a path, use that directory
        output_dir = txt_file.parent

    print(f"Processing: {txt_file}")

    try:
        zwo_file, png_file = convert_txt_to_zwo(txt_file, output_dir, True)
        print(f"Created: {zwo_file}")
        if png_file:
            print(f"Generated: {png_file}")
    except Exception as e:
        print(f"Error processing {txt_file.name}: {e}")
        sys.exit(1)


def process_queue() -> None:
    """Process all txt files in the queue directory."""
    queue_dir = Path("./queue")
    zwo_dir = Path("./zwo")
    txt_dir = Path("./txt")

    zwo_dir.mkdir(exist_ok=True)
    txt_dir.mkdir(exist_ok=True)

    txt_files = [f for f in queue_dir.glob("*.txt")]

    if not txt_files:
        print("No txt files found in queue directory")
        return

    for txt_file in txt_files:
        print(f"Processing: {txt_file.name}")

        try:
            zwo_file, png_file = convert_txt_to_zwo(txt_file, zwo_dir, True)
            print(f"Created: {zwo_file}")
            if png_file:
                print(f"Generated: {png_file}")

            completed_file = txt_dir / txt_file.name
            txt_file.rename(completed_file)
            print(f"Moved to: {completed_file}")

        except Exception as e:
            print(f"Error processing {txt_file.name}: {e}")


def main() -> None:
    """Parse arguments and execute conversion process."""
    parser = argparse.ArgumentParser(
        description="Convert workout text files to Zwift ZWO format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage Modes:

  Queue Mode (no arguments):
    python3 convert_txt_to_zwo.py
    - Processes all .txt files in queue/ directory
    - Outputs .zwo and .png files to zwo/ directory
    - Moves processed .txt files to txt/ directory

  Single File Mode:
    python3 convert_txt_to_zwo.py workout.txt
    python3 convert_txt_to_zwo.py path/to/file.txt
    - Processes specified .txt file
    - Outputs .zwo and .png files to same directory as input file
    - Original .txt file remains in place
        """,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Single .txt file to process (alternative to queue processing)",
    )

    args = parser.parse_args()

    if args.file:
        # Single file mode
        process_single_file(args.file)
    else:
        # Queue mode
        process_queue()


if __name__ == "__main__":
    main()
