from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re, os, time
import pandas as pd

# Set Chrome options



data =[]
def scrap(count):
    page = 1
    while page <= count:
        try:
            options = Options()
            options.add_argument("--disable-gpu")
            driver = webdriver.Chrome(options=options)
            driver.get(f"https://www.propertyfinder.ae/en/rent/properties-for-rent.html?page={page}")
            wait = WebDriverWait(driver, 10)
            elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "property-card-module_property-card__wrapper__ZZTal")))  # Replace "property-card" with your class name
            all_outer_html = ""
            for element in elements:
                outer_html = element.get_attribute("outerHTML")
                all_outer_html += outer_html + "\n\n"  # Add line breaks for better readability
            with open("elements_by_class.html", "w", encoding="utf-8") as file:
                file.write(all_outer_html)
            print("HTML content saved as 'elements_by_class.html'.")
            time.sleep(5)
            driver.close()
           
            with open("elements_by_class.html", "r", encoding="utf-8") as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, "html.parser")
            elements = soup.find_all(class_="property-card-module_property-card__wrapper__ZZTal")  # Replace with the correct class name
            for index, element in enumerate(elements, start=1):
                links = element.find("a",class_="property-card-module_property-card__link__L6AKb")
                href = links.get("href")
                status_button = element.find("button",class_="tag-module_tag__jFU3w")
                span_tag = status_button.find("span")
                status = span_tag.text
                type = element.find("p",class_="styles-module_content__property-type__QuVl4").text.strip()
                price = element.find("p",class_="styles-module_content__price__SgQ5p").text
                try:
                    price = " ".join(price.split())
                    price_list = price.split(" ")
                    rent_amt = price_list[0]
                    currency = price_list[1]
                    currency = currency.split("/")
                    currency_name = currency[0]
                    timespan = currency[1]
                except Exception as e:
                    print("An error occurred:", e)
                location = element.find("p",class_="styles-module_content__location__bNgNM").text.split(",")
                try:
                    clean_location = [re.sub(r'\s+', ' ', item).strip() for item in location]
                    last_two = clean_location[-2:]
                    neighborhood = last_two[0]
                    city = last_two[1]
                except Exception as e:
                    print("An error occurred:", e)
                div = soup.find("div", class_="styles-module_content__details__5sHyT")   
                p_tags = div.find_all("p", class_="styles-module_content__details-item__mlu9B")  
                if len(p_tags) >= 3:
            # Extract the content from the first 3 <p> tags
                    bedroom = p_tags[0].text.strip()  # First <p> tag
                    bathroom = p_tags[1].text.strip()
                    space = p_tags[2].text.strip()
                data.append((index, href, status, type,bedroom, bathroom, space, rent_amt, currency_name, timespan, neighborhood, city))
            
            os.remove("elements_by_class.html")
            print("File removed")
            page += 1
                
        except Exception as e:
            print("An error occurred:", e)




if __name__ == "__main__":
    scrap(2)
    colmuns = ["Id", "Link", "Status", "Type", "Bedroom", "Bathroom", "Space", "Rent Amount", "Currency", "Timespan", "Neighborhood", "City"]
    df = pd.DataFrame(data, columns=colmuns)
    print(df)
    df.to_csv("property_data.csv", index=False)
    print("closed")