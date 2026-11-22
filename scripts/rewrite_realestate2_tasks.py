"""
Rewrite real estate task files based on ground truth from data/gold/by_task/realestate2/.
Generates:
  - data/tasks/realestate_all_tasks_20.jsonl
  - data/tasks/realestate_all_tasks_20.csv
  - data/tasks/realestate_dev_tasks_4.jsonl
  - data/tasks/realestate_test_tasks_16.jsonl
"""
import json, os, csv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(REPO, "data", "tasks")

# ------------------------------------------------------------------
# Ground truth from gold files (count, expected_fields, sample_detail_url)
# ------------------------------------------------------------------
GOLD = {
    "WBV1_REAL_RIGHTMOVE_001_LISTING": {
        "count": 25,
        "fields": ["address", "bathrooms", "bedrooms", "description", "images_urls", "listing_agent", "listing_agent_logo", "listing_agent_phone", "listing_url", "price", "property_type", "published_date"],
        "sample_detail_url": "https://www.rightmove.co.uk/properties/89583912#/?channel=RES_BUY",
    },
    "WBV1_REAL_RIGHTMOVE_002_DETAIL": {
        "count": 1,
        "fields": ["address", "bathrooms", "bedrooms", "description", "furnish_type", "has_parking", "images_urls", "key_features", "listing_agent_location", "listing_agent_logo", "listing_office", "listing_url", "price", "property_type", "published_date", "rating", "review_count", "reviews"],
        "sample_detail_url": "https://www.rightmove.co.uk/properties/146059961",
    },
    "WBV1_REAL_DAFT.IE_001_LISTING": {
        "count": 20,
        "fields": ["address", "bathrooms", "bedrooms", "energy_rating", "floor_area", "images_urls", "listing_agent", "listing_agent_logo", "listing_agent_name", "listing_agent_photo", "listing_url", "price", "property_type"],
        "sample_detail_url": "https://www.daft.ie/for-sale/12-knightsbrook-crescent-trim-co-meath/6595237",
    },
    "WBV1_REAL_DAFT.IE_002_DETAIL": {
        "count": 1,
        "fields": ["address", "bathrooms", "bedrooms", "ber_number", "description", "energy_rating", "estimated_stamp_duty", "floor_area", "key_features", "listing_url", "price_per_m2", "property_type", "published_date", "sale_type", "satellite_view_url", "schools", "street_view_url", "transport"],
        "sample_detail_url": "https://www.daft.ie/for-sale/14-riverwood-place-castleknock-dublin-15/6550113",
    },
    "WBV1_REAL_FINN_EIENDOM_001_LISTING": {
        "count": 51,
        "fields": ["address", "bedrooms", "floor_area", "images_urls", "listing_agent_logo", "listing_office", "listing_title", "listing_url", "monthly_fees", "open_house_schedule", "price", "property_type", "tenure", "total_price"],
        "sample_detail_url": "https://www.finn.no/realestate/homes/ad.html?finnkode=464659921",
    },
    "WBV1_REAL_FINN_EIENDOM_002_DETAIL": {
        "count": 1,
        "fields": ["additional_costs", "address", "bedrooms", "description", "energy_rating", "floor_area", "floor_level", "images_urls", "internal_area", "joint_debt", "joint_wealth", "land_area", "listing_id", "listing_title", "listing_url", "monthly_fees", "price_assessment", "property_type", "published_date", "room_layout", "rooms", "total_price", "year_built"],
        "sample_detail_url": "https://www.finn.no/realestate/homes/ad.html?finnkode=465141868",
    },
    "WBV1_REAL_APARTMENTS_001_LISTING": {
        "count": 24,
        "fields": ["address", "bathrooms", "bathrooms_partial", "bedrooms", "floor_area", "images_urls", "listing_agent", "listing_url", "mls_number", "parking", "price", "property_type"],
        "sample_detail_url": "https://www.coldwellbankerhomes.com/ca/san-francisco/899-40th-ave/pid_71927566/",
    },
    "WBV1_REAL_APARTMENTS_002_DETAIL": {
        "count": 1,
        "fields": ["address", "apn", "appliances", "architectural_style", "assoc_fee_freq", "assoc_name", "association", "association_fee", "basement_desc", "bathroom_features", "bathrooms", "bedroom_1", "bedrooms", "county", "cross_streets", "current_bldg_use", "dining_room", "district", "exterior_features", "fencing_description", "fireplace", "fireplaces", "floor_area", "flooring", "for_sale", "foundation", "full_bathrooms", "garage", "half_bathrooms", "heating_type", "hoa_fee", "hoa_fee_freq", "images_urls", "interior_features", "kitchen", "laundry", "listing_agent", "listing_office", "lot_features", "lot_size_acres", "lot_size_sq_ft", "mls_number", "number_of_fireplaces", "number_of_rooms", "parking", "parking_features", "price", "price_sales_history", "primary_bathroom", "primary_bedroom", "property_type", "property_view", "road_maintenance", "roof", "rooms_areas", "sale_type", "school_district", "schools", "special_conditions", "status", "street_road_desc", "tax_history", "utility_description", "water", "year_built"],
        "sample_detail_url": "https://www.apartments.com/the-landing-san-francisco-ca/q9q57k2/",
    },
    "WBV1_REAL_REDFIN_001_LISTING": {
        "count": 41,
        "fields": ["bathrooms", "bedrooms", "floor_area", "images_urls", "key_features", "listing_agent", "listing_url", "open_house_schedule", "price"],
        "sample_detail_url": "https://www.redfin.com/NY/Bayside/21404-33rd-Ave-11361/home/20835511",
    },
    "WBV1_REAL_REDFIN_002_DETAIL": {
        "count": 1,
        "fields": ["around_this_home", "description", "floor_area", "images_urls", "land_area", "listing_agent", "listing_url", "price", "property_details", "property_type", "public_record", "status", "year_built"],
        "sample_detail_url": "https://www.redfin.com/NY/Bronx/2749-Fish-Ave-10469/home/44736662",
    },
    "WBV1_REAL_MAROC_ANNONCES_001_LISTING": {
        "count": 20,
        "fields": ["address", "images_urls", "listing_title", "listing_url", "price", "property_type", "published_date"],
        "sample_detail_url": "https://www.marocannonces.com/categorie/315/Appartements/annonce/10387457/Vend-joli-appart-Maarif.html",
    },
    "WBV1_REAL_MAROC_ANNONCES_002_DETAIL": {
        "count": 1,
        "fields": ["address", "bathrooms", "description", "floor_area", "images_urls", "listing_agent_name", "listing_agent_phone", "listing_id", "listing_title", "listing_url", "price", "published_date", "rooms"],
        "sample_detail_url": "https://www.marocannonces.com/categorie/315/Appartements/annonce/10387457/Vend-joli-appart-Maarif.html",
    },
    "WBV1_REAL_REALESTATE.CO.NZ_001_LISTING": {
        "count": 14,
        "fields": ["address", "bathrooms", "bedrooms", "floor_area", "images_urls", "listing_agent_logo", "listing_agent_name", "listing_agent_photo", "listing_office", "listing_title", "listing_url", "price", "property_type", "sale_type"],
        "sample_detail_url": "https://www.realestate.co.nz/43058090/residential/sale/9-woodham-place-rototuna-north",
    },
    "WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL": {
        "count": 1,
        "fields": ["address", "bathrooms", "bedrooms", "floor_area", "images_urls", "land_area", "listing_url", "parking", "price"],
        "sample_detail_url": "https://www.realestate.co.nz/property/12b-mary-street-papanui-christchurch-city-canterbury/m1fv7m7sc",
    },
    "WBV1_REAL_ONTHEMARKET_001_LISTING": {
        "count": 30,
        "fields": ["address", "bathrooms", "bedrooms", "images_urls", "key_features", "listing_agent_logo", "listing_agent_phone", "listing_office", "listing_url", "price", "property_type"],
        "sample_detail_url": "https://www.onthemarket.com/details/19328039/",
    },
    "WBV1_REAL_ONTHEMARKET_002_DETAIL": {
        "count": 1,
        "fields": ["about_agent", "address", "area_statistics", "bathrooms", "bedrooms", "council_tax", "energy_rating", "floor_area", "images_urls", "key_features", "listing_agent", "listing_agent_logo", "listing_agent_phone", "listing_agent_website", "listing_title", "listing_url", "mobile_signal", "nearest_stations", "price", "property_information", "property_type"],
        "sample_detail_url": "https://www.onthemarket.com/details/19547756/",
    },
    "WBV1_REAL_CENTURY_21_001_LISTING": {
        "count": 300,
        "fields": ["address", "bathrooms", "bedrooms", "floor_area", "images_urls", "listing_agent", "listing_url", "mls_number", "open_house_schedule", "price", "status"],
        "sample_detail_url": "https://www.century21.com/homes/detail/ca/san-francisco/160-noe-st/lid-P00800000HBefcSWXRC1B0KXXzmuHK6fTxoqoUkF",
    },
    "WBV1_REAL_CENTURY_21_002_DETAIL": {
        "count": 1,
        "fields": ["address", "amenities", "appliances", "bathrooms", "bedrooms", "building_area", "floor_area", "flooring", "foundation_description", "garage", "heating", "images_urls", "kitchen_description", "land_area", "listing_id", "listing_url", "monthly_fees", "parking", "price", "price_per_area", "property_type", "published_date", "roof", "status", "water", "year_built"],
        "sample_detail_url": "https://www.century21.com/homes/detail/ca/foster-city/516-saint-vincent-ln/lid-P00800000HBedlsr85sXbFx0cqjVggkXDKwuEsSx",
    },
    "WBV1_REAL_LEBONCOIN_001_LISTING": {
        "count": 35,
        "fields": ["additional_facilities", "address", "energy_rating", "floor_area", "images_urls", "listing_agent_logo", "listing_office", "listing_url", "price", "price_per_m2", "property_type", "rooms"],
        "sample_detail_url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3051337441",
    },
    "WBV1_REAL_LEBONCOIN_002_DETAIL": {
        "count": 1,
        "fields": ["address", "bathrooms", "bedrooms", "characteristics", "description", "energy_rating", "floor_area", "greenhouse_gas_rating", "heating_mode", "heating_type", "images_urls", "listing_agent", "listing_agent_logo", "listing_title", "monthly_fees", "price", "price_per_m2", "property_type", "rooms"],
        "sample_detail_url": "https://www.leboncoin.fr/ad/ventes_immobilieres/3201084037",
    },
}

