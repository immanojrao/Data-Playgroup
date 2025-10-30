# Excel Data Analyzer with Django + AG Grid

A powerful Django-based web application for analyzing Excel data with AG Grid tables, advanced filtering through slicers, and dynamic chart visualization.

## Features

### 1. **Column Selection**
- Select which columns to display in the data table
- Quick "Select All" and "Deselect All" options
- Real-time updates to the AG Grid table

### 2. **Advanced Filtering with Slicers (5+ Slicers)**
- Dynamic slicers generated from your Excel columns
- Each slicer shows unique values from the respective column
- Multiple selections within a slicer (OR logic)
- Easy "Apply Filters" and "Clear All Filters" buttons
- Integrates seamlessly with AG Grid filtering

### 3. **Interactive AG Grid Table**
- Sortable columns
- Built-in column filters
- Floating filters for quick filtering
- Pagination support (20 rows per page)
- Resizable columns

### 4. **Dynamic Chart Visualization**

#### Chart Types:
- Bar Chart
- Line Chart
- Pie Chart
- Scatter Plot
- Doughnut Chart
- Area Chart
- Horizontal Bar Chart

#### Chart Features:
- **Scrollable Charts**: When the number of x-axis values increases, the chart becomes horizontally scrollable instead of reducing bar width
- **Skip Null/Zero Values**: Automatically filters out null and zero values from charts (optional toggle)
- **Aggregation Methods**: Sum, Average, Count, Min, Max
- **Group by X-Axis**: Aggregate duplicate x-axis values
- **Zoom & Pan**: Mouse wheel zoom and pan support

### 5. **Responsive Design**
- Modern gradient UI with purple theme
- Step-by-step workflow with numbered badges
- Mobile-friendly responsive layout

## Project Structure

```
Data-Playgroup/
├── dashboard/                  # Django app
│   ├── views.py               # Backend views (Excel handling, API endpoints)
│   ├── urls.py                # URL routing for dashboard
│   └── templates/
│       └── dashboard/
│           └── index.html     # Main template with AG Grid & Chart.js
├── myproject/                 # Django project
│   ├── settings.py            # Django settings
│   ├── urls.py                # Main URL configuration
│   └── wsgi.py                # WSGI configuration
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── data.xlsx                  # Your Excel data file (place here)
└── README.md                  # This file
```

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies include:
- Django 5.0.0
- pandas 2.1.4
- openpyxl 3.1.2
- django-cors-headers 4.3.1
- gunicorn 21.2.0

### 2. Add Your Excel File

Place your Excel file in the root directory and name it `data.xlsx`, or update the file path in `dashboard/views.py`:

```python
# In dashboard/views.py, line 14
df = pd.read_excel(os.path.join(BASE_DIR, 'data.xlsx'))
```

**Note**: If no Excel file is found, the app will create a sample DataFrame with dummy data.

### 3. Run Migrations

```bash
python manage.py migrate
```

### 4. Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## Usage Guide

### Step 1: Select Columns to Display
1. Check/uncheck columns you want to display
2. Click "Load Selected Columns" to update the table
3. Use "Select All" or "Deselect All" for quick selection

### Step 2: Initialize and Use Slicers
1. Click "Initialize Slicers" to load unique values from your columns
2. Select specific values from each slicer to filter data
3. Click "Apply Filters" to filter the AG Grid table
4. Use "Clear All Filters" to reset

**Note**: At least 5 slicers will be created based on your selected columns.

### Step 3: View and Filter Data in AG Grid
- Use the column filters in the table header
- Sort columns by clicking headers
- The table automatically reflects slicer filters

### Step 4: Create Dynamic Charts
1. Select Chart Type from dropdown
2. Choose X-Axis Column (categorical data)
3. Choose Y-Axis Column (numerical data)
4. Select Aggregation Method (Sum, Average, etc.)
5. Toggle "Group by X-Axis" to aggregate duplicate values
6. Toggle "Skip Null & Zero Values" to clean your data
7. Click "Generate Chart"

