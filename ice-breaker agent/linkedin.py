import os
import requests
from dotenv import load_dotenv

def scrape_linkedin_profile(profile_url:str, mock: bool=False):
    #proxy curl from http requests
    # 토큰 할당량 => 
    if mock:
        profile_url = "https://gist.githubusercontent.com/emarco177/859ec7d786b45d8e3e3f688c6c9139d8/raw/32f3c85b9513994c572613f2c8b376b633bfc43f/eden-marco-scrapin.json"
        response = requests.get(profile_url, timeout=10)
    else:
        api_endpoint ="https://nubela.co/proxycurl/api/v2/linkedin"
        params = {
            "apikey": os.environ["PROXYCURL_API_KEY"],
            "linkedInUrl": profile_url,
        }
        response = requests.get(
            api_endpoint, 
            params=params,
            timeout=10)
        
    data = response.json()
    data = {
        k: v
        for k, v in data.items()
        if v not in ([], "", "", None) and k not in ["certifications"]
    }
    if data.get("groups"):
        for group_dict in data.get("groups"):
            group_dict.pop("profile_pic_url")
    return data


if __name__ =="__main__":
    print(
        scrape_linkedin_profile(
            profile_url="https://www.linkedin.com/in/eden-marco/"
            )
        )