# Excel Data Analyzer with Flask + AG Grid

A simple and powerful Flask web application for analyzing Excel data with interactive tables and dynamic charts.

## ✨ Key Features

### 📊 **5+ Data Slicers**
Filter your data with multiple slicers showing unique values from each column. Select specific values to instantly filter the data table.

### 📈 **Scrollable Charts**
When you have many data points, charts automatically become horizontally scrollable instead of squishing the bars together - keeping everything readable!

### 🎯 **Skip Null & Zero Values**
Automatically remove null and zero values from your charts to reduce clutter and focus on meaningful data.

### 📋 **Other Features**
- Select which columns to display
- Interactive AG Grid table with sorting and filtering
- 7 chart types: Bar, Line, Pie, Scatter, Doughnut, Area, Horizontal Bar
- Data aggregation: Sum, Average, Count, Min, Max
- Beautiful modern UI with purple gradient theme

---

## 🚀 Quick Start (3 Simple Steps!)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python app.py
```

### Step 3: Open Your Browser
Go to: **http://127.0.0.1:5000/**

That's it! 🎉

---

## 📁 Simple Project Structure

```
Data-Playgroup/
├── app.py                 # Main Flask application (all backend code here!)
├── templates/
│   └── index.html        # Single HTML file (all frontend code here!)
├── requirements.txt      # Python dependencies
├── data.xlsx            # Your Excel file (optional - sample data loads if missing)
└── README.md            # This file
```

**Just 2 files to understand:**
1. **app.py** - All Python/backend code (only 103 lines!)
2. **templates/index.html** - All HTML/CSS/JavaScript (complete UI)

---

## 📖 How to Use

### 1️⃣ Select Columns
- Check the columns you want to see
- Click "Load Selected Columns"

### 2️⃣ Use Slicers to Filter Data
- Click "Initialize Slicers"
- Check boxes in each slicer to filter by specific values
- Click "Apply Filters" to update the table

### 3️⃣ View Your Data
- The AG Grid table shows your filtered data
- Sort columns by clicking headers
- Use the search boxes to filter further

### 4️⃣ Create Charts
- Choose chart type
- Select X-axis and Y-axis columns
- Pick aggregation method (Sum, Average, etc.)
- Toggle "Skip Null & Zero Values" ON to clean your chart
- Click "Generate Chart"

**Pro Tip:** If your chart has many bars, it will automatically become scrollable so you can scroll left/right to see all your data!

---

## 🔧 Customization

### Use Your Own Excel File
Just place your Excel file in the project folder and name it `data.xlsx`

Or update line 10 in `app.py`:
```python
df = pd.read_excel("your-file.xlsx")
```

### Change Number of Slicers
Edit line 499 in `templates/index.html`:
```javascript
const columnsForSlicers = selectedColumns.slice(0, 10); // Change 10 to any number
```

### Adjust Chart Scroll Width
Edit line 677 in `templates/index.html`:
```javascript
const minBarWidth = 40; // Change to make bars wider or narrower
```

---

## 🎨 All Chart Features

### Chart Types
- **Bar Chart** - Great for comparing categories
- **Line Chart** - Perfect for trends over time
- **Pie Chart** - Show proportions
- **Scatter Plot** - Find correlations
- **Doughnut** - Like pie but fancier
- **Area Chart** - Filled line chart
- **Horizontal Bar** - Bars go sideways

### Chart Options
- **Aggregation**: Sum, Average, Count, Min, Max
- **Group by X-Axis**: Combine duplicate values
- **Skip Null & Zero**: Remove empty/zero data points
- **Zoom & Pan**: Mouse wheel to zoom, drag to pan

---

## 📊 Sample Data

If you don't have an Excel file, the app automatically creates sample data with:
- **8 employees** with different attributes
- **6 columns**: Name, Age, Department, Salary, Experience, City
- Perfect for testing all features!

---

## 🔌 API Endpoints

The app has 4 simple endpoints:

1. **GET /** - Main page
2. **POST /get_data** - Get selected columns
3. **POST /get_unique_values** - Get unique values for slicers
4. **POST /get_chart_data** - Get chart data (legacy, not actively used)

---

## 💻 Technologies Used

- **Backend**: Flask 3.0 (Python micro-framework)
- **Data**: pandas, openpyxl (Excel reading)
- **Table**: AG Grid Community 31.0
- **Charts**: Chart.js 4.4 with Zoom Plugin
- **Styling**: Pure CSS (no frameworks!)

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "data.xlsx not found"
No problem! The app creates sample data automatically.

### Charts not showing
Make sure you:
1. Selected columns and loaded data
2. Chose both X and Y axis columns
3. Have some data after filtering

### Port already in use
Change the port in `app.py` line 103:
```python
app.run(debug=True, port=5001)  # Use different port
```

---

## 🎓 Learning Flask?

This project is a great learning resource! Here's what you can learn:

- **app.py** teaches you:
  - Flask routing (`@app.route`)
  - Handling POST requests
  - Working with pandas DataFrames
  - Returning JSON responses

- **templates/index.html** teaches you:
  - AG Grid integration
  - Chart.js usage
  - Async JavaScript (fetch API)
  - DOM manipulation

---

## 📝 License

This project is open source and free to use!

## 🤝 Contributing

Feel free to:
- Add new chart types
- Improve the UI
- Add more aggregation methods
- Create more complex filters

---

## 🙏 Credits

Built with:
- [Flask](https://flask.palletsprojects.com/)
- [pandas](https://pandas.pydata.org/)
- [AG Grid](https://www.ag-grid.com/)
- [Chart.js](https://www.chartjs.org/)

---

**Enjoy analyzing your data! 📊✨**
