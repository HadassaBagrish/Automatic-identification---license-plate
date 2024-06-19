import string
import easyocr

# Initialize the OCR reader
reader = easyocr.Reader(['ang','en'], gpu=False)

# Mapping dictionaries for character conversion
dict_char_to_int_UK = {'O': '0',
                    'I': '1',
                    'J': '3',
                    'A': '4',
                    'G': '6',
                    'S': '5'}
dict_int_to_char_UK = {v: k for k, v in dict_char_to_int_UK.items()}

#
# dict_int_to_char_UK = {'0': 'O',
#                     '1': 'I',
#                     '3': 'J',
#                     '4': 'A',
#                     '6': 'G',
#                     '5': 'S'}

dict_char_to_int_IL = {'0': 0,
                    '1': 1,
                    '2': 2,
                    '3': 3,
                    '4': 4,
                    '5': 5,
                    '6': 6,
                    '7': 7,
                    '8': 8,
                    '9': 9}
dict_int_to_char_IL = {v: k for k, v in dict_char_to_int_IL.items()}

def write_csv(results, output_path):
    """
    Write the results to a CSV file.

    Args:
        results (dict): Dictionary containing the results.
        output_path (str): Path to the output CSV file.
    """
    with open(output_path, 'w') as f:
        f.write('{},{},{},{},{},{},{}\n'.format('frame_nmr', 'car_id', 'car_bbox',
                                                'license_plate_bbox', 'license_plate_bbox_score', 'license_number',
                                                'license_number_score'))

        for frame_nmr in results.keys():
            for car_id in results[frame_nmr].keys():
                print(results[frame_nmr][car_id])
                if 'car' in results[frame_nmr][car_id].keys() and \
                   'license_plate' in results[frame_nmr][car_id].keys() and \
                   'text' in results[frame_nmr][car_id]['license_plate'].keys():
                    f.write('{},{},{},{},{},{},{}\n'.format(frame_nmr,
                                                            car_id,
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['car']['bbox'][0],
                                                                results[frame_nmr][car_id]['car']['bbox'][1],
                                                                results[frame_nmr][car_id]['car']['bbox'][2],
                                                                results[frame_nmr][car_id]['car']['bbox'][3]),
                                                            '[{} {} {} {}]'.format(
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][0],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][1],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][2],
                                                                results[frame_nmr][car_id]['license_plate']['bbox'][3]),
                                                            results[frame_nmr][car_id]['license_plate']['bbox_score'],
                                                            results[frame_nmr][car_id]['license_plate']['text'],
                                                            results[frame_nmr][car_id]['license_plate']['text_score'])
                            )
        f.close()


def license_complies_format(text):
    """
    Check if the license plate text complies with the required format.

    Args:
        text (str): License plate text.

    Returns:
        bool: True if the license plate complies with the format, False otherwise.
    """
    if len(text)< 7:
        return None
    if len(text) == 7:
        if (text[0] in dict_char_to_int_IL.keys()) and \
                (text[1] in dict_char_to_int_IL.keys()) and \
                (text[2] in dict_char_to_int_IL.keys()) and \
                (text[3] in dict_char_to_int_IL.keys()) and \
                (text[4] in dict_char_to_int_IL.keys()) and \
                (text[5] in dict_char_to_int_IL.keys()) and \
                (text[6] in dict_char_to_int_IL.keys()):
            return True

    if len(text) == 8:
        if (text[0] in dict_char_to_int_IL.keys()) and \
                (text[1] in dict_char_to_int_IL.keys()) and \
                (text[2] in dict_char_to_int_IL.keys()) and \
                (text[3] in dict_char_to_int_IL.keys()) and \
                (text[4] in dict_char_to_int_IL.keys()) and \
                (text[5] in dict_char_to_int_IL.keys()) and \
                (text[6] in dict_char_to_int_IL.keys()) and \
                (text[7] in dict_char_to_int_IL.keys()):
            return True



    # if (text[0] in string.ascii_uppercase or text[0] in dict_int_to_char_UK.keys()) and \
    #    (text[1] in string.ascii_uppercase or text[1] in dict_int_to_char_UK.keys()) and \
    #    (text[2] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[2] in dict_char_to_int_UK.keys()) and \
    #    (text[3] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] or text[3] in dict_char_to_int_UK.keys()) and \
    #    (text[4] in string.ascii_uppercase or text[4] in dict_int_to_char_UK.keys()) and \
    #    (text[5] in string.ascii_uppercase or text[5] in dict_int_to_char_UK.keys()) and \
    #    (text[6] in string.ascii_uppercase or text[6] in dict_int_to_char_UK.keys()):
    #     return True

    else:
        return False


def format_license(text):
    """
    Format the license plate text by converting characters using the mapping dictionaries.

    Args:
        text (str): License plate text.

    Returns:
        str: Formatted license plate text.
    """
    license_plate_ = ''
    mapping = {0: dict_int_to_char_IL, 1: dict_int_to_char_IL, 4: dict_int_to_char_IL, 5: dict_int_to_char_IL,
               6: dict_int_to_char_IL,
               2: dict_char_to_int_IL, 3: dict_char_to_int_IL}
    # mapping = {0: dict_int_to_char_UK, 1: dict_int_to_char_UK, 4: dict_int_to_char_UK, 5: dict_int_to_char_UK, 6: dict_int_to_char_UK,
    #            2: dict_char_to_int_UK, 3: dict_char_to_int_UK}
    for j in [0, 1, 2, 3, 4, 5, 6]:
        if text[j] in mapping[j].keys():
            license_plate_ += mapping[j][text[j]]
        else:
            license_plate_ += text[j]

    return license_plate_


def read_license_plate(license_plate_crop):
    """
    Read the license plate text from the given cropped image.

    Args:
        license_plate_crop (PIL.Image.Image): Cropped image containing the license plate.

    Returns:
        tuple: Tuple containing the formatted license plate text and its confidence score.
    """
    import string
    detections = reader.readtext(license_plate_crop)
    score = 0
    for detection in detections:
        bbox, text, score = detection


        text = text.upper().replace(' ', '')
        translator = str.maketrans("", "", string.punctuation)
        text = text.translate(translator)
        if text == '164603':
            print('1')


        if license_complies_format(text):
            return text, score
            # return format_license(text), score

    return None, None


def get_car(license_plate, vehicle_track_ids):
    """
    Retrieve the vehicle coordinates and ID based on the license plate coordinates.

    Args:
        license_plate (tuple): Tuple containing the coordinates of the license plate (x1, y1, x2, y2, score, class_id).
        vehicle_track_ids (list): List of vehicle track IDs and their corresponding coordinates.

    Returns:
        tuple: Tuple containing the vehicle coordinates (x1, y1, x2, y2) and ID.
    """
    x1, y1, x2, y2, score, class_id = license_plate

    foundIt = False
    for j in range(len(vehicle_track_ids)):
        xcar1, ycar1, xcar2, ycar2, car_id = vehicle_track_ids[j]

        if x1 > xcar1 and y1 > ycar1 and x2 < xcar2 and y2 < ycar2:
            car_indx = j
            foundIt = True
            break

    if foundIt:
        return vehicle_track_ids[car_indx]

    return -1, -1, -1, -1, -1