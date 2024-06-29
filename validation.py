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
from datetime import datetime  # Importing datetime class directly


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


def convert_rgb_to_name(rgb_color):
    requested_color = rgb_color
    min_colors = {}
    for name, hex_value in webcolors.css3_names_to_hex.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(hex_value)
        rd = (r_c - requested_color[0]) ** 2
        gd = (g_c - requested_color[1]) ** 2
        bd = (b_c - requested_color[2]) ** 2
        min_colors[(rd + gd + bd)] = name
    print(min_colors[min(min_colors.keys())])



    r, g, b = rgb_color
    if 200 <= b <= 255 and 0 <= g <= 50 and 0 <= r <= 50:
        return 'אדום'
    # elif 0 <= r <= 50 and 200 <= g <= 255 and 0 <= b <= 50:
    #     return 'ירוק'
    elif 0 <= b <= 50 and 30 <= g <= 70 and 30 <= r <= 70:
        return 'כחול'
    # elif 200 <= r <= 255 and 200 <= g <= 255 and 0 <= b <= 50:
    #     return 'צהוב'
    # elif 0 <= r <= 50 and 200 <= g <= 255 and 200 <= b <= 255:
    #     return 'טורקיז'
    # elif 200 <= r <= 255 and 0 <= g <= 50 and 200 <= b <= 255:
    #     return 'מגנטה'
    elif 90 <= b <= 120 and 80 <= g <= 120 and 70 <= r <= 110:
        return 'שחור'
    # elif 200 <= r <= 255 and 200 <= g <= 255 and 200 <= b <= 255:
    #     return 'לבן'
    # elif 100 <= r <= 150 and 100 <= g <= 150 and 100 <= b <= 150:
    #     return 'אפור'
    # elif 0 <= r <= 100 and 0 <= g <= 100 and 150 <= b <= 205:
    #     return 'כחול מטל'
    # elif 180 <= r <= 200 and 180 <= g <= 200 and 180 <= b <= 200:
    #     return 'כסף'
    elif 180 <= b <= 255 and 180 <= g <= 220 and 140 <= r <= 200:
        return 'בז מטאלי'
    # elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
    #     return 'תכלת מטאלי'
    elif 50 <= b <= 100 and 50 <= g <= 90 and 50 <= r <= 100:
        return 'שנהב לבן'
    elif 69 <= b <= 100 and 60 <= g <= 100 and 60 <= r <= 100:
        return 'כסף'
    # elif 150 <= r <= 180 and 150 <= g <= 180 and 150 <= b <= 180:
    #     return 'אפור כהה'
    elif 50 <= b <= 80 and 80 <= g <= 120 and 110 <= r <= 150:
        return 'אפור כהה מטלי'
    # elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
    #     return 'כחול בהיר'
    # elif 0 <= r <= 20 and 110 <= g <= 140 and 0 <= b <= 20:
    #     return 'ירוק כהה'
    # elif 100 <= b <= 150 and 100 <= g <= 150 and 100 <= r <= 150:
    #     return 'אפור'
    elif 150 <= b <= 200 and 130 <= g <= 160 and 90 <= r <= 120:
        return 'קרם'
    # elif 0 <= r <= 20 and 0 <= g <= 20 and 200 <= b <= 255:
    #     return 'כחול'
    # elif 90 <= r <= 115 and 90 <= g <= 115 and 90 <= b <= 115:
    #     return 'כסוף כהה מטלי'
    # elif 100 <= r <= 150 and 0 <= g <= 30 and 0 <= b <= 30:
    #     return 'בורדו מטל'
    # elif 60 <= r <= 80 and 90 <= g <= 120 and 120 <= b <= 150:
    #     return 'אפור פלדה'
    elif 100 <= b <= 150 and 90 <= g <= 140 and 100 <= r <= 120:
        return 'אפור בהיר מטלי'
    # elif 20 <= r <= 40 and 20 <= g <= 40 and 20 <= b <= 40:
    #     return 'שחור מטלי'
    # elif 240 <= r <= 255 and 190 <= g <= 220 and 0 <= b <= 30:
    #     return 'זהב'
    else:
        return 'צבע לא מוגדר'

