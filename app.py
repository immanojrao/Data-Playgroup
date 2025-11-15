from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Path to Excel file
DATA_FILE = 'data.xlsx'

def convert_to_json_serializable(obj):
    """Convert pandas/numpy objects to JSON-serializable types"""
    if pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, datetime)):
        return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (list, tuple)):
        return [convert_to_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_to_json_serializable(v) for k, v in obj.items()}
    else:
        return obj

def load_data():
    """Load Excel data and convert dates"""
    df = pd.read_excel(DATA_FILE)

    # Convert Date column to datetime with robust handling
    if 'Date' in df.columns:
        try:
            # Try to convert dates, coercing errors to NaT
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

            # If all values became NaT, try common date formats
            if df['Date'].isna().all():
                date_formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y', '%m-%d-%Y']
                for fmt in date_formats:
                    try:
                        df['Date'] = pd.to_datetime(df['Date'], format=fmt, errors='coerce')
                        if not df['Date'].isna().all():
                            break
                    except:
                        continue

            # Log warning if some dates couldn't be parsed
            null_count = df['Date'].isna().sum()
            if null_count > 0:
                print(f"Warning: {null_count} date values could not be parsed and were set to null")
        except Exception as e:
            print(f"Error converting dates: {str(e)}")
            # Keep original values if conversion fails completely
            pass

    # Auto-detect and convert other date-like columns
    for col in df.columns:
        if col != 'Date' and df[col].dtype == 'object':
            # Try to detect if column contains dates
            sample_val = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
            if sample_val and isinstance(sample_val, str):
                # Check if it looks like a date
                if any(sep in str(sample_val) for sep in ['-', '/', '.']):
                    try:
                        converted = pd.to_datetime(df[col], errors='coerce')
                        # If more than 50% converted successfully, it's likely a date column
                        if converted.notna().sum() / len(df) > 0.5:
                            df[col] = converted
                    except:
                        pass

    return df

@app.route('/')
def index():
    """Main page"""
    df = load_data()
    columns = df.columns.tolist()

    # Get date range for date filter
    min_date = max_date = None
    if 'Date' in df.columns:
        try:
            # Filter out NaT values before getting min/max
            valid_dates = df['Date'].dropna()
            if len(valid_dates) > 0:
                min_date_obj = valid_dates.min()
                max_date_obj = valid_dates.max()
                # Ensure proper conversion to string
                min_date = convert_to_json_serializable(min_date_obj)
                max_date = convert_to_json_serializable(max_date_obj)
        except Exception as e:
            print(f"Error getting date range: {str(e)}")
            # Use default dates if conversion fails
            min_date = max_date = None

    return render_template('index.html',
                         columns=columns,
                         min_date=min_date,
                         max_date=max_date)

@app.route('/api/data', methods=['POST'])
def get_data():
    """Get filtered data based on selected columns and date range"""
    try:
        data = request.get_json()
        selected_columns = data.get('columns', [])
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        df = load_data()

        # Apply date filter if provided
        if start_date and end_date and 'Date' in df.columns:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        # Select only requested columns
        if selected_columns:
            df = df[selected_columns]

        # Convert dates to string for JSON serialization
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # Convert datetime to string, NaT becomes None
                df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) else None)

        # Convert to dict records and ensure all values are JSON serializable
        records = df.to_dict('records')
        records = [convert_to_json_serializable(record) for record in records]

        # Save state in session
        session['selected_columns'] = selected_columns
        session['start_date'] = start_date.strftime('%Y-%m-%d') if isinstance(start_date, pd.Timestamp) else start_date
        session['end_date'] = end_date.strftime('%Y-%m-%d') if isinstance(end_date, pd.Timestamp) else end_date

        return jsonify({
            'success': True,
            'data': records,
            'columns': selected_columns
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chart-data', methods=['POST'])
def get_chart_data():
    """Get aggregated data for charts"""
    try:
        data = request.get_json()
        chart_type = data.get('chart_type', 'bar')
        x_column = data.get('x_column')
        y_column = data.get('y_column')
        aggregation = data.get('aggregation', 'sum')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if not x_column or not y_column:
            return jsonify({'success': False, 'error': 'X and Y columns are required'}), 400

        df = load_data()

        # Apply date filter
        if start_date and end_date and 'Date' in df.columns:
            start_date = pd.to_datetime(start_date)
            end_date = pd.to_datetime(end_date)
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        # Group by x_column and aggregate y_column
        if aggregation == 'sum':
            result = df.groupby(x_column)[y_column].sum()
        elif aggregation == 'average':
            result = df.groupby(x_column)[y_column].mean()
        elif aggregation == 'max':
            result = df.groupby(x_column)[y_column].max()
        elif aggregation == 'min':
            result = df.groupby(x_column)[y_column].min()
        elif aggregation == 'count':
            result = df.groupby(x_column)[y_column].count()
        else:
            result = df.groupby(x_column)[y_column].sum()

        # Convert to lists and ensure JSON serializable
        labels = [convert_to_json_serializable(x) for x in result.index.tolist()]
        values = [convert_to_json_serializable(x) for x in result.values.tolist()]

        return jsonify({
            'success': True,
            'labels': labels,
            'values': values,
            'chart_type': chart_type
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/session', methods=['GET'])
def get_session():
    """Get saved session state"""
    return jsonify({
        'selected_columns': session.get('selected_columns', []),
        'start_date': session.get('start_date'),
        'end_date': session.get('end_date')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
