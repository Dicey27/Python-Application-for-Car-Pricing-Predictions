import psycopg2
from flask import Flask, request, render_template, redirect, url_for, session, flash, jsonify
import pandas as pd
import plotly.graph_objs as go
from PricePrediciton import estimate_price
import json
import plotly.express as px
import plotly
import csv
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = 'mysecret'
bcrypt = Bcrypt(app)


def get_db_connection():
    return psycopg2.connect(host='localhost', dbname='AutoEstimateHub', user='postgres', password='admin')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        user = cur.fetchone()
        if user:
            flash('Username or email already exists!')
            return redirect(url_for('register'))

        cur.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed_password, email))
        conn.commit()
        cur.close()
        conn.close()

        flash('Registered successfully! Please login.')
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']


        if username == 'admin' and password == 'admin':
            session['username'] = username
            session['role'] = 'administrator'
            flash('Logged in successfully as administrator!')
            return redirect(url_for('home'))
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()

            if user and bcrypt.check_password_hash(user[0], password):
                session['username'] = username
                session['role'] = 'user'
                flash('Logged in successfully!')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password!')
                return render_template('login.html')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')

    return redirect(url_for('home'))


@app.route('/')
def home():
    username = session.get('username', None)
    return render_template('masin.html', username=username)


@app.route('/arbdecizie')
def arbdecizie():
     return render_template('arbdecizie.html')


@app.route('/predict', methods=['POST'])
def predict():

    marca = request.form['marca']
    model = request.form['model']
    anul = int(request.form['anul'])
    kilometrajul = int(request.form['kilometrajul'].replace(' ', ''))
    capacitatea_motorului = int(request.form['capacitatea_motorului'].replace(' ', ''))
    tipul_de_combustibil = request.form['tipul_de_combustibil']


    estimated_price = estimate_price(marca, model, anul, kilometrajul, capacitatea_motorului, tipul_de_combustibil)


    return render_template('result.html', prediction=f'{estimated_price:,.2f} EUR')


