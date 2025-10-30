from flask import Flask, render_template, request, jsonify
import pandas as pd
import json
import os

app = Flask(__name__)

# Load your Excel data (replace with your file path)
try:
    df = pd.read_excel("data.xlsx")
except FileNotFoundError:
    # Create sample data if Excel file doesn't exist
    df = pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry'],
        'Age': [25, 30, 35, 40, 45, 28, 33, 38],
        'Department': ['IT', 'HR', 'IT', 'Sales', 'IT', 'HR', 'Sales', 'IT'],
        'Salary': [50000, 60000, 70000, 80000, 90000, 55000, 75000, 85000],
        'Experience': [2, 5, 8, 12, 15, 3, 7, 10],
        'City': ['New York', 'Boston', 'New York', 'Chicago', 'Boston', 'Chicago', 'New York', 'Boston']
    })


@app.route("/")
def index():
    # Get all column names
    columns = df.columns.tolist()
    return render_template("index.html", columns=columns)


@app.route("/get_data", methods=["POST"])
def get_data():
    """Get data with selected columns"""
    data = request.get_json()
    selected_columns = data.get("columns", df.columns.tolist())

    # Filter dataframe to only include selected columns
    filtered_df = df[selected_columns]

    # Convert to JSON format for AG Grid
    result = {"data": filtered_df.to_dict("records"), "columns": selected_columns}

    return jsonify(result)


@app.route("/get_filtered_data", methods=["POST"])
def get_filtered_data():
    """Get filtered data from AG Grid for charting"""
    data = request.get_json()
    filtered_rows = data.get("filteredData", [])

    return jsonify(
        {"success": True, "rowCount": len(filtered_rows), "data": filtered_rows}
    )


@app.route("/get_chart_data", methods=["POST"])
def get_chart_data():
    """Prepare data for charting"""
    data = request.get_json()
    filtered_data = data.get("data", [])
    x_column = data.get("xColumn")
    y_column = data.get("yColumn")

    if not filtered_data or not x_column or not y_column:
        return jsonify({"error": "Missing required data"}), 400

    # Extract x and y values
    x_values = [row.get(x_column) for row in filtered_data]
    y_values = [row.get(y_column) for row in filtered_data]

    return jsonify(
        {
            "xValues": x_values,
            "yValues": y_values,
            "xColumn": x_column,
            "yColumn": y_column,
        }
    )


@app.route("/get_unique_values", methods=["POST"])
def get_unique_values():
    """Get unique values for a specific column (for slicers)"""
    data = request.get_json()
    column = data.get("column")

    if not column or column not in df.columns:
        return jsonify({"error": "Invalid column"}), 400

    # Get unique values for the column, excluding null/NaN
    unique_values = df[column].dropna().unique().tolist()

    # Convert numpy types to Python types for JSON serialization
    unique_values = [
        str(val) if not isinstance(val, (int, float, str, bool)) else val
        for val in unique_values
    ]

    return jsonify({"column": column, "uniqueValues": sorted(unique_values, key=lambda x: str(x))})


if __name__ == "__main__":
    app.run(debug=True)
