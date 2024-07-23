from flask import Flask, render_template, request, jsonify
import sqlite3

DB_PATH = 'sql/app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY, plate TEXT, description TEXT)''')
    conn.commit()
    conn.close()
    print("Database initialized")

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads'

#--------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

#--------------------------------------------
@app.route('/register', methods=['POST'])
def register():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Example data: current timestamp. Modify as needed.
    car_description = request.json['description']
    car_plate = request.json['plate']
    c.execute("INSERT INTO cars (plate, description) VALUES (?, ?)", (car_plate, car_description))
    conn.commit()
    conn.close()
    return jsonify({"message": "Data registered"})

#--------------------------------------------
@app.route('/cars', methods=['GET'])
def get_cars():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cars")
    cars = c.fetchall()
    conn.close()
    
    # Convert the list of tuples into a list of dictionaries
    cars_list = [{"id": car[0], "plate":car[1], "description": car[2]} for car in cars]
    
    response = jsonify(cars_list)
    return response


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
