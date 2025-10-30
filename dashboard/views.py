from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import json
import os
from pathlib import Path

# Build paths to find the Excel file
BASE_DIR = Path(__file__).resolve().parent.parent

# Load your Excel data (replace with your file path)
try:
    df = pd.read_excel(os.path.join(BASE_DIR, 'data.xlsx'))
except FileNotFoundError:
    # If data.xlsx doesn't exist, create a sample DataFrame
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
        'Age': [25, 30, 35, 40, 45],
        'Department': ['IT', 'HR', 'IT', 'Sales', 'IT'],
        'Salary': [50000, 60000, 70000, 80000, 90000],
        'Experience': [2, 5, 8, 12, 15]
    })


def index(request):
    """Main view - renders the dashboard"""
    # Get all column names
    columns = df.columns.tolist()
    return render(request, 'dashboard/index.html', {'columns': columns})


@csrf_exempt
def get_data(request):
    """Get data with selected columns"""
    if request.method == 'POST':
        data = json.loads(request.body)
        selected_columns = data.get('columns', df.columns.tolist())

        # Filter dataframe to only include selected columns
        filtered_df = df[selected_columns]

        # Convert to JSON format for AG Grid
        result = {
            'data': filtered_df.to_dict('records'),
            'columns': selected_columns
        }

        return JsonResponse(result)

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def get_filtered_data(request):
    """Get filtered data from AG Grid for charting"""
    if request.method == 'POST':
        data = json.loads(request.body)
        filtered_rows = data.get('filteredData', [])

        return JsonResponse({
            'success': True,
            'rowCount': len(filtered_rows),
            'data': filtered_rows
        })

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def get_chart_data(request):
    """Prepare data for charting"""
    if request.method == 'POST':
        data = json.loads(request.body)
        filtered_data = data.get('data', [])
        x_column = data.get('xColumn')
        y_column = data.get('yColumn')

        if not filtered_data or not x_column or not y_column:
            return JsonResponse({'error': 'Missing required data'}, status=400)

        # Extract x and y values
        x_values = [row.get(x_column) for row in filtered_data]
        y_values = [row.get(y_column) for row in filtered_data]

        return JsonResponse({
            'xValues': x_values,
            'yValues': y_values,
            'xColumn': x_column,
            'yColumn': y_column
        })

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)


@csrf_exempt
def get_unique_values(request):
    """Get unique values for a specific column (for slicers)"""
    if request.method == 'POST':
        data = json.loads(request.body)
        column = data.get('column')

        if not column or column not in df.columns:
            return JsonResponse({'error': 'Invalid column'}, status=400)

        # Get unique values for the column, excluding null/NaN
        unique_values = df[column].dropna().unique().tolist()

        # Convert numpy types to Python types
        unique_values = [str(val) if not isinstance(val, (int, float, str, bool)) else val for val in unique_values]

        return JsonResponse({
            'column': column,
            'uniqueValues': sorted(unique_values, key=lambda x: str(x))
        })

    return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
