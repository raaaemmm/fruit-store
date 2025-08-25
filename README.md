# 🍎 Fruit Store Management System

A comprehensive web-based management system for fruit stores built with FastAPI, MongoDB, and modern web technologies. This system provides complete CRUD operations for managing customers, fruits inventory, suppliers, and orders with real-time statistics and responsive design.

## 🌟 Features

### Core Functionality
- **Customer Management**: Track customer information, membership status, and contact details
- **Fruit Inventory**: Manage fruit stock, pricing, categories, and organic certification
- **Supplier Management**: Maintain supplier relationships and track fruit supply chains
- **Order Processing**: Create, track, and manage customer orders with status updates
- **Real-time Statistics**: Live dashboard with key performance metrics

### Technical Features
- **Responsive Design**: Bootstrap-powered UI that works on all devices
- **Real-time Updates**: Live statistics and data synchronization
- **RESTful API**: Clean API endpoints for all operations
- **Database Integration**: MongoDB with Motor async driver
- **Form Validation**: Client and server-side validation
- **Error Handling**: Comprehensive error handling and user feedback

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Database**: MongoDB with Motor (async driver)
- **Frontend**: HTML5, Bootstrap 5, Jinja2 templates
- **Icons**: Font Awesome
- **Server**: Uvicorn ASGI server
- **Environment**: Python-dotenv for configuration

## 📋 Prerequisites

Before running this application, ensure you have:

- Python 3.8 or higher
- MongoDB (local installation or MongoDB Atlas)
- Git (for cloning the repository)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/fruit-store.git
cd fruit-store
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=fruit_store

# FastAPI Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=true

# Application Settings
APP_TITLE=Fruit Store Management
APP_VERSION=1.0.0
DEBUG=true

# Template and Static Directories
TEMPLATE_DIR=templates
STATIC_DIR=static
```

### 5. Configure MongoDB
Make sure MongoDB is running and accessible at the URL specified in your `.env` file.

### 6. Run the Application
```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Access the Application
Open your browser and navigate to: `http://localhost:8000`

## ⚙️ Project Structure

```
fruit-store/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create from template)
├── README.md                  # Project documentation
├── database/
│   └── connection.py          # Database connection configuration
├── models/                    # Pydantic models
│   ├── customer.py           # Customer data models
│   ├── fruit.py              # Fruit data models
│   ├── order.py              # Order data models
│   └── supplier.py           # Supplier data models
├── routes/                    # Route handlers
│   ├── api_routes.py         # REST API endpoints
│   └── web_routes.py         # Web interface routes
├── utils/
│   └── helpers.py            # Utility functions
└── templates/                # HTML templates (Jinja2)
    ├── base.html             # Base template
    ├── index.html            # Dashboard
    ├── customers/            # Customer templates
    ├── fruits/               # Fruit templates
    ├── suppliers/            # Supplier templates
    └── orders/               # Order templates
```

## 📖 API Documentation

Once the application is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **Health Check Endpoint**: `http://localhost:8000/health`
- **Statistics API**: `http://localhost:8000/api/stats`

### Key API Endpoints

#### Web Routes
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard homepage |
| `/customers` | GET | List all customers |
| `/customers/create` | GET/POST | Create customer form/action |
| `/fruits` | GET | List all fruits |
| `/suppliers` | GET | List all suppliers |
| `/orders` | GET | List all orders |

#### API Routes
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stats` | GET | Get dashboard statistics |
| `/api/customers` | GET/POST | List/Create customers |
| `/api/customers/{id}` | GET/PUT/DELETE | Customer operations |
| `/api/fruits` | GET/POST | List/Create fruits |
| `/api/suppliers` | GET/POST | List/Create suppliers |
| `/api/orders` | GET/POST | List/Create orders |

## 🗄️ Database Schema

### Collections

#### Customers
```javascript
{
  "_id": ObjectId,
  "customerId": String,
  "name": String,
  "phone": String,
  "address": String,
  "isMember": Boolean,
  "updated_at": DateTime
}
```

#### Fruits
```javascript
{
  "_id": ObjectId,
  "barCode": String,
  "name": String,
  "category": String,
  "pricePerKg": Number,
  "stockKg": Number,
  "country": String,
  "supplierId": ObjectId,
  "isOrganic": Boolean
}
```

#### Suppliers
```javascript
{
  "_id": ObjectId,
  "name": String,
  "phone": String,
  "location": String,
  "fruitsSupplied": [String],
  "active": Boolean
}
```

#### Orders
```javascript
{
  "_id": ObjectId,
  "orderDate": DateTime,
  "customerId": String,
  "items": [{
    "fruitId": ObjectId,
    "quantityKg": Number
  }],
  "totalAmount": Number,
  "status": String,
  "updated_at": DateTime
}
```

## 🎨 User Interface

The application features a modern, responsive design with:

- **Navigation Bar**: Easy access to all sections
- **Dashboard**: Real-time statistics and quick actions
- **Data Tables**: Clean display of all entities
- **Forms**: Intuitive forms with validation
- **Status Indicators**: Color-coded status badges
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🧪 Development

### Adding New Features

1. **Create new models** in the `models/` directory
2. **Add routes** in `routes/api_routes.py` or `routes/web_routes.py`
3. **Create templates** in the appropriate `templates/` subdirectory
4. **Update navigation** in `templates/base.html`
5. **Test your changes**

### Code Style

- Follow PEP 8 for Python code
- Use async/await for database operations
- Implement proper error handling
- Add appropriate logging
- Write descriptive commit messages

## 🚀 Deployment

### Production Environment Variables
```env
DEBUG=false
APP_RELOAD=false
MONGODB_URL=mongodb://your-production-mongodb-url
```

### Using Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📞 Support

If you encounter any issues:

1. Check the application logs
2. Verify MongoDB connection
3. Ensure all environment variables are set correctly
4. Create an issue with detailed error information

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Styled with [Bootstrap](https://getbootstrap.com/)
- Database powered by [MongoDB](https://www.mongodb.com/)

---

**Happy fruit store management! 🍓🥝🍊**