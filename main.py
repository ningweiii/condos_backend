from datetime import datetime, timedelta
import json
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
log = logging.getLogger(__name__)

BASE_URL = "https://api.condos.ca/v1/listings"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
}
query = {"neighbourhood_name": "South Surrey", "status": "Active"}

filename = "listings_south_surrey_active_sale.json"
filters = {
    "neighbourhood_name": "South Surrey",
    "home_type": "Townhouse",
    "status": "Active",
    "bedrooms": "3",
    "bathrooms": "3",
    "building_age": "10",
    "parking_spots": "1",
    "offer": "Sale",
    "days_on_market": "10",
}
# CRITERIA = {
#     "asking_price": 859800,
#     "bathrooms": 3,
#     "bedrooms": 1,
#     "building_age": "3",
#     "entry_date": "2022-01-31",
#     "has_balcony": 0,
#     "has_locker": 0,
#     "home_type": "Townhouse",
#     "maintenance_fee": "243.00",
#     "mls_number": "R2647899",
#     "neighbourhood_name": "South Surrey",
#     "offer": "Sale", // Rent
#     "outdoor_space": "Rooftop Deck",
#     "parking_spots": 4,
#     "parking_type": "Owned",
#     "photo_base_url": "https://shared-s3.property.ca/public/images/listings/optimized/r2647899/mls/",
#     # https://shared-s3.property.ca/public/images/listings/optimized/r2647899/mls/r2647899_2.jpg?v=3
#     "photo_count": 25,
#     "photo_version": 3,
#     "property_type": "Condo Townhouse",
#     "rooms": '[{"id": 3770516, "type": "Living Room", "unit": "Feet", "level": null, "order": 1, "width": "13.00", "length": "11.33", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770517, "type": "Dining Room", "unit": "Feet", "level": null, "order": 2, "width": "11.58", "length": "9.75", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770518, "type": "Kitchen", "unit": "Feet", "level": null, "order": 3, "width": "8.58", "length": "12.17", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770519, "type": "Den", "unit": "Feet", "level": null, "order": 4, "width": "7.00", "length": "7.58", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770520, "type": "Master Bedroom", "unit": "Feet", "level": null, "order": 5, "width": "11.00", "length": "14.00", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770521, "type": "Bedroom", "unit": "Feet", "level": null, "order": 6, "width": "11.17", "length": "9.17", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}, {"id": 3770522, "type": "Foyer", "unit": "Feet", "level": null, "order": 7, "width": "5.00", "length": "7.00", "listing_id": 714170, "description_1": null, "description_2": null, "description_3": null}]',
#     "sqft": 1253,
#     "status": "Active",
#     "street_id": 76764,
#     "street_name": "19 Avenue",
#     "tax": 2627.13,
#     "tax_year": 2021,
#     "title": "74 - 16433 19TH AVENUE",
#     "title_to_land": "Freehold Strata",
#     "unit_name": "74",
#     "url": "surrey/berkeley-village-16400-20-ave-16433-19-ave/unit-74-R2647899",
#     "mode": "Sold" / Active
# }

# https://api.condos.ca/v1/listings?mode=Sold&neighbourhood_name=West%20End&home_type=Condo
def save_listings(
    neighbourhood_name: str = "South Surrey",
    mode: str = "Active",
    offer: str = "Sale",
) -> None:
    """
    Save all listings into json file based on neighbourhood_name (e.g south surrey, richmond)
    and mode (active or sold
    )"""
    try:
        # https://jonathansoma.com/lede/foundations-2018/classes/apis/multiple-pages-of-data-from-apis/
        results = []
        query = {
            "neighbourhood_name": neighbourhood_name,
            "mode": mode,
        }
        response = requests.get(BASE_URL, headers=headers, params=query)
        data = response.json()
        results += data["data"]
        while data["next_page_url"] is not None:
            log.debug("next page found, downloading", data["next_page_url"])
            response = requests.get(
                data["next_page_url"], headers=headers, params=query
            )
            data = response.json()
            results += data["data"]

        log.debug("We have", len(results), "total results")
        parsed_neighbourhood_name = "_".join(neighbourhood_name.lower().split())
        filename = (
            "listings_"
            + parsed_neighbourhood_name
            + "_"
            + mode
            + "_"
            + offer
            + ".json"
        ).lower()
        with open(filename, "w") as outfile:
            json.dump(results, outfile, indent=4)

        log.debug("Sync done!")
    except requests.exceptions.HTTPError as errh:
        log.debug(errh)
    except requests.exceptions.ConnectionError as errc:
        log.debug(errc)
    except requests.exceptions.Timeout as errt:
        log.debug(errt)
    except requests.exceptions.RequestException as err:
        log.debug(err)


def query_listings(filters: dict, data: dict) -> list:
    """
    Parse data getting from frontend into query dict format
    Query from json file based on criteria
    Return json
    """
    result = []
    for d in data:
        log.debug(d)
        add = True
        for filterkey, filtervalue in filters.items():
            if filterkey == "bedrooms":
                print("bedrooms")
                print(filterkey, filtervalue)
                print(d.get("bedrooms"))
                print("------------------")
                if int(filtervalue) > int(d.get("bedrooms", "0")):
                    add = False
                    break
            elif filterkey == "bathrooms":
                print("bathrooms")
                print(filterkey, filtervalue)
                print(d.get("bathrooms"))
                print("------------------")
                if int(filtervalue) > int(d.get("bathrooms", "0")):
                    add = False
                    break
            elif filterkey == "parking_spots":
                print("parking_spots")
                print(filterkey, filtervalue)
                print(d.get("parking_spots"))
                print("------------------")
                print(d.get("parking_spots"))
                if int(filtervalue) > int(d.get("parking_spots") or 0):
                    add = False
                    break
            elif filterkey == "building_age":
                print("building_age")
                print(filterkey, filtervalue)
                print(d.get("building_age"))
                print("------------------")
                if int(filtervalue) < int(d.get("building_age", "99999")):
                    print("bigger")
                    add = False
                    break
            elif filterkey == "days_on_market":
                print("days_on_market")
                print(filterkey, filtervalue)
                print(d.get("days_on_market"))
                print("------------------")
                # filtervalue days_on_market, if the date on the market in earlier than the earlest_entry_date
                # opt out from the list
                earliest_entry_date = datetime.now() - timedelta(days=int(filtervalue))
                if datetime.fromisoformat(d.get("entry_date")) < earliest_entry_date:
                    add = False
                    break
            elif d.get(filterkey) and filtervalue != d.get(filterkey):
                add = False
                break
        if add:
            print("&&&&&&&&")
            print("ADDED")
            result.append(d)

    return result


@app.get("/listings")
def read_listings():
    f = open(filename)
    print("done")
    all_data = json.load(f)
    f.close()
    filtered_data = query_listings(filters=filters, data=all_data)
    return filtered_data


# save_listings(neighbourhood_name="West End",mode="Sold")
# save_listings()


# f = open("listings_test.json")
# f = open(filename)
# data = json.load(f)
# f.close()
# logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
# print(query_listings(filters=filters, data=data))
