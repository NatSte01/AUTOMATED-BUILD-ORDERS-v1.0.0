# AUTOMATED-BUILD-ORDERS-v1.0.0

An automated build order optimization system for Beyond All Reason (BAR) game, specifically designed for the **Cortex faction ONLY**.

## Overview

This project provides an intelligent build order optimization system that calculates optimal construction sequences for units and buildings in Beyond All Reason. The system analyzes resource costs (metal, energy), build times, and dependencies to generate efficient build orders that maximize economic growth and strategic advantage.

## Core Features

- **Automated Build Order Generation**: Creates optimized construction sequences
- **Resource Management**: Tracks metal, energy, and buildpower requirements
- **Dependency Resolution**: Handles unit prerequisites and technology tree progression
- **Multi-objective Optimization**: Balances economy, military, and infrastructure needs
- **Real-time Strategy Planning**: Adapts build orders based on game state

## Project Structure

### Main Program
- **`limited_buildings_main.py`** - Core optimization engine containing:
  - Unit database with costs, build times, and capabilities
  - Genetic algorithm for build order optimization
  - Resource simulation and tracking
  - Build dependency management

- **`path_maker.py`** - Pathfinding and spatial optimization utilities

### Data Processing Pipeline (Planned)

The following files are intended to process and format unit data from the game's Lua definition files:

- **`core_units_data.py`** - Core unit data extraction and processing
- **`game_date.py`** - Game timing and progression data handling  
- **`get_data.py`** - Data extraction utilities from Lua files
- **`sample.py`** - Sample data generation and testing utilities
- **`tech_tree.py`** - Technology tree and dependency analysis
- **`unitDefRenames.lua`** - Unit definition renaming and mapping

These files are designed to:
1. Parse unit definitions from the Lua files in the `Cortext Hide` directory
2. Extract resource costs (metal, energy), build times, and unit capabilities
3. Format the data for input into the main optimization program
4. Handle unit renaming and mapping between different naming conventions

## Current Status

**Note**: The data processing pipeline is currently **incomplete**. The system currently uses hardcoded unit data in `limited_buildings_main.py`, but the vision is to have a proper automated data extraction system that:

- Processes the extensive Lua unit definition files in the `Cortext Hide` directory
- Automatically extracts and formats unit costs, build times, and capabilities
- Provides proper preprocessing before feeding data to `limited_buildings_main.py`

## Unit Data Sources

The project includes extensive unit definition files in Lua format located in:
- `Cortext Hide/CorShips/` - Naval units
- `Cortext Hide/CorBots/` - Bot units  
- `Cortext Hide/CorAircraft/` - Aircraft units
- Additional unit categories and definitions

These files contain detailed unit specifications including:
```lua
energycost = 3200,     # Energy cost to build
metalcost = 200,       # Metal cost to build  
buildtime = 5960,      # Time required to build
health = 420,          # Unit hit points
# ... and many other attributes
```

## Installation and Usage

### Prerequisites
- Python 3.7+
- Required packages: `heapq`, `sys`, `os`, `pickle`, `time`, `random`, `json`, `dataclasses`, `collections`, `typing`, `multiprocessing`, `curses`, `copy`

### Running the Program
```bash
python limited_buildings_main.py
```

**Note**: Full installation instructions and proper data pipeline setup will be provided once the data processing components are completed.

## Resource Management

The system tracks three primary resources:
- **Metal (M)**: Primary construction resource
- **Energy (E)**: Power resource for units and production
- **Buildpower**: Construction capacity from builders

Starting conditions:
- Metal: 1000 units
- Energy: 1000 units  
- Base metal income: 0.0/sec
- Base energy income: 30.0/sec
- Commander buildpower: 300

## Technology Tiers

The system recognizes different technology tiers:
- **T1**: Basic units and structures
- **T2**: Advanced units requiring T1 constructors
- **Commander**: Special starting unit capabilities

## Future Development

1. **Complete Data Pipeline**: Finish implementation of the data processing files to automatically extract unit data from Lua files
2. **Enhanced Processing**: Improve data formatting and validation before input to the main program
3. **Dynamic Updates**: Allow for automatic updates when game unit definitions change
4. **Extended Faction Support**: Potentially expand beyond Cortex faction

## Contributing

This project is specifically designed for the Cortex faction in Beyond All Reason. Contributions should maintain compatibility with the existing unit database and optimization algorithms.

Should you have other ideas, such as adding factions, adding more units and buildings, making tech tree robust, and much more. Please submit it so that I can test the program and merge it.

Ultimately I want this program to be a widget, it has a lot more improvements needed and I know most of the code there will be mediocre since I am not a coder. But please let me know if you have suggestions.

## License

See `LICENSE` file for details.
