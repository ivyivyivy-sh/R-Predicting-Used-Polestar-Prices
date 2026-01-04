# -*- coding: utf-8 -*-
"""
Polestar Car Listings Scraper for Blocket.se
Fetches all Polestar listings and saves to CSV with Swedish column names.
"""

import requests
import time
import pandas as pd
from datetime import datetime

# --- Configuration ---
API_URL = "https://www.blocket.se/mobility/search/api/search/SEARCH_ID_CAR_USED"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_all_polestar_listings():
    """
    Fetches ALL Polestar listings from Blocket.se API.
    Returns list of raw listing data.
    """
    all_listings = []
    page = 1
    
    print("--- Starting Polestar Scrape ---")
    
    while True:
        print(f"Fetching page {page}...", end=" ")
        
        # Parameters for Polestar search
        params = {
            'q': 'Polestar',
            'sort': 'published_desc',  # Sort by newest first
            'page': page
        }
        
        try:
            response = requests.get(API_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            ads = data.get('docs', [])
            
            if not ads:
                print("No more ads found.")
                break
            
            print(f"Found {len(ads)} ads.")
            all_listings.extend(ads)
            page += 1
            
            # Be polite to the server
            time.sleep(1.5)
            
        except Exception as e:
            print(f"\n❌ Error fetching page {page}: {e}")
            break
    
    print(f"\nTotal Polestar listings fetched: {len(all_listings)}")
    return all_listings

def process_polestar_listings(listings):
    """
    Converts raw API data into a Pandas DataFrame with Swedish column names.
    """
    processed_data = []
    
    for ad in listings:
        # Extract fields with Swedish column names matching your requirements
        item = {
            'Försäljningspris': ad.get('price', {}).get('amount') if ad.get('price') else None,
            'Säljare': ad.get('dealer_segment'),
            'Bränsle': ad.get('fuel'),
            'Växellåda': ad.get('transmission'),
            'Miltal': ad.get('mileage'),
            'Modellår': ad.get('year'),
            'Biltyp': ad.get('vehicle_type'),
            'Drivning': ad.get('drivetrain'),  # Note: Might need additional processing
            'Hästkrafter': ad.get('power'),  # Note: Might need additional processing
            'Färg': ad.get('color'),
            'Motorstorlek': None,  # Not directly available in API, will be None
            'Datum_i_trafik': datetime.fromtimestamp(ad.get('timestamp') / 1000).strftime('%Y-%m-%d') if ad.get('timestamp') else None,
            'Märke': 'Polestar',
            'Modell': ad.get('model'),
            'ID': ad.get('id'),
            'Rubrik': ad.get('heading'),
            'Plats': ad.get('location'),
            'Räckvidd_WLTP': ad.get('driving_range'),
            'URL': f"https://www.blocket.se/mobility/item/{ad.get('id')}" if ad.get('id') else None,
            'Publiceringsdatum': datetime.fromtimestamp(ad.get('timestamp') / 1000).strftime('%Y-%m-%d %H:%M:%S') if ad.get('timestamp') else None,
            'Modellvariant': ad.get('model_specification'),
            'Beskrivning': ad.get('description')
        }
        processed_data.append(item)
    
    # Create DataFrame with desired column order
    columns_order = [
        'Försäljningspris', 'Säljare', 'Bränsle', 'Växellåda', 'Miltal', 
        'Modellår', 'Biltyp', 'Drivning', 'Hästkrafter', 'Färg', 
        'Motorstorlek', 'Datum_i_trafik', 'Märke', 'Modell'
    ]
    
    df = pd.DataFrame(processed_data)
    
    # Reorder columns and add the rest as additional columns
    main_columns = [col for col in columns_order if col in df.columns]
    additional_columns = [col for col in df.columns if col not in columns_order]
    
    return df[main_columns + additional_columns]

def fetch_additional_details_for_polestar(df):
    """
    OPTIONAL: Fetches additional details that might not be in the main API response.
    This is slower but can get more detailed information.
    """
    print("\n--- Fetching Additional Details (Optional, slower) ---")
    print("This step is optional and can be skipped if not needed.")
    
    proceed = input("Do you want to fetch additional details? (y/n): ").lower()
    
    if proceed != 'y':
        return df
    
    for index, row in df.iterrows():
        ad_id = row['ID']
        
        # Progress indicator
        if (index + 1) % 10 == 0:
            print(f"Processing {index+1}/{len(df)}...")
        
        try:
            # Fetch the ad page HTML for additional details
            url = f"https://www.blocket.se/mobility/item/{ad_id}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            # Parse HTML (simplified - would need BeautifulSoup for full parsing)
            # For now, we'll just note that details are available
            df.at[index, 'Detaljer_Tillgängliga'] = 'Ja'
            
        except:
            df.at[index, 'Detaljer_Tillgängliga'] = 'Nej'
        
        # Be very polite - longer delay for page visits
        time.sleep(2)
    
    return df

def main():
    """
    Main execution function for scraping Polestar listings.
    """
    print("=" * 60)
    print("POLESTAR LISTINGS SCRAPER FOR BLOCKET.SE")
    print("=" * 60)
    
    # 1. Fetch all Polestar listings
    print("\n[1/3] Fetching listings from Blocket.se API...")
    raw_listings = fetch_all_polestar_listings()
    
    if not raw_listings:
        print("❌ No listings found. Exiting.")
        return
    
    # 2. Process into DataFrame with Swedish column names
    print("\n[2/3] Processing data...")
    df = process_polestar_listings(raw_listings)
    
    # 3. Optional: Fetch additional details
    print("\n[3/3] Data processing complete.")
    
    # Ask about additional details
    fetch_details = input("\nFetch additional details from individual pages? (Slower) (y/n): ").lower()
    if fetch_details == 'y':
        df = fetch_additional_details_for_polestar(df)
    
    # 4. Save to CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"polestar_blocket_listings_{timestamp}.csv"
    
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    
    print("\n" + "=" * 60)
    print("✅ SCRAPING COMPLETE!")
    print(f"📊 Total listings: {len(df)}")
    print(f"💾 Saved to: {csv_filename}")
    print("=" * 60)
    
    # Show summary
    print("\n--- DATA SUMMARY ---")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst few rows:")
    print(df.head())
    
    print(f"\nMissing values per column:")
    for col in df.columns:
        missing = df[col].isna().sum()
        if missing > 0:
            print(f"  {col}: {missing} missing")
    
    return df

# Run the scraper
if __name__ == "__main__":
    df_polestar = main()