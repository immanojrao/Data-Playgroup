import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { AgGridReact } from 'ag-grid-react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';
import { Bar, Line, Pie, Scatter, Doughnut } from 'react-chartjs-2';
import { authAPI, dataAPI } from '../services/api';
import 'ag-grid-community/styles/ag-grid.css';
import 'ag-grid-community/styles/ag-theme-alpine.css';
import '../styles/Dashboard.css';

// Register Chart.js components
ChartJS.register(CategoryScale, LinearScale, BarElement, PointElement, LineElement, ArcElement, Title, Tooltip, Legend);

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const gridRef = useRef();

  // State
  const [columns, setColumns] = useState([]);
  const [selectedColumns, setSelectedColumns] = useState([]);
  const [rowData, setRowData] = useState([]);
  const [columnDefs, setColumnDefs] = useState([]);

  // Slicers
  const [slicers, setSlicers] = useState({});
  const [slicerSelections, setSlicerSelections] = useState({});

  // Chart
  const [chartType, setChartType] = useState('bar');
  const [xColumn, setXColumn] = useState('');
  const [yColumn, setYColumn] = useState('');
  const [aggregation, setAggregation] = useState('sum');
  const [groupData, setGroupData] = useState(true);
  const [skipNullZero, setSkipNullZero] = useState(true);
  const [chartData, setChartData] = useState(null);

  // Load columns on mount
  useEffect(() => {
    loadColumns();
  }, []);

  const loadColumns = async () => {
    try {
      const cols = await dataAPI.getColumns();
      setColumns(cols);
      setSelectedColumns(cols);
      loadData(cols);
    } catch (error) {
      console.error('Error loading columns:', error);
    }
  };

  const loadData = async (cols = selectedColumns) => {
    try {
      const result = await dataAPI.getData(cols);
      setRowData(result.data);

      const colDefs = result.columns.map(col => ({
        field: col,
        headerName: col,
        sortable: true,
        filter: true,
        resizable: true,
        floatingFilter: true,
      }));
      setColumnDefs(colDefs);

      if (result.columns.length > 0) {
        setXColumn(result.columns[0]);
        setYColumn(result.columns.length > 1 ? result.columns[1] : result.columns[0]);
      }
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleColumnToggle = (column) => {
    setSelectedColumns(prev =>
      prev.includes(column)
        ? prev.filter(c => c !== column)
        : [...prev, column]
    );
  };

  const selectAllColumns = () => setSelectedColumns(columns);
  const deselectAllColumns = () => setSelectedColumns([]);

  const initializeSlicers = async () => {
    try {
      const slicerColumns = selectedColumns.slice(0, Math.max(5, selectedColumns.length));
      const slicersData = {};

      for (const column of slicerColumns) {
        const result = await dataAPI.getUniqueValues(column);
        slicersData[column] = result.uniqueValues;
      }

      setSlicers(slicersData);
      setSlicerSelections({});
    } catch (error) {
      console.error('Error initializing slicers:', error);
    }
  };

  const handleSlicerChange = (column, value) => {
    setSlicerSelections(prev => {
      const current = prev[column] || [];
      const newSelection = current.includes(value)
        ? current.filter(v => v !== value)
        : [...current, value];

      return { ...prev, [column]: newSelection };
    });
  };

  const applySlicerFilters = () => {
    if (!gridRef.current) return;

    const api = gridRef.current.api;

    Object.keys(slicers).forEach(column => {
      const filterInstance = api.getColumnFilterInstance(column);
      const selectedValues = slicerSelections[column];

      if (selectedValues && selectedValues.length > 0) {
        filterInstance.setModel({
          filterType: 'set',
          values: selectedValues
        });
      } else {
        filterInstance.setModel(null);
      }
    });

    api.onFilterChanged();
  };

  const clearAllSlicers = () => {
    setSlicerSelections({});
    if (gridRef.current) {
      gridRef.current.api.setFilterModel(null);
    }
  };

  const generateChart = () => {
    if (!gridRef.current || !xColumn || !yColumn) return;

    const api = gridRef.current.api;
    const filteredData = [];

    api.forEachNodeAfterFilter(node => {
      filteredData.push(node.data);
    });

    if (filteredData.length === 0) {
      alert('No data available after filtering');
      return;
    }

    let xValues, yValues;

    if (groupData) {
      const aggregated = aggregateData(filteredData, xColumn, yColumn, aggregation, skipNullZero);
      xValues = aggregated.x;
      yValues = aggregated.y;
    } else {
      const processed = processData(filteredData, xColumn, yColumn, skipNullZero);
      xValues = processed.x;
      yValues = processed.y;
    }

    const data = {
      labels: xValues,
      datasets: [{
        label: yColumn,
        data: yValues,
        backgroundColor: getColors(xValues.length, 0.6),
        borderColor: getColors(xValues.length, 1),
        borderWidth: 2,
        tension: 0.4
      }]
    };

    const options = {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        title: {
          display: true,
          text: `${yColumn} by ${xColumn}`,
          font: { size: 18, weight: 'bold' }
        },
        legend: { display: true }
      },
      scales: ['bar', 'line', 'scatter'].includes(chartType) ? {
        y: {
          beginAtZero: true,
          title: { display: true, text: yColumn }
        },
        x: {
          title: { display: true, text: xColumn }
        }
      } : {}
    };

    setChartData({ data, options });
  };

  const processData = (data, xCol, yCol, skipNullZero) => {
    const xValues = [];
    const yValues = [];

    data.forEach(row => {
      const xVal = row[xCol];
      const yVal = parseFloat(row[yCol]);

      if (skipNullZero && (yVal === null || yVal === undefined || yVal === 0 || isNaN(yVal))) {
        return;
      }

      xValues.push(xVal);
      yValues.push(yVal);
    });

    return { x: xValues, y: yValues };
  };

  const aggregateData = (data, xCol, yCol, aggMethod, skipNullZero) => {
    const grouped = {};

    data.forEach(row => {
      const key = row[xCol];
      const yVal = parseFloat(row[yCol]);

      if (skipNullZero && (yVal === null || yVal === undefined || yVal === 0 || isNaN(yVal))) {
        return;
      }

      if (!grouped[key]) grouped[key] = [];
      if (!isNaN(yVal)) grouped[key].push(yVal);
    });

    const result = { x: [], y: [] };

    Object.keys(grouped).forEach(key => {
      if (grouped[key].length === 0) return;

      const aggregatedValue = applyAggregation(grouped[key], aggMethod);
      if (skipNullZero && aggregatedValue === 0) return;

      result.x.push(key);
      result.y.push(aggregatedValue);
    });

    return result;
  };

  const applyAggregation = (arr, method) => {
    if (arr.length === 0) return 0;

    switch(method) {
      case 'sum': return arr.reduce((a, b) => a + b, 0);
      case 'average': return arr.reduce((a, b) => a + b, 0) / arr.length;
      case 'count': return arr.length;
      case 'min': return Math.min(...arr);
      case 'max': return Math.max(...arr);
      default: return arr.reduce((a, b) => a + b, 0);
    }
  };

  const getColors = (count, alpha) => {
    const baseColors = [
      [102, 126, 234], [118, 75, 162], [255, 99, 132],
      [54, 162, 235], [255, 206, 86], [75, 192, 192],
      [153, 102, 255], [255, 159, 64], [199, 199, 199]
    ];

    return Array(count).fill(0).map((_, i) => {
      const color = baseColors[i % baseColors.length];
      return `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${alpha})`;
    });
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      onLogout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const renderChart = () => {
    if (!chartData) return null;

    const ChartComponent = {
      bar: Bar,
      line: Line,
      pie: Pie,
      scatter: Scatter,
      doughnut: Doughnut
    }[chartType] || Bar;

    return <ChartComponent data={chartData.data} options={chartData.options} />;
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1>📊 Excel Data Analyzer with React + Flask</h1>
          <p className="subtitle">Modern data visualization with React, AG Grid, and Chart.js</p>
        </div>
        <div className="user-info">
          <p>Welcome, <strong>{user?.name}</strong></p>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </div>

      {/* Step 1: Column Selection */}
      <div className="section">
        <div className="section-title">
          <span className="step-badge">1</span>
          Select Columns to Display
        </div>
        <div className="column-selector">
          {columns.map(column => (
            <label key={column} className="column-checkbox">
              <input
                type="checkbox"
                checked={selectedColumns.includes(column)}
                onChange={() => handleColumnToggle(column)}
              />
              <span>{column}</span>
            </label>
          ))}
        </div>
        <div className="button-group">
          <button onClick={() => loadData()}>Load Selected Columns</button>
          <button onClick={selectAllColumns} className="secondary">Select All</button>
          <button onClick={deselectAllColumns} className="secondary">Deselect All</button>
        </div>
      </div>

      {/* Step 1.5: Slicers */}
      <div className="section">
        <div className="section-title">
          <span className="step-badge">1.5</span>
          Advanced Filters (Slicers)
        </div>
        <div className="info-box">
          Select specific values from each column to filter your data.
        </div>
        <div className="button-group">
          <button onClick={initializeSlicers}>Initialize Slicers</button>
          <button onClick={applySlicerFilters} className="secondary">Apply Filters</button>
          <button onClick={clearAllSlicers} className="secondary">Clear All Filters</button>
        </div>
        <div className="slicers-container">
          {Object.keys(slicers).map(column => (
            <div key={column} className="slicer">
              <div className="slicer-title">{column}</div>
              <div className="slicer-options">
                {slicers[column].map(value => (
                  <div key={value} className="slicer-option">
                    <input
                      type="checkbox"
                      id={`slicer-${column}-${value}`}
                      checked={(slicerSelections[column] || []).includes(value)}
                      onChange={() => handleSlicerChange(column, value)}
                    />
                    <label htmlFor={`slicer-${column}-${value}`}>{value}</label>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Step 2: Data Grid */}
      <div className="section">
        <div className="section-title">
          <span className="step-badge">2</span>
          View and Filter Data
        </div>
        <div className="ag-theme-alpine" style={{ height: 500, width: '100%' }}>
          <AgGridReact
            ref={gridRef}
            rowData={rowData}
            columnDefs={columnDefs}
            defaultColDef={{
              sortable: true,
              filter: true,
              resizable: true,
              floatingFilter: true,
            }}
            pagination={true}
            paginationPageSize={20}
            rowSelection="multiple"
          />
        </div>
      </div>

      {/* Step 3: Chart */}
      <div className="section">
        <div className="section-title">
          <span className="step-badge">3</span>
          Create Dynamic Charts
        </div>
        <div className="info-box">
          Charts automatically skip null and zero values.
        </div>
        <div className="chart-controls">
          <div className="form-group">
            <label>Chart Type:</label>
            <select value={chartType} onChange={(e) => setChartType(e.target.value)}>
              <option value="bar">Bar Chart</option>
              <option value="line">Line Chart</option>
              <option value="pie">Pie Chart</option>
              <option value="scatter">Scatter Plot</option>
              <option value="doughnut">Doughnut Chart</option>
            </select>
          </div>
          <div className="form-group">
            <label>X-Axis Column:</label>
            <select value={xColumn} onChange={(e) => setXColumn(e.target.value)}>
              {selectedColumns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Y-Axis Column:</label>
            <select value={yColumn} onChange={(e) => setYColumn(e.target.value)}>
              {selectedColumns.map(col => <option key={col} value={col}>{col}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Aggregation:</label>
            <select value={aggregation} onChange={(e) => setAggregation(e.target.value)}>
              <option value="sum">Sum</option>
              <option value="average">Average</option>
              <option value="count">Count</option>
              <option value="min">Minimum</option>
              <option value="max">Maximum</option>
            </select>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" checked={groupData} onChange={(e) => setGroupData(e.target.checked)} />
              Group by X-Axis
            </label>
          </div>
          <div className="form-group">
            <label className="checkbox-label">
              <input type="checkbox" checked={skipNullZero} onChange={(e) => setSkipNullZero(e.target.checked)} />
              Skip Null & Zero Values
            </label>
          </div>
        </div>
        <button onClick={generateChart} style={{ marginBottom: 20 }}>Generate Chart</button>
        <div className="chart-wrapper">
          {renderChart()}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
