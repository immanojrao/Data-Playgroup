from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

# Load your Excel data (replace with your file path)
df = pd.read_excel("data.xlsx")


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


if __name__ == "__main__":
    app.run(debug=True)
