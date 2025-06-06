import os
import random
from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Excel file path
EXCEL_FILE_PATH = 'data/data.xlsx'

# Load data from Excel file
df = pd.read_excel(EXCEL_FILE_PATH)
data = df.to_dict('records')

@app.route('/')
def index():
    # Fetch all holidays from Excel data
    
    countries = list(set(item['country'] for item in data))
    years = list(set(item['Year'] for item in data))
    
    # Generate random links
    random_links = []
    for _ in range(5):  # Generate 5 random links
        random_country = random.choice(countries)
        random_year = random.choice(years)
        random_links.append((random_country, random_year))

    return render_template('index.html', countries=countries, years=years, random_links=random_links)

@app.route('/calendar')
def calendar():
    country = request.args.get('country')
    year = request.args.get('year')

    # Fetch filtered data from Excel data
    filtered_data = [item for item in data if item['country'] == country and str(item['Year']) == year]

    # Process the data
    for holiday in filtered_data:
        holiday['Date'] = pd.to_datetime(holiday['Date']).strftime('%Y-%m-%d')  # Ensure Date is in string format

    # Get the unique years from the dataset
    years = list(set(item['Year'] for item in data))

    return render_template('calendar.html', holidays=filtered_data, country=country, year=year, years=years)

@app.route('/download')
def download():
    country = request.args.get('country')
    year = request.args.get('year')

    # Fetch filtered data from Excel data
    filtered_data = [item for item in data if item['country'] == country and str(item['Year']) == year]
    
    if not filtered_data:
        return "No data found for the specified country and year.", 404

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(filtered_data)
    file_path = f'holidays_{country}_{year}.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@app.route('/api/holidays')
def api_holidays():
    country = request.args.get('country')
    year = request.args.get('year')

    # Fetch filtered data from Excel data
    filtered_data = [item for item in data if item['country'] == country and str(item['Year']) == year]
    
    if not filtered_data:
        return jsonify({"error": "No data found for the specified country and year."}), 404

    # Process the data
    for holiday in filtered_data:
        holiday['Date'] = pd.to_datetime(holiday['Date']).strftime('%d.%m.%Y')  # Ensure Date is in string format

    return jsonify(filtered_data)


if __name__ == '__main__':
    app.run(debug=True)
