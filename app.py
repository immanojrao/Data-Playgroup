from flask import Flask, render_template, request, jsonify, session
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# Path to Excel file
DATA_FILE = 'data.xlsx'

def load_data():
    """Load Excel data and convert dates"""
    df = pd.read_excel(DATA_FILE)
    # Convert Date column to datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    return df

@app.route('/')
def index():
    """Main page"""
    df = load_data()
    columns = df.columns.tolist()

    # Get date range for date filter
    if 'Date' in df.columns:
        min_date = df['Date'].min().strftime('%Y-%m-%d')
        max_date = df['Date'].max().strftime('%Y-%m-%d')
    else:
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
        if 'Date' in df.columns:
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        # Convert to dict records
        records = df.to_dict('records')

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

        # Convert to lists
        labels = result.index.tolist()
        values = result.values.tolist()

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
