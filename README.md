# Excel Data Analyzer - React + Flask

A modern, full-stack web application for analyzing Excel data with interactive tables and dynamic charts. Built with **React** frontend and **Flask** API backend.

## 🎯 Architecture

```
┌─────────────────────┐         ┌──────────────────────┐
│   React Frontend    │  HTTP   │    Flask Backend     │
│   (Port 3000)       │ ◄─────► │    (Port 5000)       │
│                     │  API    │                      │
│ - Login UI          │         │ - Authentication     │
│ - Dashboard         │         │ - Data Processing    │
│ - AG Grid Table     │         │ - Excel Reading      │
│ - Chart.js Charts   │         │ - API Endpoints      │
└─────────────────────┘         └──────────────────────┘
```

**Benefits of This Architecture:**
- ✅ Modern SPA (Single Page Application)
- ✅ Better performance and UX
- ✅ Easy to scale frontend and backend independently
- ✅ Can deploy frontend to CDN
- ✅ Reusable API for mobile apps later

---

## ✨ Features

### 🔐 Authentication
- Session-based login/logout
- Password hashing (SHA256)
- Protected routes
- Automatic session timeout (1 hour)

### 📊 Data Visualization
- **5+ Slicers**: Filter by unique column values
- **AG Grid Table**: Sortable, filterable, paginated
- **7 Chart Types**: Bar, Line, Pie, Scatter, Doughnut, Area, Horizontal Bar
- **Aggregations**: Sum, Average, Count, Min, Max
- **Skip Null/Zero Values**: Clean chart data automatically

### 🎨 Modern UI
- React with hooks
- Responsive design
- Purple gradient theme
- Smooth animations
- Professional layout

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js 16+** and npm
- **2GB RAM** minimum

### 1. Backend Setup (Flask API)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run Flask backend on port 5000
python app.py
```

Backend runs at: **http://localhost:5000**

### 2. Frontend Setup (React)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies (first time only)
npm install

# Run development server
npm run dev
```

Frontend runs at: **http://localhost:3000**

### 3. Open Application

Go to: **http://localhost:3000**

**Login with:**
- Admin: `admin` / `admin123`
- User: `user1` / `user123`

---

## 📁 Project Structure

```
Data-Playgroup/
├── app.py                      # Flask API backend
├── requirements.txt            # Python dependencies
├── data.xlsx                   # Your Excel data
├── gunicorn_config.py          # Production config
├── .env.example                # Environment template
│
├── frontend/                   # React frontend
│   ├── package.json            # Node dependencies
│   ├── vite.config.js          # Vite configuration
│   ├── index.html              # HTML entry point
│   │
│   └── src/
│       ├── main.jsx            # React entry point
│       ├── App.jsx             # Main App component
│       ├── components/
│       │   ├── Login.jsx       # Login page
│       │   └── Dashboard.jsx   # Main dashboard
│       ├── services/
│       │   └── api.js          # API client (axios)
│       └── styles/
│           ├── Login.css
│           └── Dashboard.css
│
├── DEPLOYMENT.md               # Production deployment guide
└── SECURITY.md                 # Security analysis
```

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/login        Login user
POST   /api/logout       Logout user
GET    /api/session      Check if logged in
```

### Data
```
GET    /api/columns            Get all column names
POST   /api/data               Get filtered data
POST   /api/unique-values      Get unique values for slicers
```

### Example API Call

```javascript
// Login
const response = await fetch('http://localhost:5000/api/login', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
});
```

---

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload
python app.py

# Check logs
tail -f logs/error.log

# Test API endpoint
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Frontend Development

```bash
cd frontend

# Start dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Making Changes

**Adding a new React component:**
```javascript
// frontend/src/components/NewComponent.jsx
import React from 'react';

const NewComponent = () => {
  return <div>Hello!</div>;
};

export default NewComponent;
```

**Adding a new API endpoint:**
```python
# app.py
@app.route("/api/new-endpoint", methods=["POST"])
@login_required
def new_endpoint():
    data = request.get_json()
    return jsonify({'result': 'success'})
```

---

## 📦 Production Deployment

### Option 1: Same Server (Recommended for small teams)

```bash
# 1. Build React frontend
cd frontend
npm run build

# 2. Serve React build with Flask
# (Modify app.py to serve static files)

# 3. Run with Gunicorn
gunicorn -c gunicorn_config.py app:app
```

### Option 2: Separate Servers (Recommended for 200+ users)

**Frontend (Nginx/CDN):**
```bash
cd frontend
npm run build
# Deploy dist/ folder to nginx or CDN
```

**Backend (Private server):**
```bash
# Run Flask API
gunicorn -c gunicorn_config.py app:app

# Update CORS settings in app.py
CORS(app, origins=['https://your-frontend-domain.com'])
```