async def validation(queue):
    http = urllib3.PoolManager()
    results = []

    while queue:
        item = queue.popleft()
        result = item['license_plate']['license_plate_number']
        if result:
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

            # Make a request using the PoolManager
            response = http.request('GET', full_url)
            # Read and decode the response data
            response_data = response.data.decode('utf-8')

            # Find the position of the word "fields"
            end = response_data.find('fields')
            start = response_data.find('"records"')
            filtered_data = response_data[start:end] if end != -1 and start != -1 else response_data

            # Extract the substring from the start to the position of "fields"
            # if end != -1 and start != -1:
            #     filtered_data = response_data[start:end]
            # else:
            #     filtered_data = response_data

            # Print the filtered data
            print(filtered_data)
            color_start = filtered_data.find('"tzeva_rechev":') + len('"tzeva_rechev":')
            color_end = filtered_data.find(',', color_start)
            nameColorCar = filtered_data[color_start:color_end].strip().strip('"')
            if (nameColorCar == ''):
                continue

            print("Extracted car color from API:", nameColorCar)

            # Load the video
            video_path = 'good1.mp4'
            cap = cv2.VideoCapture(video_path)
            frame_number = int(item['validation']['frame_nmr'])
            car_bbox = item['validation']['car_bbox']  # Assuming it's in a form like '[x, y, w, h]'

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
            dominant_color = get_dominant_color(car_image)
            car_color_name = convert_rgb_to_name(dominant_color)
            print("Detected car color:", car_color_name,"API" ,nameColorCar)

            if car_color_name.lower() == nameColorCar.lower():
                print(f"Color match for license number {result}: {car_color_name}")
            else:
                print(
                    f"Color mismatch for license number {result}: API color - {nameColorCar}, Detected color - {car_color_name}")
            color_match = car_color_name.lower() == nameColorCar.lower()
            results.append({
                'license_plate': result,
                'frame_number': frame_number,
                'color_verified': color_match,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            # results.append({
            #     'license_plate': result,
            #     'frame_number': frame_number,
            #     'color_verified': color_match,
            #     'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # })

            cap.release()
        else:
            print("Failed to extract text from the image.")
    return results

            # for i in range(len(results)):
    #     result = results['license_number'][i]
    #     if result:
    #         # result = result.split('\n')
    #         print("Extracted text:")
    #         print(result)
    #         # Base URL of the API endpoint
    #         base_url = 'https://data.gov.il/api/3/action/datastore_search'
    #         # Resource ID for the specific dataset
    #         resource_id = '053cea08-09bc-40ec-8f7a-156f0677aff3'
    #         mispar_rechev = str(result)
    #
    #         # Create a dictionary of query parameters
    #         query_params = {
    #             'resource_id': resource_id,
    #             'q': mispar_rechev  # Example query parameter
    #         }
    #
    #         # Encode the query parameters and construct the full URL
    #         full_url = f"{base_url}?{urlencode(query_params)}"
    #
    #         # Create a PoolManager instance
    #         http = urllib3.PoolManager()
    #
    #         # Make a request using the PoolManager
    #         response = http.request('GET', full_url)
    #         # Read and decode the response data
    #         response_data = response.data.decode('utf-8')
    #
    #         # Find the position of the word "fields"
    #         end = response_data.find('fields')
    #         start = response_data.find('"records"')
    #
    #         # Extract the substring from the start to the position of "fields"
    #         if end != -1 and start != -1:
    #             filtered_data = response_data[start:end]
    #         else:
    #             filtered_data = response_data
    #
    #         # Print the filtered data
    #         print(filtered_data)
    #         color_start = filtered_data.find('"tzeva_rechev":') + len('"tzeva_rechev":')
    #         color_end = filtered_data.find(',', color_start)
    #         nameColorCar = filtered_data[color_start:color_end].strip().strip('"')
    #         print("Extracted car color from API:", nameColorCar)
    #
    #         # Load the video
    #         video_path = 'good1.mp4'
    #         cap = cv2.VideoCapture(video_path)
    #         frame_number = int(results['frame_nmr'][i])
    #         car_bbox = results['car_bbox'][i]  # Assuming it's in a form like '[x, y, w, h]'
    #
    #         # Set the video to the specific frame number
    #         cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    #         ret, frame = cap.read()
    #
    #         if not ret:
    #             print(f"Failed to extract frame {frame_number} from the video.")
    #             continue
    #
    #         # Extract the car's bounding box from the frame
    #         car_bbox = car_bbox.split()
    #         car_bbox = [float(item) for item in car_bbox]
    #         x, y, w, h = car_bbox
    #         car_image = frame[int(y):int(y + h), int(x):int(x + w)]
    #         print("Shape of car_image:", car_image.shape)
    #
    #         # Get the dominant color of the car image
    #         dominant_color = get_dominant_color(car_image)

            # Convert the dominant color to a more readable format (e.g., closest color name)
            # This is a simplistic approach; for better results, consider using a color library or more advanced method
        #     def convert_rgb_to_name(rgb_color):
        #         r, g, b = rgb_color
        #
        #         if 200 <= r <= 255 and 0 <= g <= 50 and 0 <= b <= 50:
        #             return 'אדום'
        #         elif 0 <= r <= 50 and 200 <= g <= 255 and 0 <= b <= 50:
        #             return 'ירוק'
        #         elif 0 <= r <= 50 and 0 <= g <= 50 and 200 <= b <= 255:
        #             return 'כחול'
        #         elif 200 <= r <= 255 and 200 <= g <= 255 and 0 <= b <= 50:
        #             return 'צהוב'
        #         elif 0 <= r <= 50 and 200 <= g <= 255 and 200 <= b <= 255:
        #             return 'טורקיז'
        #         elif 200 <= r <= 255 and 0 <= g <= 50 and 200 <= b <= 255:
        #             return 'מגנטה'
        #         elif 0 <= r <= 50 and 0 <= g <= 50 and 0 <= b <= 50:
        #             return 'שחור'
        #         elif 200 <= r <= 255 and 200 <= g <= 255 and 200 <= b <= 255:
        #             return 'לבן'
        #         elif 100 <= r <= 150 and 100 <= g <= 150 and 100 <= b <= 150:
        #             return 'אפור'
        #         elif 0 <= r <= 100 and 0 <= g <= 100 and 150 <= b <= 205:
        #             return 'כחול מטל'
        #         elif 180 <= r <= 200 and 180 <= g <= 200 and 180 <= b <= 200:
        #             return 'כסף'
        #         elif 240 <= r <= 255 and 240 <= g <= 255 and 210 <= b <= 235:
        #             return 'בז'
        #         elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
        #             return 'תכלת מטאלי'
        #         elif 245 <= r <= 255 and 245 <= g <= 255 and 230 <= b <= 240:
        #             return 'שנהב לבן'
        #         elif 180 <= r <= 200 and 180 <= g <= 200 and 180 <= b <= 200:
        #             return 'כסף מטלי'
        #         elif 150 <= r <= 180 and 150 <= g <= 180 and 150 <= b <= 180:
        #             return 'אפור כהה'
        #         elif 85 <= r <= 105 and 110 <= g <= 140 and 120 <= b <= 160:
        #             return 'אפור כחול מטלי'
        #         elif 160 <= r <= 185 and 200 <= g <= 225 and 220 <= b <= 240:
        #             return 'כחול בהיר'
        #         elif 0 <= r <= 20 and 110 <= g <= 140 and 0 <= b <= 20:
        #             return 'ירוק כהה'
        #         elif 100 <= r <= 150 and 100 <= g <= 150 and 100 <= b <= 150:
        #             return 'אפור'
        #         elif 0 <= r <= 20 and 0 <= g <= 20 and 100 <= b <= 150:
        #             return 'כחול כהה'
        #         elif 0 <= r <= 20 and 0 <= g <= 20 and 200 <= b <= 255:
        #             return 'כחול'
        #         elif 90 <= r <= 115 and 90 <= g <= 115 and 90 <= b <= 115:
        #             return 'כסוף כהה מטלי'
        #         elif 100 <= r <= 150 and 0 <= g <= 30 and 0 <= b <= 30:
        #             return 'בורדו מטל'
        #         elif 60 <= r <= 80 and 90 <= g <= 120 and 120 <= b <= 150:
        #             return 'אפור פלדה'
        #         elif 150 <= r <= 180 and 150 <= g <= 180 and 150 <= b <= 180:
        #             return 'אפור מטל'
        #         elif 20 <= r <= 40 and 20 <= g <= 40 and 20 <= b <= 40:
        #             return 'שחור מטלי'
        #         elif 240 <= r <= 255 and 190 <= g <= 220 and 0 <= b <= 30:
        #             return 'זהב'
        #         else:
        #             return 'צבע לא מוגדר'
        #
        #         car_color_name = convert_rgb_to_name(dominant_color)
        #         print("Detected car color:", car_color_name)
        #
        #         # Compare the detected color with the API color
        #         if car_color_name.lower() == nameColorCar.lower():
        #             print(f"Color match for license number {result}: {car_color_name}")
        #         else:
        #             print(
        #                 f"Color mismatch for license number {result}: API color - {nameColorCar}, Detected color - {car_color_name}")
        #
        #         # Release the video capture object
        #         cap.release()
        # else:
        #     print("Failed to extract text from the image.")
        #
        #
        #


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