**Chart Scrolling**: If you have many x-axis values (e.g., 50+ data points), the chart will automatically become horizontally scrollable to maintain readable bar widths.

## API Endpoints

### 1. `GET /`
Renders the main dashboard page with all columns.

### 2. `POST /get_data`
Returns data for selected columns.

**Request Body**:
```json
{
  "columns": ["Column1", "Column2", "Column3"]
}
```

**Response**:
```json
{
  "data": [{...}, {...}],
  "columns": ["Column1", "Column2", "Column3"]
}
```

### 3. `POST /get_unique_values`
Returns unique values for a specific column (used by slicers).

**Request Body**:
```json
{
  "column": "Department"
}
```

**Response**:
```json
{
  "column": "Department",
  "uniqueValues": ["IT", "HR", "Sales"]
}
```

## Key Implementation Details

### Skip Null/Zero Values Logic
The application filters data in two stages:

1. **Before Aggregation** (dashboard/templates/dashboard/index.html:728-731):
```javascript
// Skip null/zero values if option is enabled (before aggregation)
if (skipNullZero && (yVal === null || yVal === undefined || yVal === 0 || isNaN(yVal))) {
    return;
}
```

2. **After Aggregation** (dashboard/templates/dashboard/index.html:753-756):
```javascript
// Skip if aggregated value is zero (when skipNullZero is enabled)
if (skipNullZero && aggregatedValue === 0) {
    return;
}
```

### Scrollable Chart Implementation
Charts dynamically calculate width based on data points (dashboard/templates/dashboard/index.html:677-690):

```javascript
// Calculate dynamic width for scrollable chart
const minBarWidth = 40; // minimum width per bar in pixels
const calculatedWidth = Math.max(800, xValues.length * minBarWidth);

if (chartType === 'bar' || chartType === 'horizontalBar') {
    chartContainer.style.width = calculatedWidth + 'px';
    canvas.width = calculatedWidth;
}
```

### Slicer Integration with AG Grid
Slicers use AG Grid's native filter API (dashboard/templates/dashboard/index.html:585-598):

```javascript
// Apply filters to AG Grid
Object.keys(slicersData).forEach(column => {
    const filterInstance = gridApi.getColumnFilterInstance(column);

    if (filtersByColumn[column] && filtersByColumn[column].length > 0) {
        filterInstance.setModel({
            filterType: 'set',
            values: filtersByColumn[column]
        });
    } else {
        filterInstance.setModel(null);
    }
});
```

## Technologies Used

- **Backend**: Django 5.0
- **Data Processing**: pandas, openpyxl
- **Frontend Table**: AG Grid Community 31.0.0
- **Charts**: Chart.js 4.4.0 with Zoom Plugin
- **Styling**: Custom CSS with gradient themes

## Customization

### Change Excel File Path
Edit `dashboard/views.py` line 14:
```python
df = pd.read_excel(os.path.join(BASE_DIR, 'your-file.xlsx'))
```

### Adjust Number of Slicers
Edit `dashboard/templates/dashboard/index.html` line 499:
```javascript
const columnsForSlicers = selectedColumns.slice(0, 10); // Change 10 to your desired number
```

### Modify Chart Bar Width
Edit `dashboard/templates/dashboard/index.html` line 677:
```javascript
const minBarWidth = 40; // Change to adjust minimum bar width
```

## Production Deployment

For production deployment with Gunicorn:

```bash
gunicorn myproject.wsgi:application --bind 0.0.0.0:8000
```

Remember to:
1. Set `DEBUG = False` in `myproject/settings.py`
2. Configure `ALLOWED_HOSTS` appropriately
3. Set up static files serving
4. Use a proper database (PostgreSQL, MySQL) instead of SQLite

## License

This project is open source and available under the MIT License.

## Support

For issues or questions, please open an issue on the project repository.
