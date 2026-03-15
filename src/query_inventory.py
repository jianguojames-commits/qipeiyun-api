import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

def query_parts_inventory(
    csv_path: str, 
    oe_number: Optional[str] = None,
    brand: Optional[str] = None,
    category: Optional[str] = None,
    vehicle_make: Optional[str] = None,
    vehicle_model: Optional[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Query auto parts inventory from the cleaned CSV file.
    
    Args:
        csv_path: Absolute path to the clean_parts.csv file.
        oe_number: Original Equipment number (case-insensitive, exact match).
        brand: Brand name (case-insensitive, partial match).
        category: Category of the part (case-insensitive, partial match).
        vehicle_make: Vehicle manufacturer (case-insensitive, partial match).
        vehicle_model: Vehicle model (case-insensitive, partial match).
        **kwargs: Other fields from the CSV to filter by.
        
    Returns:
        A list of matching part records as dictionaries.
    """
    results = []
    file_path = Path(csv_path)
    
    if not file_path.exists():
        print(f"Error: Inventory file not found at {csv_path}")
        return []

    # Prepare search filters (lowercase for case-insensitive matching)
    filters = {
        'oe_number': oe_number.upper() if oe_number else None,
        'brand': brand.lower() if brand else None,
        'category': category.lower() if category else None,
        'vehicle_make': vehicle_make.lower() if vehicle_make else None,
        'vehicle_model': vehicle_model.lower() if vehicle_model else None,
    }
    # Add extra filters from kwargs
    for k, v in kwargs.items():
        if v is not None:
            filters[k] = str(v).lower()

    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                is_match = True
                
                # Check predefined filters
                for field, search_val in filters.items():
                    if search_val is None:
                        continue
                    
                    actual_val = row.get(field, "").strip()
                    
                    if field == 'oe_number':
                        # OE numbers are usually exact matches after normalization
                        if search_val != actual_val.upper():
                            is_match = False
                            break
                    else:
                        # Other fields use partial matching
                        if search_val not in actual_val.lower():
                            is_match = False
                            break
                
                if is_match:
                    # Parse JSON specs if present
                    if row.get('specs'):
                        try:
                            row['specs'] = json.loads(row['specs'])
                        except json.JSONDecodeError:
                            pass
                    results.append(row)
                    
    except Exception as e:
        print(f"Error reading inventory: {e}")
        return []

    return results

if __name__ == "__main__":
    # Example usage script
    INVENTORY_FILE = "/Users/zhaojianguo/trae_test/data/clean/clean_parts.csv"
    
    print("=== Auto Parts Inventory Query Tool ===\n")
    
    # 1. Query by Brand
    print("Searching for brand 'Bosch'...")
    bosch_parts = query_parts_inventory(INVENTORY_FILE, brand="Bosch")
    print(f"Found {len(bosch_parts)} parts.")
    for p in bosch_parts:
        print(f"- {p['name']} (OE: {p['oe_number']}) - Price: {p['price']} {p['currency']}")
    
    # 2. Query by Category and Vehicle
    print("\nSearching for 'Brake Pad' for 'Toyota'...")
    toyota_brakes = query_parts_inventory(INVENTORY_FILE, category="Brake Pad", vehicle_make="Toyota")
    for p in toyota_brakes:
        print(f"- {p['name']} for {p['vehicle_make']} {p['vehicle_model']} ({p['vehicle_year_start']}-{p['vehicle_year_end'] or '+'})")
    
    # 3. Query by OE Number
    oe_query = "90915YZZE1"
    print(f"\nSearching for OE Number '{oe_query}'...")
    oe_results = query_parts_inventory(INVENTORY_FILE, oe_number=oe_query)
    if oe_results:
        part = oe_results[0]
        print(f"Match Found: {part['brand']} {part['name']} for {part['vehicle_make']} {part['vehicle_model']}")
    else:
        print("No match found for OE number.")
