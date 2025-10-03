# Route Optimizer for Shop Visits

A Python script that optimizes routes for visiting multiple shops/addresses, considering traffic conditions, distance, and time efficiency.

## Features

- **Automatic Address Detection**: Automatically finds address columns in Excel files
- **Traffic Optimization**: Considers traffic density based on time of day
- **Time Calculation**: Estimates arrival times for each stop
- **Google Maps Integration**: Optional API support for more accurate location data
- **Excel Output**: Saves optimization results to Excel files
- **Multi-language Support**: Works with Turkish addresses and location names

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd route-optimizer
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python route_optimizer.py path/to/your/excel/file.xlsx
```

### Advanced Usage
```bash
# With Google Maps API for better accuracy
python route_optimizer.py file.xlsx --api_key YOUR_API_KEY

# With specific starting address
python route_optimizer.py file.xlsx --start_address "Your Starting Address"

# With specific address column
python route_optimizer.py file.xlsx --address_column "Address Column Name"

# Custom output file
python route_optimizer.py file.xlsx --output custom_output.xlsx
```

### Command Line Options

| Option | Description | Required |
|--------|-------------|----------|
| `excel_file` | Path to Excel file containing addresses | Yes |
| `--api_key` | Google Maps API key (optional) | No |
| `--address_column` | Name of column containing addresses | No |
| `--start_address` | Starting address for route | No |
| `--output` | Output Excel file name (default: optimized_route.xlsx) | No |

## Traffic Factors

The script considers different traffic conditions throughout the day:

- **07:00-09:00 & 17:00-19:00**: Rush hour (50% slower)
- **10:00-16:00 & 20:00-22:00**: Moderate traffic (20% slower)
- **Other times**: Normal traffic conditions

## Output

The script generates:
1. **Console Output**: Route summary with total distance, time, and optimized order
2. **Excel File**: Two sheets - Summary and detailed route information

### Excel Output Structure

**Summary Sheet:**
- Total distance in kilometers
- Total time in minutes
- Traffic factor used
- Optimization timestamp

**Optimized Route Sheet:**
- Stop number
- Address
- Next address
- Distance between stops
- Estimated travel time
- Arrival time

## Excel File Requirements

Your Excel file should contain addresses in a column. The script automatically detects columns with names containing:
- `adres`
- `address`
- `lokasyon`
- `location`

If no such column is found, it will search for text that looks like addresses.

## Google Maps API (Optional)

For more accurate geocoding and routing, you can use Google Maps API:

1. Get an API key from [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the following APIs:
   - Geocoding API
   - Maps JavaScript API
   - Directions API (optional)
3. Use the `--api_key` parameter when running the script

Without API key, the script uses OpenStreetMap Nominatim service (free but rate-limited).

## Examples

### Turkish Addresses Example
```bash
python route_optimizer.py shops.xlsx --address_column "Dükkan Adresleri"
```

### English Addresses Example
```bash
python route_optimizer.py stores.xlsx --api_key "YOUR_API_KEY"
```

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please create an issue in the repository.