# ------------------------------------------------------------------
# Base task definitions
# ------------------------------------------------------------------
BASE_TASKS = [
    {
        "task_id": "WBV1_REAL_RIGHTMOVE_001_LISTING",
        "domain": "Real Estate",
        "website_id": "rightmove",
        "website_name": "Rightmove",
        "start_url": "https://www.rightmove.co.uk",
        "instruction": "Extract property listings from the Rightmove search results page. For each property card, return address, price, property_type, bedrooms, bathrooms if visible, description if visible, published_date if visible, listing_agent info if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_RIGHTMOVE_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "rightmove",
        "website_name": "Rightmove",
        "start_url": "https://www.rightmove.co.uk",
        "instruction": "Open a property page from the Rightmove listing and extract address, price, property_type, bedrooms, bathrooms, key_features, description, furnish_type if visible, has_parking if visible, published_date, images_urls, listing agent details, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_DAFT.IE_001_LISTING",
        "domain": "Real Estate",
        "website_id": "daft.ie",
        "website_name": "Daft.ie",
        "start_url": "https://www.daft.ie",
        "instruction": "Extract property listings from the Daft.ie search results page. For each property card, return address, price, property_type, bedrooms, bathrooms if visible, floor_area if visible, energy_rating if visible, listing_agent info if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_DAFT.IE_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "daft.ie",
        "website_name": "Daft.ie",
        "start_url": "https://www.daft.ie",
        "instruction": "Open a property page from the Daft.ie listing and extract address, price, property_type, bedrooms, bathrooms, floor_area, energy_rating, key_features, description, sale_type, published_date, ber_number if available, estimated_stamp_duty if available, schools, transport, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_FINN_EIENDOM_001_LISTING",
        "domain": "Real Estate",
        "website_id": "finn_eiendom",
        "website_name": "Finn eiendom",
        "start_url": "https://www.finn.no/realestate/homes/search.html",
        "instruction": "Extract property listings from the Finn Eiendom search results page. For each property card, return listing_title, address, price, total_price if visible, property_type, bedrooms if visible, floor_area if visible, monthly_fees if visible, tenure if visible, open_house_schedule if visible, listing_office if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_FINN_EIENDOM_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "finn_eiendom",
        "website_name": "Finn eiendom",
        "start_url": "https://www.finn.no/realestate/homes/search.html",
        "instruction": "Open a property page from the Finn Eiendom listing and extract listing_title, address, price, total_price, joint_debt, joint_wealth, additional_costs if available, property_type, bedrooms, floor_area, internal_area if available, land_area if available, rooms, room_layout if available, floor_level if available, energy_rating if available, monthly_fees, price_assessment if available, description, year_built if available, published_date, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_APARTMENTS_001_LISTING",
        "domain": "Real Estate",
        "website_id": "apartments.com",
        "website_name": "Apartments",
        "start_url": "https://www.apartments.com/san-francisco-ca/",
        "instruction": "Extract property listings from the Apartments.com San Francisco search results page. For each property card, return address, price, property_type, bedrooms, bathrooms if visible, floor_area if visible, parking if visible, listing_agent if visible, mls_number if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_APARTMENTS_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "apartments.com",
        "website_name": "Apartments",
        "start_url": "https://www.apartments.com/the-landing-san-francisco-ca/q9q57k2/",
        "instruction": "Open a property page from the Apartments.com listing and extract all available property details including address, price, property_type, bedrooms, bathrooms, floor_area, lot size, year_built, garage, heating_type, appliances, interior/exterior features, rooms, parking, school_district, schools, listing_agent, listing_office, status, sale_type, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "hard",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_REDFIN_001_LISTING",
        "domain": "Real Estate",
        "website_id": "redfin",
        "website_name": "Redfin",
        "start_url": "https://www.redfin.com/city/30749/CA/San-Francisco",
        "instruction": "Extract property listings from the Redfin San Francisco search results page. For each property card, return price, bedrooms, bathrooms if visible, floor_area if visible, key_features if visible, open_house_schedule if visible, listing_agent if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_REDFIN_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "redfin",
        "website_name": "Redfin",
        "start_url": "https://www.redfin.com/city/30749/CA/San-Francisco",
        "instruction": "Open a property page from the Redfin listing and extract price, property_type, floor_area, land_area if available, year_built if available, status, description, property_details, public_record if available, around_this_home if available, listing_agent, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_MAROC_ANNONCES_001_LISTING",
        "domain": "Real Estate",
        "website_id": "maroc_annonces",
        "website_name": "Maroc annonces",
        "start_url": "https://www.marocannonces.com/maroc/immobilier-casablanca-b309-t556.html",
        "instruction": "Extract property listings from the Maroc Annonces Casablanca real estate search results. For each property card, return listing_title, address, price, property_type, published_date if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_MAROC_ANNONCES_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "maroc_annonces",
        "website_name": "Maroc annonces",
        "start_url": "https://www.marocannonces.com/maroc/immobilier-casablanca-b309-t556.html",
        "instruction": "Open a property page from the Maroc Annonces listing and extract listing_title, address, price, floor_area if available, bathrooms if available, rooms if available, description, published_date, listing_agent_name if available, listing_agent_phone if available, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_REALESTATE.CO.NZ_001_LISTING",
        "domain": "Real Estate",
        "website_id": "realestate.co.nz",
        "website_name": "Realestate.co.nz",
        "start_url": "https://www.realestate.co.nz/residential/sale",
        "instruction": "Extract property listings from the realestate.co.nz residential sale search results. For each property card, return listing_title, address, price, sale_type, property_type, bedrooms if visible, bathrooms if visible, floor_area if visible, listing_agent info if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "realestate.co.nz",
        "website_name": "Realestate.co.nz",
        "start_url": "https://www.realestate.co.nz/residential/sale",
        "instruction": "Open a property page from the realestate.co.nz listing and extract address, price, bedrooms, bathrooms if available, floor_area if available, land_area if available, parking if available, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_ONTHEMARKET_001_LISTING",
        "domain": "Real Estate",
        "website_id": "onthemarket",
        "website_name": "Onthemarket",
        "start_url": "https://www.onthemarket.com/for-sale/property/uk/",
        "instruction": "Extract property listings from the OnTheMarket UK for-sale search results. For each property card, return address, price, property_type, bedrooms, bathrooms if visible, key_features if visible, listing_agent info if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_ONTHEMARKET_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "onthemarket",
        "website_name": "Onthemarket",
        "start_url": "https://www.onthemarket.com/for-sale/property/uk/",
        "instruction": "Open a property page from the OnTheMarket listing and extract listing_title, address, price, property_type, bedrooms, bathrooms, floor_area if available, key_features, energy_rating if available, council_tax if available, nearest_stations if available, mobile_signal if available, area_statistics if available, property_information, listing_agent details, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_CENTURY_21_001_LISTING",
        "domain": "Real Estate",
        "website_id": "century_21",
        "website_name": "Century 21",
        "start_url": "https://www.century21.com/real-estate/san-francisco-ca/LCASANFRANCISCO/",
        "instruction": "Extract property listings from the Century 21 San Francisco search results page. For each property card, return address, price, bedrooms, bathrooms if visible, floor_area if visible, status if visible, open_house_schedule if visible, mls_number if visible, listing_agent if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_CENTURY_21_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "century_21",
        "website_name": "Century 21",
        "start_url": "https://www.century21.com/real-estate/san-francisco-ca/LCASANFRANCISCO/",
        "instruction": "Open a property page from the Century 21 listing and extract address, price, property_type, bedrooms, bathrooms, floor_area, building_area if available, land_area if available, year_built if available, status, published_date if available, garage if available, parking if available, heating if available, water if available, flooring if available, roof if available, appliances if available, amenities if available, kitchen_description if available, foundation_description if available, monthly_fees if available, price_per_area if available, listing_id if available, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_LEBONCOIN_001_LISTING",
        "domain": "Real Estate",
        "website_id": "leboncoin",
        "website_name": "Leboncoin",
        "start_url": "https://www.leboncoin.fr/cl/ventes_immobilieres/cp_ch%C3%A2tillon_92320",
        "instruction": "Extract property listings from the Leboncoin real estate search results. For each property card, return address, price, price_per_m2 if visible, property_type, rooms if visible, floor_area if visible, energy_rating if visible, additional_facilities if visible, listing_office if visible, and listing_url.",
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_REAL_LEBONCOIN_002_DETAIL",
        "domain": "Real Estate",
        "website_id": "leboncoin",
        "website_name": "Leboncoin",
        "start_url": "https://www.leboncoin.fr/cl/ventes_immobilieres/cp_ch%C3%A2tillon_92320",
        "instruction": "Open a property page from the Leboncoin listing and extract listing_title, address, price, price_per_m2 if available, property_type, rooms, bedrooms if available, bathrooms if available, floor_area, energy_rating if available, greenhouse_gas_rating if available, heating_type if available, heating_mode if available, monthly_fees if available, characteristics if available, description, listing_agent info if available, images_urls, and listing_url.",
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
]

# ------------------------------------------------------------------
# Ordered keys for all output files
# ------------------------------------------------------------------
ORDERED_KEYS = [
    "task_id", "domain", "website_id", "website_name", "schema_id",
    "start_url", "sample_detail_url", "instruction",
    "requires_pagination", "requires_detail_page", "max_pages",
    "target_records", "difficulty", "verified_status",
    "verification_basis", "snapshot_required", "expected_fields",
]

def assign_schema(task_id):
    return "real_estate_detail_v1" if "_002_DETAIL" in task_id else "real_estate_listing_v1"

all_tasks = []
for base in BASE_TASKS:
    tid = base["task_id"]
    g = GOLD[tid]
    task = {
        "task_id": tid,
        "domain": base["domain"],
        "website_id": base["website_id"],
        "website_name": base["website_name"],
        "schema_id": assign_schema(tid),
        "start_url": base["start_url"],
        "sample_detail_url": g["sample_detail_url"],
        "instruction": base["instruction"],
        "requires_pagination": base["requires_pagination"],
        "requires_detail_page": base["requires_detail_page"],
        "max_pages": base["max_pages"],
        "target_records": g["count"],
        "difficulty": base["difficulty"],
        "verified_status": base["verified_status"],
        "verification_basis": base["verification_basis"],
        "snapshot_required": base["snapshot_required"],
        "expected_fields": g["fields"],
    }
    all_tasks.append(task)

# Dev split: Rightmove + Daft.ie (first 4)
dev_ids = {
    "WBV1_REAL_RIGHTMOVE_001_LISTING",
    "WBV1_REAL_RIGHTMOVE_002_DETAIL",
    "WBV1_REAL_DAFT.IE_001_LISTING",
    "WBV1_REAL_DAFT.IE_002_DETAIL",
}
dev_tasks = [t for t in all_tasks if t["task_id"] in dev_ids]
test_tasks = [t for t in all_tasks if t["task_id"] not in dev_ids]

def write_jsonl(path, tasks):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

def write_csv(path, tasks):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ORDERED_KEYS)
        writer.writeheader()
        for t in tasks:
            row = dict(t)
            row["expected_fields"] = json.dumps(row["expected_fields"])
            writer.writerow(row)

write_jsonl(os.path.join(TASKS_DIR, "realestate_all_tasks_20.jsonl"), all_tasks)
write_jsonl(os.path.join(TASKS_DIR, "realestate_dev_tasks_4.jsonl"), dev_tasks)
write_jsonl(os.path.join(TASKS_DIR, "realestate_test_tasks_16.jsonl"), test_tasks)
write_csv(os.path.join(TASKS_DIR, "realestate_all_tasks_20.csv"), all_tasks)

print(f"Written {len(all_tasks)} tasks to realestate_all_tasks_20.*")
print(f"Written {len(dev_tasks)} tasks to realestate_dev_tasks_4.jsonl")
print(f"Written {len(test_tasks)} tasks to realestate_test_tasks_16.jsonl")

# Verify
for t in all_tasks:
    tid = t["task_id"]
    assert t["schema_id"] == assign_schema(tid), f"{tid}: schema mismatch"
    assert t["target_records"] == GOLD[tid]["count"], f"{tid}: count mismatch"
    assert t["expected_fields"] == GOLD[tid]["fields"], f"{tid}: fields mismatch"
print("All sanity checks passed.")
