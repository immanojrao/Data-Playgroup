from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import os
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)

# =============================================================================
# CORS Configuration for React Frontend
# =============================================================================
CORS(app, supports_credentials=True, origins=['http://localhost:3000', 'http://localhost:5000'])

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# =============================================================================
# USER DATABASE
# =============================================================================
USERS = {
    'admin': {
        'password': generate_password_hash('admin123'),
        'role': 'admin',
        'name': 'Administrator'
    },
    'user1': {
        'password': generate_password_hash('user123'),
        'role': 'user',
        'name': 'Regular User'
    }
}

# =============================================================================
# DATA LOADING
# =============================================================================
df = None

def load_data():
    """Load Excel data once and cache it"""
    global df
    if df is None:
        try:
            data_file = os.environ.get('DATA_FILE', 'data.xlsx')
            df = pd.read_excel(data_file)
            app.logger.info(f"Loaded data from {data_file}: {df.shape[0]} rows, {df.shape[1]} columns")
        except FileNotFoundError:
            app.logger.warning("Data file not found, creating sample data")
            df = pd.DataFrame({
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
                'Age': [25, 30, 35, 40, 45, 28, 33, 38],
                'Department': ['IT', 'HR', 'IT', 'Sales', 'IT', 'HR', 'Sales', 'IT'],
                'Salary': [50000, 60000, 70000, 80000, 90000, 55000, 75000, 85000],
                'Experience': [2, 5, 8, 12, 15, 3, 7, 10],
                'City': ['New York', 'Boston', 'New York', 'Chicago', 'Boston', 'Chicago', 'New York', 'Boston']
            })
    return df

load_data()

# =============================================================================
# AUTHENTICATION DECORATOR
# =============================================================================
def login_required(f):
    """Decorator to require login for API routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# AUTHENTICATION API ENDPOINTS
# =============================================================================
@app.route("/api/login", methods=["POST"])
def login():
    """User login API"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = USERS.get(username)
    if user and check_password_hash(user['password'], password):
        session.clear()
        session['username'] = username
        session['role'] = user['role']
        session['name'] = user['name']
        session.permanent = True

        app.logger.info(f"User '{username}' logged in successfully")
        return jsonify({
            'success': True,
            'user': {
                'username': username,
                'name': user['name'],
                'role': user['role']
            }
        })
    else:
        app.logger.warning(f"Failed login attempt for username: {username}")
        return jsonify({'error': 'Invalid username or password'}), 401

@app.route("/api/logout", methods=["POST"])
def logout():
    """User logout API"""
    username = session.get('username', 'Unknown')
    session.clear()
    app.logger.info(f"User '{username}' logged out")
    return jsonify({'success': True})

@app.route("/api/session", methods=["GET"])
def check_session():
    """Check if user is logged in"""
    if 'username' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'username': session['username'],
                'name': session['name'],
                'role': session['role']
            }
        })
    return jsonify({'authenticated': False}), 401

# =============================================================================
# DATA API ENDPOINTS
# =============================================================================
@app.route("/api/columns", methods=["GET"])
@login_required
def get_columns():
    """Get all column names"""
    data = load_data()
    return jsonify({'columns': data.columns.tolist()})

@app.route("/api/data", methods=["POST"])
@login_required
def get_data():
    """Get data with selected columns"""
    try:
        data = load_data()
        request_data = request.get_json()
        selected_columns = request_data.get("columns", data.columns.tolist())

        invalid_cols = [col for col in selected_columns if col not in data.columns]
        if invalid_cols:
            return jsonify({"error": f"Invalid columns: {invalid_cols}"}), 400

        filtered_df = data[selected_columns]

        return jsonify({
            "data": filtered_df.to_dict("records"),
            "columns": selected_columns
        })
    except Exception as e:
        app.logger.error(f"Error in get_data: {str(e)}")
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route("/api/unique-values", methods=["POST"])
@login_required
def get_unique_values():
    """Get unique values for a specific column (for slicers)"""
    try:
        data = load_data()
        request_data = request.get_json()
        column = request_data.get("column")

        if not column or column not in data.columns:
            return jsonify({"error": "Invalid column"}), 400

        unique_values = data[column].dropna().unique().tolist()
        unique_values = [
            str(val) if not isinstance(val, (int, float, str, bool)) else val
            for val in unique_values
        ]

        return jsonify({
            "column": column,
            "uniqueValues": sorted(unique_values, key=lambda x: str(x))
        })
    except Exception as e:
        app.logger.error(f"Error in get_unique_values: {str(e)}")
        return jsonify({"error": "Failed to get unique values"}), 500

# =============================================================================
# ERROR HANDLERS
# =============================================================================
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
