from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import pandas as pd
import json
import os
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

app = Flask(__name__)

# =============================================================================
# SECURITY CONFIGURATION - CHANGE THESE FOR PRODUCTION!
# =============================================================================
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True if using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session timeout

# =============================================================================
# USER DATABASE - Replace with your organization's authentication system
# =============================================================================
# In production, use a database or integrate with LDAP/Active Directory
USERS = {
    'admin': {
        'password': generate_password_hash('admin123'),  # Change this password!
        'role': 'admin',
        'name': 'Administrator'
    },
    'user1': {
        'password': generate_password_hash('user123'),  # Change this password!
        'role': 'user',
        'name': 'Regular User'
    }
}

# =============================================================================
# DATA LOADING - Cached for performance
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
            # Create sample data if Excel file doesn't exist
            df = pd.DataFrame({
                'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
                'Age': [25, 30, 35, 40, 45, 28, 33, 38],
                'Department': ['IT', 'HR', 'IT', 'Sales', 'IT', 'HR', 'Sales', 'IT'],
                'Salary': [50000, 60000, 70000, 80000, 90000, 55000, 75000, 85000],
                'Experience': [2, 5, 8, 12, 15, 3, 7, 10],
                'City': ['New York', 'Boston', 'New York', 'Chicago', 'Boston', 'Chicago', 'New York', 'Boston']
            })
    return df

# Load data on startup
load_data()

# =============================================================================
# AUTHENTICATION DECORATOR
# =============================================================================
def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    """User login page"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate credentials
        user = USERS.get(username)
        if user and check_password_hash(user['password'], password):
            session.clear()
            session['username'] = username
            session['role'] = user['role']
            session['name'] = user['name']
            session.permanent = True

            app.logger.info(f"User '{username}' logged in successfully")
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            app.logger.warning(f"Failed login attempt for username: {username}")
            flash('Invalid username or password', 'error')

    return render_template("login.html")

@app.route("/logout")
def logout():
    """User logout"""
    username = session.get('username', 'Unknown')
    session.clear()
    app.logger.info(f"User '{username}' logged out")
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# =============================================================================
# APPLICATION ROUTES - All require authentication
# =============================================================================
@app.route("/")
@login_required
def index():
    """Main dashboard page"""
    data = load_data()
    columns = data.columns.tolist()
    return render_template("index.html",
                         columns=columns,
                         username=session.get('name', 'User'),
                         role=session.get('role', 'user'))

@app.route("/get_data", methods=["POST"])
@login_required
def get_data():
    """Get data with selected columns"""
    try:
        data = load_data()
        request_data = request.get_json()
        selected_columns = request_data.get("columns", data.columns.tolist())

        # Validate columns exist
        invalid_cols = [col for col in selected_columns if col not in data.columns]
        if invalid_cols:
            return jsonify({"error": f"Invalid columns: {invalid_cols}"}), 400

        # Filter dataframe to only include selected columns
        filtered_df = data[selected_columns]

        # Convert to JSON format for AG Grid
        result = {
            "data": filtered_df.to_dict("records"),
            "columns": selected_columns
        }

        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in get_data: {str(e)}")
        return jsonify({"error": "Failed to retrieve data"}), 500

@app.route("/get_filtered_data", methods=["POST"])
@login_required
def get_filtered_data():
    """Get filtered data from AG Grid for charting"""
    try:
        request_data = request.get_json()
        filtered_rows = request_data.get("filteredData", [])

        return jsonify({
            "success": True,
            "rowCount": len(filtered_rows),
            "data": filtered_rows
        })
    except Exception as e:
        app.logger.error(f"Error in get_filtered_data: {str(e)}")
        return jsonify({"error": "Failed to process filtered data"}), 500

@app.route("/get_chart_data", methods=["POST"])
@login_required
def get_chart_data():
    """Prepare data for charting"""
    try:
        request_data = request.get_json()
        filtered_data = request_data.get("data", [])
        x_column = request_data.get("xColumn")
        y_column = request_data.get("yColumn")

        if not filtered_data or not x_column or not y_column:
            return jsonify({"error": "Missing required data"}), 400

        # Extract x and y values
        x_values = [row.get(x_column) for row in filtered_data]
        y_values = [row.get(y_column) for row in filtered_data]

        return jsonify({
            "xValues": x_values,
            "yValues": y_values,
            "xColumn": x_column,
            "yColumn": y_column,
        })
    except Exception as e:
        app.logger.error(f"Error in get_chart_data: {str(e)}")
        return jsonify({"error": "Failed to generate chart data"}), 500

@app.route("/get_unique_values", methods=["POST"])
@login_required
def get_unique_values():
    """Get unique values for a specific column (for slicers)"""
    try:
        data = load_data()
        request_data = request.get_json()
        column = request_data.get("column")

        if not column or column not in data.columns:
            return jsonify({"error": "Invalid column"}), 400

        # Get unique values for the column, excluding null/NaN
        unique_values = data[column].dropna().unique().tolist()

        # Convert numpy types to Python types for JSON serialization
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
@app.errorhandler(401)
def unauthorized(e):
    """Handle unauthorized access"""
    if request.is_json:
        return jsonify({'error': 'Unauthorized access'}), 401
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    app.logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    # Development mode - DO NOT USE IN PRODUCTION
    app.run(debug=True, host='0.0.0.0', port=5000)
