# Data Analysis Dashboard

A simple and clean web application for analyzing Excel data with interactive tables and charts.

## Features

✅ **Column Selection** - Choose which columns to display in the data grid
✅ **Interactive Data Grid** - Sort, filter, and search data using AG Grid
✅ **Date Filter** - Filter data by date range (applies to both grid and charts)
✅ **Dynamic Charts** - Create various chart types with your data
✅ **Multiple Chart Types** - Bar, Line, Pie, Doughnut, Radar, and Polar Area charts
✅ **Data Aggregation** - Sum, Average, Max, Min, and Count operations
✅ **State Persistence** - Your selections are saved during your session
✅ **Clean Blue Theme** - Simple, professional interface with blue color scheme

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Prepare Your Data

Place your Excel file in the project folder and name it `data.xlsx`. The file should have a `Date` column for date filtering to work.

**Example data structure:**
```
Product   | Category    | Sales | Quantity | Region | Date
Laptop    | Electronics | 1200  | 15       | North  | 2024-01-15
Mouse     | Electronics | 250   | 50       | South  | 2024-01-16
```

### 3. Run the Application

```bash
python app.py
```

### 4. Open in Browser

Navigate to: `http://localhost:5000`

## How to Use

### Selecting Columns

1. Check/uncheck columns in the "Select Columns to Display" section
2. Click "Load Data" to update the grid

### Filtering by Date

1. Select a start and end date in the "Date Filter" section
2. Click "Apply Filter"
3. The filter applies to both the data grid and charts

### Creating Charts

1. **Select Chart Type** - Choose from Bar, Line, Pie, etc.
2. **Select X-Axis Column** - The column for grouping (e.g., Category, Region)
3. **Select Y-Axis Column** - The column to measure (e.g., Sales, Quantity)
4. **Select Aggregation** - How to combine values (Sum, Average, Max, Min, Count)
5. **Click "Generate Chart"**

### Grid Features

The data grid has built-in features:
- **Sort** - Click column headers to sort
- **Filter** - Use the filter boxes below column headers
- **Search** - Type in filter boxes to search
- **Pagination** - Navigate through pages of data

Your grid filters work independently from column selection and date filters.

## File Structure

```
.
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── data.xlsx             # Your Excel data file
└── templates/
    └── index.html        # Web interface
```

## Requirements

- Python 3.7+
- Flask 3.0.0
- pandas 2.1.4
- openpyxl 3.1.2

## API Endpoints

### POST /api/data
Get filtered data based on selected columns and date range

**Request:**
```json
{
  "columns": ["Product", "Sales", "Date"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "columns": [...]
}
```

### POST /api/chart-data
Get aggregated data for charts

**Request:**
```json
{
  "chart_type": "bar",
  "x_column": "Category",
  "y_column": "Sales",
  "aggregation": "sum",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31"
}
```

**Response:**
```json
{
  "success": true,
  "labels": ["Electronics", "Furniture"],
  "values": [6228, 6925]
}
```

### GET /api/session
Get saved session state (selected columns and date range)

## Tips

- **Column Selection**: Uncheck columns you don't need to focus on relevant data
- **Date Range**: Narrow down your date range to analyze specific time periods
- **Grid Filters**: Use grid's built-in filters for detailed data exploration
- **Chart Types**:
  - Use **Bar/Line** for trends and comparisons
  - Use **Pie/Doughnut** for proportions
  - Use **Radar** for multivariate data
- **Aggregations**:
  - **Sum** for totals
  - **Average** for means
  - **Max/Min** for extremes
  - **Count** for frequencies

## Troubleshooting

**Issue**: "Failed to load data"
**Solution**: Make sure `data.xlsx` exists and has valid data

**Issue**: Charts not showing
**Solution**: Ensure you've selected both X and Y columns and clicked "Generate Chart"

**Issue**: Date filter not working
**Solution**: Ensure your Excel file has a column named "Date" with valid dates

## License

MIT License