See **DEPLOYMENT.md** for complete production guide.

---

## 🔒 Security Features

✅ **Authentication**: Session-based with secure cookies
✅ **Password Hashing**: Werkzeug SHA256
✅ **CORS Protection**: Configured for specific origins
✅ **XSS Protection**: React auto-escapes all content
✅ **CSRF Protection**: SameSite cookies
✅ **Input Validation**: All API inputs validated
✅ **No SQL Injection**: No database (uses pandas)
✅ **Secure Sessions**: HTTPOnly cookies, 1-hour timeout

**Security Rating: A-** (A+ with HTTPS)

See **SECURITY.md** for full security audit.

---

## 🎓 Technology Stack

### Frontend
- **React 18** - UI library
- **Vite** - Build tool (faster than Webpack!)
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **AG Grid React** - Data table
- **Chart.js** - Charts
- **React-Chartjs-2** - React wrapper for Chart.js

### Backend
- **Flask 3.0** - API framework
- **pandas** - Data processing
- **openpyxl** - Excel reading
- **flask-cors** - CORS support
- **Gunicorn** - Production server

---

## 📖 How to Use

### Step 1: Login
1. Open http://localhost:3000
2. Enter username and password
3. Click "Login"

### Step 2: Select Columns
1. Check columns you want to see
2. Click "Load Selected Columns"

### Step 3: Use Slicers (Filter Data)
1. Click "Initialize Slicers"
2. Select values in each slicer
3. Click "Apply Filters"

### Step 4: View Data
- Data table shows filtered results
- Sort by clicking column headers
- Search using filters

### Step 5: Create Charts
1. Choose chart type (Bar, Line, etc.)
2. Select X and Y axis columns
3. Choose aggregation method
4. Toggle "Skip Null & Zero Values"
5. Click "Generate Chart"

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
SECRET_KEY=your-secret-key-here
DATA_FILE=data.xlsx
FLASK_ENV=production
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Frontend Configuration

Edit `frontend/vite.config.js`:
```javascript
export default defineConfig({
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:5000'  // Change backend URL
    }
  }
})
```

### CORS Configuration

Edit `app.py`:
```python
CORS(app, origins=[
  'http://localhost:3000',      # Development
  'https://your-domain.com'     # Production
])
```

---

## 🐛 Troubleshooting

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend API errors

```bash
# Check if Flask is running
curl http://localhost:5000/api/session

# Check logs
tail -f logs/error.log

# Restart backend
pkill -f "python app.py"
python app.py
```

### CORS errors

Make sure backend CORS settings include frontend URL:
```python
# app.py line 14
CORS(app, supports_credentials=True, origins=['http://localhost:3000'])
```

### Login not working

1. Check backend is running on port 5000
2. Check browser console for errors
3. Verify credentials in `app.py` lines 28-39
4. Clear browser cookies and try again

---

## 📊 Performance

### Current Capacity
- **200-300 concurrent users**: ✅ Easily with Gunicorn
- **500+ users**: ✅ With CDN for frontend
- **1000+ users**: ✅ With load balancer

### Optimization Tips

**Frontend:**
- Build with `npm run build` (minified, optimized)
- Deploy to CDN (Cloudflare, AWS CloudFront)
- Enable gzip compression

**Backend:**
- Use Gunicorn with multiple workers
- Add Redis for caching
- Use nginx reverse proxy

---

## 🆚 Why React Instead of Plain HTML?

| Feature | Plain HTML/JS | React |
|---------|---------------|-------|
| **Code Organization** | Mixed HTML/JS | Component-based ✅ |
| **State Management** | Manual DOM | React hooks ✅ |
| **Reusability** | Copy-paste | Reusable components ✅ |
| **Performance** | Full page reload | Virtual DOM ✅ |
| **Developer Experience** | Vanilla JS | Modern tools ✅ |
| **Scalability** | Hard to maintain | Easy to scale ✅ |
| **Testing** | Difficult | Easy with Jest ✅ |
| **Type Safety** | No | Can add TypeScript ✅ |

---

## 🚀 Next Steps

### Easy Enhancements
1. Add TypeScript for type safety
2. Add React Testing Library tests
3. Add more chart types
4. Add export to PDF/CSV
5. Add dark mode toggle

### Advanced Enhancements
1. WebSocket for real-time updates
2. Redis for session storage
3. PostgreSQL for user database
4. LDAP/Active Directory integration
5. Multi-file upload support
6. Scheduled data refresh

---

## 📝 License

This project is open source and free to use.

---

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

## 📞 Support

- Check **DEPLOYMENT.md** for production deployment
- Check **SECURITY.md** for security analysis
- Contact your IT department for organizational deployment

---

**Built with ❤️ using React and Flask**

**Enjoy your modern data analyzer!** 📊✨
