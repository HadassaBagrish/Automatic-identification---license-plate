import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import cv2
import urllib3
from urllib.parse import urlencode
from sklearn.cluster import KMeans  # Import KMeans from scikit-learn
import numpy as np
import webcolors


def closest_color(rgb_color):
    css3_hex_to_names = {webcolors.hex_to_rgb(hex_code): name for name, hex_code in webcolors.CSS3_NAMES_TO_HEX.items()}
    min_dist = float('inf')
    closest_name = None
    for color, name in css3_hex_to_names.items():
        dist = np.linalg.norm(np.array(color) - np.array(rgb_color))
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name


def get_dominant_color(image, k=4):
    # Reshape the image to have two dimensions
    image_flat = image.reshape((-1, 3))

    # Apply KMeans clustering
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(image_flat)

    # Get the dominant colors
    dominant_colors = kmeans.cluster_centers_

    # Convert dominant color to integer
    dominant_colors = dominant_colors.astype(int)
    return dominant_colors[0]  # Return the most dominant color

    # return dominant_colors


async def validation(results):
    results = pd.read_csv('./validation_data1.csv')
    for i in range(len(results)):
        result = results['license_number'][i]
        if result:
            # result = result.split('\n')
            print("Extracted text:")
            print(result)
            # Base URL of the API endpoint
            base_url = 'https://data.gov.il/api/3/action/datastore_search'
            # Resource ID for the specific dataset
            resource_id = '053cea08-09bc-40ec-8f7a-156f0677aff3'
            mispar_rechev = str(result)

            # Create a dictionary of query parameters
            query_params = {
                'resource_id': resource_id,
                'q': mispar_rechev  # Example query parameter
            }

            # Encode the query parameters and construct the full URL
            full_url = f"{base_url}?{urlencode(query_params)}"

            # Create a PoolManager instance
            http = urllib3.PoolManager()

            # Make a request using the PoolManager
            response = http.request('GET', full_url)
            # Read and decode the response data
            response_data = response.data.decode('utf-8')

            # Find the position of the word "fields"
            end = response_data.find('fields')
            start = response_data.find('"records"')

            # Extract the substring from the start to the position of "fields"
            if end != -1 and start != -1:
                filtered_data = response_data[start:end]
            else:
                filtered_data = response_data

            # Print the filtered data
            print(filtered_data)
            color_start = filtered_data.find('"tzeva_rechev":') + len('"tzeva_rechev":')
            color_end = filtered_data.find(',', color_start)
            nameColorCar = filtered_data[color_start:color_end].strip().strip('"')
            print("Extracted car color from API:", nameColorCar)

            # Load the video
            video_path = 'good1.mp4'
            cap = cv2.VideoCapture(video_path)
            frame_number = int(results['frame_nmr'][i])
            car_bbox = results['car_bbox'][i]  # Assuming it's in a form like '[x, y, w, h]'

            # Set the video to the specific frame number
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()

            if not ret:
                print(f"Failed to extract frame {frame_number} from the video.")
                continue

            # Extract the car's bounding box from the frame
            car_bbox = car_bbox.split()
            car_bbox = [float(item) for item in car_bbox]
            x, y, w, h = car_bbox
            car_image = frame[int(y):int(y + h), int(x):int(x + w)]
            print("Shape of car_image:", car_image.shape)

            # Get the dominant color of the car image
            dominant_color = get_dominant_color(car_image)

            # Convert the dominant color to a more readable format (e.g., closest color name)
            # This is a simplistic approach; for better results, consider using a color library or more advanced method
            def convert_rgb_to_name(rgb_color):
                color_names = {
                    (255, 0, 0): 'אדום',
                    (0, 255, 0): 'ירוק',
                    (0, 0, 255): 'כחול',
                    (255, 255, 0): 'צהוב',
                    (0, 255, 255): 'טורקיז',
                    (255, 0, 255): 'magenta',
                    (0, 0, 0): 'שחור',
                    (255, 255, 255): 'לבן',
                    (128, 128, 128): 'אפור',
                    (0, 0, 205): 'כחול מטל',  # Medium Blue
                    (0, 0, 0): 'שחור',  # Black
                    (192, 192, 192): 'כסף',  # Silver
                    (245, 245, 220): 'בז',  # Beige
                    (173, 216, 230): 'תכלת מטאלי',  # Light Blue
                    (255, 255, 240): 'שנהב לבן',  # Ivory White
                    (192, 192, 192): 'כסף מטלי',  # Metallic Silver
                    (169, 169, 169): 'אפור כהה',  # Dark Gray
                    (96, 123, 139): 'אפור כחול מטלי',  # Blue Gray Metallic
                    (173, 216, 230): 'כחול בהיר',  # Light Blue
                    (0, 128, 0): 'ירוק',  # Green
                    (128, 128, 128): 'אפור',  # Gray
                    (0, 0, 139): 'כחול כהה',  # Dark Blue
                    (0, 0, 255): 'כחול',  # Blue
                    (105, 105, 105): 'כסוף כהה מטלי',  # Dark Metallic Silver
                    (128, 0, 0): 'בורדו מטל',  # Maroon
                    (70, 130, 180): 'אפור פלדה',  # Steel Gray
                    (169, 169, 169): 'אפור מטל',  # Metallic Gray
                    (25, 25, 25): 'שחור מטלי',  # Metallic Black
                    (255, 215, 0): 'זהב'  # Gold
                }

                # Find the closest color name
                min_dist = float('inf')
                closest_color = None
                for color, name in color_names.items():
                    dist = np.linalg.norm(np.array(color) - rgb_color)
                    if dist < min_dist:
                        min_dist = dist
                        closest_color = name
                return closest_color

            car_color_name = convert_rgb_to_name(dominant_color)
            print("Detected car color:", car_color_name)

            # Compare the detected color with the API color
            if car_color_name.lower() == nameColorCar.lower():
                print(f"Color match for license number {result}: {car_color_name}")
            else:
                print(
                    f"Color mismatch for license number {result}: API color - {nameColorCar}, Detected color - {car_color_name}")

            # Release the video capture object
            cap.release()
        else:
            print("Failed to extract text from the image.")





        # result=2760345
#
#
#         # Set the URL of the website's search page
#         url = "https://www.check-car.co.il/israeli-vin-check/"
#         # Define the payload for the search
#
#         # Set up the ChromeDriver
#         driver = webdriver.Chrome()
#
#         # Make the HTTP request
#         driver.get(url)
#         search_box = driver.find_element("name", "car")
#         search_box.send_keys(str(result))
#         search_box.send_keys(Keys.RETURN)
#
#         # Wait for the page to load (you might need to adjust the time depending on the website)
#         driver.implicitly_wait(10)
#
#         # Get the HTML content after the dynamic content has loaded
#         html_content = driver.page_source
#
#         # Parse the HTML content
#         soup = BeautifulSoup(html_content, 'html.parser')
#         import time
#
#         time.sleep(10)
#
#         # Extract information from the website
#         # Your scraping logic here
#
#         # For example, printing the text of all paragraphs
#         paragraphs = soup.find_all('div', class_='table_col type-string')
#         for paragraph in paragraphs:
#             print(paragraph.text)
#
#         # Close the browser
#         driver.quit()
#     else:
#         print("Failed to extract text from the image.")


