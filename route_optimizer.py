#!/usr/bin/env python3
"""
Optimized Route Planner for Shop Visits
This script reads shop addresses from an Excel file and creates an optimized route
considering traffic conditions, distance, and time efficiency.
"""

import pandas as pd
import numpy as np
import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import googlemaps
from itertools import permutations
import argparse
import sys

class RouteOptimizer:
    def __init__(self, api_key: str = None):
        """
        Initialize the route optimizer with Google Maps API key
        """
        self.api_key = api_key
        self.gmaps = googlemaps.Client(key=api_key) if api_key else None
        self.geocoding_cache = {}
        self.distance_cache = {}

    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """
        Read Excel file and return DataFrame with addresses
        """
        try:
            df = pd.read_excel(file_path)
            print(f"Excel file loaded successfully. Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            return df
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return None

    def extract_addresses(self, df: pd.DataFrame, address_column: str = None) -> List[str]:
        """
        Extract addresses from DataFrame
        """
        if address_column is None:
            # Try to find address column automatically
            address_columns = [col for col in df.columns if any(
                keyword in col.lower() for keyword in ['adres', 'address', 'lokasyon', 'location']
            )]
            if address_columns:
                address_column = address_columns[0]
            else:
                # Use the first column that looks like it contains addresses
                for col in df.columns:
                    if df[col].dtype == 'object':
                        sample_values = df[col].dropna().head(5).astype(str)
                        if any(self._is_address(val) for val in sample_values):
                            address_column = col
                            break

        if address_column:
            addresses = df[address_column].dropna().astype(str).tolist()
            print(f"Found {len(addresses)} addresses in column '{address_column}'")
            return addresses
        else:
            print("No address column found. Please specify the column name.")
            return []

    def _is_address(self, text: str) -> bool:
        """
        Simple heuristic to check if text looks like an address
        """
        indicators = ['cad', 'sok', 'mah', 'apart', 'no:', 'kat', 'istanbul', 'ankara', 'izmir']
        return any(indicator in text.lower() for indicator in indicators)

    def geocode_address(self, address: str) -> Tuple[float, float]:
        """
        Convert address to coordinates using geocoding
        """
        if address in self.geocoding_cache:
            return self.geocoding_cache[address]

        if not self.gmaps:
            # Fallback: Use Nominatim (OpenStreetMap)
            try:
                url = f"https://nominatim.openstreetmap.org/search?format=json&q={requests.utils.quote(address)}"
                response = requests.get(url, headers={'User-Agent': 'RouteOptimizer/1.0'})
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        coords = (float(data[0]['lat']), float(data[0]['lon']))
                        self.geocoding_cache[address] = coords
                        return coords
            except Exception as e:
                print(f"Geocoding error for {address}: {e}")
                return None, None

        # Use Google Maps Geocoding API
        try:
            result = self.gmaps.geocode(address)
            if result:
                location = result[0]['geometry']['location']
                coords = (location['lat'], location['lng'])
                self.geocoding_cache[address] = coords
                return coords
        except Exception as e:
            print(f"Google geocoding error for {address}: {e}")

        return None, None

    def get_distance_matrix(self, addresses: List[str]) -> np.ndarray:
        """
        Get distance matrix between all addresses
        """
        n = len(addresses)
        distance_matrix = np.zeros((n, n))

        # Get coordinates for all addresses
        coords = []
        for addr in addresses:
            lat, lon = self.geocode_address(addr)
            coords.append((lat, lon))

        # Calculate distances
        for i in range(n):
            for j in range(n):
                if i != j:
                    cache_key = f"{i}_{j}"
                    if cache_key in self.distance_cache:
                        distance_matrix[i][j] = self.distance_cache[cache_key]
                    else:
                        dist = self._calculate_distance(coords[i], coords[j])
                        distance_matrix[i][j] = dist
                        self.distance_cache[cache_key] = dist

        return distance_matrix

    def _calculate_distance(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate distance between two coordinates using Haversine formula
        """
        if coord1 == (None, None) or coord2 == (None, None):
            return float('inf')

        lat1, lon1 = coord1
        lat2, lon2 = coord2

        R = 6371  # Earth's radius in kilometers

        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)

        a = np.sin(delta_lat/2)**2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))

        return R * c

    def get_traffic_factor(self, current_time: datetime = None) -> float:
        """
        Get traffic factor based on time of day
        """
        if current_time is None:
            current_time = datetime.now()

        hour = current_time.hour

        # Rush hours in Turkish cities
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            return 1.5  # 50% slower during rush hours
        elif (10 <= hour <= 16) or (20 <= hour <= 22):
            return 1.2  # 20% slower during moderate traffic
        else:
            return 1.0  # Normal speed

    def optimize_route(self, addresses: List[str], start_address: str = None) -> Dict:
        """
        Optimize route using nearest neighbor algorithm
        """
        if not addresses:
            return {"error": "No addresses provided"}

        # Get distance matrix
        distance_matrix = self.get_distance_matrix(addresses)

        # If no start address specified, use the first address
        if start_address is None:
            start_address = addresses[0]

        start_idx = addresses.index(start_address)

        # Nearest Neighbor algorithm
        unvisited = set(range(len(addresses)))
        current = start_idx
        route = [current]
        total_distance = 0
        unvisited.remove(current)

        current_time = datetime.now()
        traffic_factor = self.get_traffic_factor(current_time)

        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            total_distance += distance_matrix[current][nearest]
            unvisited.remove(nearest)
            current = nearest

        # Add return to start
        total_distance += distance_matrix[current][start_idx]
        route.append(start_idx)

        # Calculate time estimates
        avg_speed_km_h = 40 / traffic_factor  # Average speed considering traffic
        total_time_hours = total_distance / avg_speed_km_h

        # Create route details
        route_details = []
        for i, idx in enumerate(route[:-1]):  # Exclude the final return to start
            next_idx = route[i + 1]
            distance = distance_matrix[idx][next_idx]
            time_hours = distance / avg_speed_km_h

            route_details.append({
                "stop": i + 1,
                "address": addresses[idx],
                "next_address": addresses[next_idx],
                "distance_km": round(distance, 2),
                "estimated_time_minutes": round(time_hours * 60, 1),
                "arrival_time": (current_time + timedelta(hours=sum(r["estimated_time_minutes"] / 60 for r in route_details))).strftime("%H:%M")
            })

        return {
            "total_distance_km": round(total_distance, 2),
            "total_time_minutes": round(total_time_hours * 60, 1),
            "traffic_factor": traffic_factor,
            "route": route_details,
            "optimized_order": [addresses[i] for i in route[:-1]]
        }

    def save_route_to_excel(self, route_data: Dict, output_file: str):
        """
        Save optimized route to Excel file
        """
        df = pd.DataFrame(route_data["route"])

        # Add summary information
        summary = pd.DataFrame([{
            "Total Distance (km)": route_data["total_distance_km"],
            "Total Time (minutes)": route_data["total_time_minutes"],
            "Traffic Factor": route_data["traffic_factor"],
            "Optimization Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        with pd.ExcelWriter(output_file) as writer:
            summary.to_excel(writer, sheet_name='Summary', index=False)
            df.to_excel(writer, sheet_name='Optimized Route', index=False)

        print(f"Optimized route saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Optimize route for shop visits')
    parser.add_argument('excel_file', help='Path to Excel file containing shop addresses')
    parser.add_argument('--api_key', help='Google Maps API key (optional)')
    parser.add_argument('--address_column', help='Name of column containing addresses')
    parser.add_argument('--start_address', help='Starting address (optional)')
    parser.add_argument('--output', default='optimized_route.xlsx', help='Output Excel file name')

    args = parser.parse_args()

    # Initialize optimizer
    optimizer = RouteOptimizer(api_key=args.api_key)

    # Read Excel file
    df = optimizer.read_excel_file(args.excel_file)
    if df is None:
        sys.exit(1)

    # Extract addresses
    addresses = optimizer.extract_addresses(df, args.address_column)
    if not addresses:
        sys.exit(1)

    # Optimize route
    print("Optimizing route...")
    route_data = optimizer.optimize_route(addresses, args.start_address)

    if "error" in route_data:
        print(f"Error: {route_data['error']}")
        sys.exit(1)

    # Display results
    print("\n" + "="*60)
    print("OPTIMIZED ROUTE RESULTS")
    print("="*60)
    print(f"Total Distance: {route_data['total_distance_km']} km")
    print(f"Total Time: {route_data['total_time_minutes']} minutes")
    print(f"Traffic Factor: {route_data['traffic_factor']}")
    print("\nOptimized Route:")
    print("-"*40)

    for stop in route_data["route"]:
        print(f"{stop['stop']}. {stop['address']}")
        print(f"   → Next: {stop['distance_km']} km, {stop['estimated_time_minutes']} min")
        print(f"   Arrival: {stop['arrival_time']}")
        print()

    # Save to Excel
    optimizer.save_route_to_excel(route_data, args.output)

    print("="*60)
    print("Route optimization complete!")
    print("="*60)

if __name__ == "__main__":
    main()