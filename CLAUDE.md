# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python-based route optimization tool that creates efficient visiting routes for multiple shop addresses. The script reads addresses from Excel files, geocodes them, and calculates the optimal route considering traffic patterns and distance. Uses the nearest neighbor algorithm for route optimization.

## Core Architecture

The codebase is structured as a single-file application (`route_optimizer.py`) with the main `RouteOptimizer` class handling all functionality:

- **Geocoding**: Supports both Google Maps API (primary) and OpenStreetMap Nominatim (fallback)
- **Distance Calculation**: Uses Haversine formula for great-circle distance between coordinates
- **Route Optimization**: Implements nearest neighbor algorithm with traffic-aware time calculations
- **Google Maps Link Generation**: Automatically creates properly formatted Google Maps Directions URLs
- **Caching**: In-memory caches for geocoding results and distance calculations to minimize API calls

## Key Components

### RouteOptimizer Class (`route_optimizer.py:20-307`)

Main class with the following responsibilities:
- **Address Detection** (`extract_addresses:43`): Auto-detects address columns in Excel by searching for keywords like 'adres', 'address', 'lokasyon', 'location'
- **Geocoding** (`geocode_address:78`): Converts addresses to lat/lon coordinates with fallback from Google Maps to Nominatim
- **Distance Matrix** (`get_distance_matrix:113`): Builds n×n distance matrix between all addresses
- **Traffic Modeling** (`get_traffic_factor:162`): Returns traffic multipliers based on time of day:
  - Rush hours (07:00-09:00, 17:00-19:00): 1.5x slower
  - Moderate (10:00-16:00, 20:00-22:00): 1.2x slower
  - Normal: 1.0x
- **Route Optimization** (`optimize_route:179`): Nearest neighbor algorithm starting from specified or first address
- **Google Maps Link** (`generate_google_maps_link:251`): Creates properly formatted Google Maps Directions API v1 URLs with origin, destination, and waypoints (up to 25 intermediate stops). Addresses are URL-encoded to handle special characters and spaces.
- **Excel Output** (`save_route_to_excel:283`): Generates two-sheet Excel with summary (including Google Maps link) and detailed route information

### Algorithm

The route optimization uses a greedy nearest neighbor approach:
1. Start at specified start address (or first address if not specified)
2. Repeatedly visit the nearest unvisited address
3. Return to start address at the end
4. Calculate cumulative times based on current traffic factor

Note: This is not TSP-optimal but provides good results with O(n²) complexity.

## Development Commands

### Installation
```bash
pip install -r requirements.txt
```

### Running the Script

Basic usage (auto-detect address column):
```bash
python route_optimizer.py path/to/file.xlsx
```

With Google Maps API for better geocoding accuracy:
```bash
python route_optimizer.py file.xlsx --api_key YOUR_GOOGLE_API_KEY
```

With specific parameters:
```bash
python route_optimizer.py file.xlsx \
  --address_column "Column Name" \
  --start_address "Starting Address" \
  --output custom_output.xlsx
```

### Command-Line Arguments

- `excel_file` (required): Path to Excel file containing addresses
- `--api_key`: Google Maps API key (optional, falls back to Nominatim)
- `--address_column`: Specific column name containing addresses (optional, auto-detected)
- `--start_address`: Starting point for route (optional, uses first address by default)
- `--output`: Output filename (default: `optimized_route.xlsx`)

## Dependencies

- **pandas**: Excel I/O and data manipulation
- **numpy**: Distance calculations and matrix operations
- **googlemaps**: Google Maps Geocoding API client
- **requests**: HTTP requests for Nominatim geocoding fallback
- **openpyxl**: Excel file writing

## Important Notes

### Geocoding Rate Limits

- **Nominatim (free fallback)**: Rate limited to 1 request/second, less accurate
- **Google Maps API**: Requires API key but provides better accuracy and no strict rate limits for reasonable usage
- Both geocoding methods are cached in-memory during execution

### Multi-language Support

The script is designed to work with Turkish addresses and includes Turkish-specific address detection patterns (`route_optimizer.py:75`): 'cad', 'sok', 'mah', 'apart', 'no:', 'kat', 'istanbul', 'ankara', 'izmir'.

### Excel Input Requirements

Input Excel files should contain a column with full addresses. The script will auto-detect columns named with variations of "address"/"adres" or "location"/"lokasyon". If no such column exists, it attempts to identify address-like content using heuristics.

### Traffic Calculation

Average base speed is set to 40 km/h (`route_optimizer.py:217`), which is then divided by the traffic factor based on current time. Time calculations are estimates only and don't account for actual road conditions.