@app.route('/compara', methods=['GET', 'POST'])
def compare():
    if request.method == 'POST':
        df = pd.read_csv('detalii_masini_complet.csv')
        df['Preț'] = pd.to_numeric(df['Preț'].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        df['Kilometrajul'] = pd.to_numeric(df['Kilometrajul'].str.replace(r'[^\d.]', '', regex=True), errors='coerce')

        marca = request.form['marca']
        model = request.form['model']
        anul = int(request.form['anul'])
        kilometrajul = int(request.form['kilometrajul'].replace(' km', '').replace(',', '').strip())
        capacitatea_motorului = int(request.form['capacitatea_motorului'].replace(' cm3', '').replace(',', '').strip())
        tipul_de_combustibil = request.form['tipul_de_combustibil']


        predicted_price = estimate_price(
            marca,
            model,
            anul,
            kilometrajul,
            capacitatea_motorului,
            tipul_de_combustibil
        )


        filtered_data = df[
            (df['Marca'].str.lower() == marca.lower()) &
            (df['Model'].str.lower() == model.lower())
        ]


        fig_year = px.scatter(filtered_data, x='Anul', y='Preț',
                         hover_data=['Marca', 'Model', 'Kilometrajul', 'Capacitatea motorului', 'Tipul de combustibil'],
                         title=f'Price vs. Year Overview for {marca} {model}')


        fig_mileage = px.scatter(filtered_data, x='Kilometrajul', y='Preț',
                                 hover_data=['Marca', 'Model', 'Anul', 'Capacitatea motorului', 'Tipul de combustibil'],
                                 title=f'Price vs. Mileage Overview for {marca} {model}')

        fig_mileage.add_trace(go.Scatter(
            x=[kilometrajul],
            y=[predicted_price],
            marker=dict(color='green', size=12),
            mode='markers',
            hoverinfo='text',
            hovertext=(
                f'<b>Anul:</b> {anul}<br>'
                f'<b>Preț:</b> {predicted_price:.2f} EUR<br>'
                f'<b>Marca:</b> {marca}<br>'
                f'<b>Model:</b> {model}<br>'
                f'<b>Kilometrajul:</b> {kilometrajul} km<br>'
                f'<b>Capacitatea motorului:</b> {capacitatea_motorului} cm3<br>'
                f'<b>Tipul de combustibil:</b> {tipul_de_combustibil}'
            ),
            name='Your car'
        ))

        fig_year.add_trace(go.Scatter(
            x=[anul],
            y=[predicted_price],
            marker=dict(color='green', size=12),
            mode='markers',
            hoverinfo='text',
            hovertext=(
                f'<b>Anul:</b> {anul}<br>'
                f'<b>Preț:</b> {predicted_price:.2f} EUR<br>'
                f'<b>Marca:</b> {marca}<br>'
                f'<b>Model:</b> {model}<br>'
                f'<b>Kilometrajul:</b> {kilometrajul} km<br>'
                f'<b>Capacitatea motorului:</b> {capacitatea_motorului} cm3<br>'
                f'<b>Tipul de combustibil:</b> {tipul_de_combustibil}'
            ),
            name='Your car'
        ))



        graphJSON_year = json.dumps(fig_year, cls=plotly.utils.PlotlyJSONEncoder)
        graphJSON_mileage = json.dumps(fig_mileage, cls=plotly.utils.PlotlyJSONEncoder)


        return render_template('compara.html', graphJSON_year=graphJSON_year, graphJSON_mileage=graphJSON_mileage)
    else:

        return render_template('compara.html')


@app.route('/get-csv-data')
def get_csv_data():
    data = pd.read_csv('C://Users//edcs9//Desktop//pythonProject1interfata//detalii_masini_complet.csv')
    return jsonify(data.to_dict(orient='records'))

@app.route('/inventar')
def inventar():
    data = []
    try:
        with open('detalii_masini_complet.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                data.append(row)
    except IOError:
        print("Error: File does not appear to exist.")
    return render_template('inventar.html', data=data)

@app.route('/data')
def data():
    data = []
    with open('detalii_masini_complet.csv', mode='r', encoding='utf-8-sig') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            data.append(row)
    return jsonify(data)

@app.route('/graphs')
def graphs():
    data = pd.read_csv('C://Users//edcs9//Desktop//pythonProject1interfata//detalii_masini_complet.csv')
    data_json = data.to_json(orient='records')
    # print(data_json)
    return render_template('graphs.html', data_json=data_json)

@app.route('/predict', methods=['GET'])
def predict_form():
    return render_template('PricePredict.html')

@app.route('/anuntmasina')
def anuntmasina():
    return render_template('anuntmasina.html')

@app.route('/anuntmasina2')
def anuntmasina2():
    return render_template('anuntmasina2.html')

@app.route('/anuntmasina3')
def anuntmasina3():
    return render_template('anuntmasina3.html')

@app.route('/anuntmasina4')
def anuntmasina4():
    return render_template('anuntmasina4.html')

@app.route('/anuntmasina5')
def anuntmasina5():
    return render_template('anuntmasina5.html')

@app.route('/sell_car')
def sell_car():
        return render_template('vanzare.html')


@app.route('/add_masini', methods=['POST'])
def add_masini():
    data = request.json
    make = data.get('make')
    model = data.get('model')
    year = data.get('year')
    price = data.get('price')
    phone = data.get('phone')


    if not all([make, model, year, price]):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400

    try:
        conn = psycopg2.connect(host='localhost', dbname='AutoEstimateHub', user='postgres', password='admin')
        cur = conn.cursor()
        # Omitting user_id for now in the insertion
        cur.execute('INSERT INTO masini (make, model, year, price ,phone) VALUES (%s, %s, %s, %s, %s)',
                    (make, model, int(year), float(price),int(phone)))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/masinilavanzare.html')
def masinilavanzare():
    try:
        conn = psycopg2.connect(host='localhost', dbname='AutoEstimateHub', user='postgres', password='admin')
        cur = conn.cursor()
        cur.execute('SELECT make, model, year, price, phone FROM masini')
        listings = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('masinilavanzare.html', listings=listings)
    except Exception as e:
        print("Error fetching from the database:", e)
        return "Error fetching listings", 500

if __name__ == '__main__':
    app.run(debug=True)
