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
- **Frontend**: HTML5, Bootstrap 5.1.3, Jinja2 templates
- **Icons**: Font Awesome 6.0.0
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
git clone https://github.com/raaaemmm/fruit-store.git
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
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or use your preferred editor
```

### 5. Configure MongoDB
Make sure MongoDB is running and update your `.env` file with the correct MongoDB connection string.

### 6. Run the Application
```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 7. Access the Application
Open your browser and navigate to: `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

The application uses environment variables for configuration. Copy `.env.example` to `.env` and configure:

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

# Security (for future authentication features)
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO

# Template and Static Directories
TEMPLATE_DIR=templates
STATIC_DIR=static
```

### MongoDB Setup

#### Local MongoDB
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB service
sudo systemctl start mongodb
```

#### MongoDB Atlas (Cloud)
1. Create account at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster
3. Get connection string
4. Update `MONGODB_URL` in `.env`

## 📖 API Documentation

Once the application is running, you can access:

- **Interactive API Documentation**: `http://localhost:8000/docs`
- **Alternative API Documentation**: `http://localhost:8000/redoc`
- **Health Check Endpoint**: `http://localhost:8000/health`
- **Statistics API**: `http://localhost:8000/api/stats`

### Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard homepage |
| `/customers` | GET | List all customers |
| `/customers/create` | GET/POST | Create customer form/action |
| `/fruits` | GET | List all fruits |
| `/fruits/create` | GET/POST | Create fruit form/action |
| `/suppliers` | GET | List all suppliers |
| `/orders` | GET | List all orders |
| `/api/stats` | GET | Get dashboard statistics |
| `/health` | GET | Application health check |

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
  "status": String
}
```

## 🎨 User Interface

The application features a modern, responsive design with:

- **Navigation Bar**: Easy access to all sections
- **Dashboard**: Real-time statistics and quick actions
- **Data Tables**: Sortable and searchable data display
- **Forms**: Intuitive forms with validation
- **Status Indicators**: Color-coded status badges
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🔧 Development

### Project Structure
```
fruit-store/
├── main.py                 # Main application file
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── templates/            # HTML templates
    ├── base.html         # Base template
    ├── index.html        # Dashboard
    ├── customers/        # Customer templates
    ├── fruits/           # Fruit templates
    ├── suppliers/        # Supplier templates
    └── orders/           # Order templates
```

### Adding New Features

1. **Create new routes** in `main.py`
2. **Add HTML templates** in appropriate folders
3. **Update navigation** in `base.html`
4. **Add database models** as needed
5. **Update API documentation**

### Code Style

- Follow PEP 8 for Python code
- Use async/await for database operations
- Implement proper error handling
- Add appropriate logging
- Write descriptive commit messages

## 🚀 Deployment

### Production Deployment

#### Using Docker (Recommended)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Environment Variables for Production
```env
DEBUG=false
APP_RELOAD=false
MONGODB_URL=mongodb://your-production-mongodb-url
SECRET_KEY=your-production-secret-key
```

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Test Coverage
Tests should cover:
- API endpoints
- Database operations
- Form validation
- Error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation as needed
- Follow the existing code style
- Test your changes thoroughly

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

If you encounter any issues or have questions:

1. Check the [GitHub Issues](https://github.com/raaaemmm/fruit-store/issues)
2. Create a new issue with detailed description
3. Provide error logs and environment details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Styled with [Bootstrap](https://getbootstrap.com/)
- Icons by [Font Awesome](https://fontawesome.com/)
- Database powered by [MongoDB](https://www.mongodb.com/)

---

## 📈 Roadmap

Future enhancements planned:

- [ ] User authentication and authorization
- [ ] Advanced reporting and analytics
- [ ] Email notifications for orders
- [ ] Barcode scanning functionality
- [ ] Multi-store support
- [ ] Mobile application
- [ ] Export/import functionality
- [ ] Advanced inventory management

---

**Made with ❤️ by [raaaemmm with Claude AI](https://github.com/raaaemmm)**