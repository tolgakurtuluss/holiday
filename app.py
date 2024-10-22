import random
from flask import Flask, render_template, request, send_file, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient(os.environ.get("MONGODB_URI"))  # Update with your MongoDB connection string
db = client['holiday_db']  # Use the same database
collection = db['holidays']  # Use the same collection

@app.route('/')
def index():
    # Fetch all holidays from MongoDB
    data = list(collection.find({}))
    
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

    # Fetch filtered data from MongoDB
    filtered_data = list(collection.find({'country': country, 'Year': int(year)}))

    # Process the data
    for holiday in filtered_data:
        holiday['Date'] = holiday['Date'].strftime('%Y-%m-%d')  # Ensure Date is in string format

    # Get the unique years from the dataset
    years = list(set(item['Year'] for item in collection.find({})))

    return render_template('calendar.html', holidays=filtered_data, country=country, year=year, years=years)

@app.route('/download')
def download():
    country = request.args.get('country')
    year = request.args.get('year')

    # Fetch filtered data for the download
    filtered_data = list(collection.find({'country': country, 'Year': int(year)}))

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(filtered_data)
    file_path = f'temp_holidays_{country}_{year}.xlsx'
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/api/holidays')
def api_holidays():
    country = request.args.get('country')
    year = request.args.get('year')

    # Fetch filtered data for the API
    filtered_data = list(collection.find({'country': country, 'Year': int(year)}))

    # Process the data
    for holiday in filtered_data:
        holiday['Date'] = holiday['Date'].strftime('%d.%m.%Y')  # Ensure Date is in string format

    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
