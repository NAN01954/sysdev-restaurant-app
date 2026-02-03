from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from google.cloud import firestore
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth
import os
from datetime import datetime
import pathlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

db = firestore.Client()

# Cloud SQL connection
CONNECTION_NAME = "sysdev-coursework:us-central1:restaurant-db"
DB_USER = "postgres"
DB_PASS = "YOUR_DB_PASSWORD_HERE"
DB_NAME = "restaurant"

# Check if running locally or on App Engine
if os.environ.get('GAE_ENV', '').startswith('standard'):
    # Running on App Engine - use Unix socket
    db_socket_dir = "/cloudsql"
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@/{DB_NAME}?host={db_socket_dir}/{CONNECTION_NAME}",
        poolclass=NullPool,
    )
else:
    # Running locally - use TCP connection
    DB_HOST = "35.239.32.15"
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}",
        poolclass=NullPool,
    )

# NOTE: In production, use Google Secret Manager or environment variables
GOOGLE_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
GOOGLE_CLIENT_SECRET = "YOUR_CLIENT_SECRET_HERE"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

def is_logged_in():
    return 'user' in session

@app.route('/')
def home():
    return render_template('home.html', user=session.get('user'))

@app.route('/menu')
def menu():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, description, price, category FROM menu_items WHERE available = true"))
        menu_items = [dict(row._mapping) for row in result]
    return render_template('menu.html', menu_items=menu_items, user=session.get('user'))

@app.route('/login')
def login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/callback"]
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"]
    )
    flow.redirect_uri = url_for('callback', _external=True)
    authorization_url, state = flow.authorization_url(prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:8080/callback"]
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        state=session['state']
    )
    flow.redirect_uri = url_for('callback', _external=True)
    flow.fetch_token(authorization_response=request.url)
    
    credentials = flow.credentials
    import requests as req
    userinfo_response = req.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"}
    )
    
    userinfo = userinfo_response.json()
    session['user'] = {
        'email': userinfo['email'],
        'name': userinfo['name']
    }
    
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        selected_items = request.form.getlist('items')
        
        total = 0.0
        for item_str in selected_items:
            price = float(item_str.split('£')[1])
            total += price
        
        order_data = {
            'user_email': session['user']['email'],
            'user_name': session['user']['name'],
            'items': selected_items,
            'total': total,
            'status': 'pending',
            'timestamp': datetime.now()
        }
        
        db.collection('orders').add(order_data)
        
        return redirect(url_for('my_orders'))
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, price FROM menu_items WHERE available = true"))
        menu_items = [dict(row._mapping) for row in result]
    return render_template('order.html', menu_items=menu_items, user=session.get('user'))

@app.route('/my-orders')
def my_orders():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_email = session['user']['email']
    orders_ref = db.collection('orders').where('user_email', '==', user_email)
    orders = []
    
    for order in orders_ref.stream():
        order_dict = order.to_dict()
        order_dict['id'] = order.id
        orders.append(order_dict)
    
    return render_template('my_orders.html', orders=orders, user=session.get('user'))

@app.route('/api/menu')
def api_menu():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT id, name, description, price, category FROM menu_items WHERE available = true"))
        menu_items = [dict(row._mapping) for row in result]
    return jsonify(menu_items)

@app.route('/api/order', methods=['POST'])
def api_order():
    if not is_logged_in():
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.get_json()
    
    order_data = {
        'user_email': session['user']['email'],
        'user_name': session['user']['name'],
        'items': data.get('items', []),
        'total': data.get('total', 0.0),
        'status': 'pending',
        'timestamp': datetime.now()
    }
    
    doc_ref = db.collection('orders').add(order_data)
    
    return jsonify({'success': True, 'order_id': doc_ref[1].id}), 201

if __name__ == '__main__':
    print("Starting Flask app on port 8080...")
    app.run(host='0.0.0.0', port=8080, debug=True)