from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import main
import add_missing_data
import validation
import util
import pandas as pd

app = Flask(__name__)
CORS(app)

first_request = False  # משתנה גלובלי למעקב אחרי הבקשה הראשונה


async def main_routine():
    frame_queue = await main.process_video()
    print(frame_queue)
    frame_queue = await add_missing_data.interpolated_data(frame_queue)
    frame_queue = await add_missing_data.merge_rows(frame_queue)
    frame_queue = await validation.validation(frame_queue)
    output_path = 'details_cars.csv'
    for item in frame_queue:
        util.write_csv(item, output_path)
    # for item in frame_queue:
    #     res = {'license_plate': item['license_plate'], 'frame_number': item['frame_number'], 'color_verified': True,
    #            'date': item['date']}
    #     append_single_record_to_csv(res, '/details_cars.csv')

# def append_single_record_to_csv(record, output_path, write_header=False):
#    with open(output_path, 'a', newline='') as csvfile:
#        fieldnames = ['license_plate', 'frame_number', 'color_verified', 'date']
#        writer = csv.DictWriter(csvfile, fieldnames=fieldnames
#        if write_header:
#            writer.writeheader(
#        writer.writerow(record)
#
#
#
# util.write_csv(frame_queue, './data.csv')
@app.route('/find_by_number/<int:number>', methods=['GET'])
def find_by_number(number):
    if not number:
        return jsonify({"error": "No number provided"}), 400

    try:
        data = pd.read_csv('./details_cars.csv')

        # המרת עמודת התאריך לפורמט datetime
        data['date'] = pd.to_datetime(data['date'])

        # הסרת השניות מהתאריכים
        data['date'] = data['date'].dt.floor('min')

    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except ValueError:
        return jsonify({"error": "Error parsing date in the data file"}), 400

    # חיפוש לפי מספר רישוי
    result = data[data['license_plate'] == number]
    if result.empty:
        return jsonify({"": "רכב זה לא קיים באגר"})

    return result.to_json(orient='records')


@app.route('/display_by_date/<string:date>', methods=['GET'])
def display_by_date(date):
    if date == 'T':
        return jsonify({"error": "No date provided"}), 400

    try:
        data = pd.read_csv('./details_cars.csv', encoding='ISO-8859-8')

        # המרת עמודת התאריך לפורמט datetime
        data['date'] = pd.to_datetime(data['date'])

        # הסרת השניות מהתאריכים
        data['date'] = data['date'].dt.floor('H')


        # התאריך הרצוי
        target_date = pd.to_datetime(date)

        # סינון השורות עם התאריך הרצוי
        filtered_df = data[data['date'] == target_date]

    except FileNotFoundError:
        return jsonify({"error": "Data file not found"}), 404
    except ValueError:
        return jsonify({"error": "Invalid date format provided"}), 400

    if filtered_df.empty:
        return jsonify({"": "אין פירוט על רכבים בתאריך ו/או בשעה זה/ו"})

    return jsonify(filtered_df.to_dict(orient='records'))



@app.route(f'/add_car_waring/<int:number>', methods=['GET'])
def add_car_waring(number):
    # קרא את הנתונים הקיימים מהקובץ
    data = pd.read_excel('./carWaring.xlsx', header=None)
    print(number)
    if number != 0:
        try:
            # המרת המספר למספר שלם והוספתו לרשימה הקיימת
            number = int(number)
            new_data = pd.DataFrame([number])  # צור DataFrame חדש עבור המספר החדש
            data = pd.concat([data, new_data], ignore_index=True)  # הוסף את המספר לקובץ ה-Excel הקיים
            print(data)
            data.to_excel('./carWaring.xlsx', index=False, header=False)

            # שמירת הנתונים המעודכנים חזרה לקובץ
        except Exception as e:
            return str(e), 500

    data_fixed = []
    for i in range(0, len(data)):
        if i < len(data):
            entry = {str(i + 1): int(data.iloc[i, 0])}
            data_fixed.append(entry)
    return jsonify(data_fixed)

@app.route('/car_warning', methods=['GET'])
def car_warning():
    # קריאת הנתונים מקובץ ה-Excel
    car_warning_data = pd.read_excel('./carWaring.xlsx', header=None)
    car_warning_numbers = car_warning_data[0].tolist()
    # קריאת הנתונים מקובץ ה-CSV
    details_cars_data = pd.read_csv('./details_cars.csv')
    license_plate_numbers = details_cars_data['license_plate'].tolist()
    # חיפוש התאמות בין שני הקבצים
    matched_cars = details_cars_data[details_cars_data['license_plate'].isin(car_warning_numbers)]
    # בדיקת האם יש רכבים בעמודת details_cars_data שמכילים את הערך FALSE
    false_entries = details_cars_data[details_cars_data['color_verified'] == False]

    # החזרת התאמות
    if not matched_cars.empty or not false_entries.empty:
        return jsonify({
            "message": "Matching license plates found",
            "matched_cars": matched_cars.to_dict(orient='records'),
            "false_entries_exist": false_entries.to_dict(orient='records')
        }), 200
    else:
        return jsonify({
            "message": "No matching license plates found",
            "false_entries_exist": not false_entries.empty
        }), 404
            # return "Number added successfully", 200


    # data = pd.read_excel('./carWaring.xlsx', header=None)
    # print(data)
    # data_fixed = []
    # for i in range(0, len(data)):
    #     if i < len(data):
    #         entry = {str(i + 1): int(data.iloc[i, 0])}
    #         data_fixed.append(entry)
    #
    # return jsonify(data_fixed)

# @app.before_request
# def before_first_request_func():
#     global first_request
#     if first_request:
#         first_request = False
#         asyncio.run(main_routine())

if __name__ == "__main__":
    asyncio.run(main_routine())
    app.run(debug=False)

