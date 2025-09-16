# 𐚁 Sombrero

All-in-one tool for solving common issues with Scan-o-Matic projects.

## Features

- Interpolate missing greyscale values when only some scans are missing values.
- Replace missing greyscale values with fixture values.
- Visualize greyscale values directly in the terminal.
- Calculate and warn about high standard deviation in greyscale values.
- Automatically backup original data files before making changes.

## Installation

```bash
pip install git+https://github.com/yourusername/sombrero.git
```

## Usage

`sombrero [OPTIONS] PROJECT_DIR COMMAND [ARGS]...`

Run `sombrero --help` for more information on available commands and options.

### Example

```bash
# Interpolate missing greyscale values
sombrero /path/to/project greyscale interpolate

# Use '--interactive' to choose between average and fixture greyscale values after visualizing them
sombrero /path/to/project greyscale interpolate --interactive

# Visualize greyscale values in the terminal
sombrero /path/to/project greyscale visualize

# Restore original data files from backup
sombrero /path/to/project restore
```
