# 🍎 Fruit Store Management System - API Routes Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (future enhancement planned)

---

## 🏠 System Routes

### Health Check
```http
GET /health
```
**Description**: Check application and database health status

**Response Example**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-25T10:30:00.000Z",
  "app": "Fruit Store",
  "version": "1.0.0",
  "database": "connected"
}
```

---

## 📊 Dashboard Statistics

### Get Dashboard Stats
```http
GET /api/stats
```
**Description**: Get comprehensive dashboard statistics

**Response Example**:
```json
{
  "success": true,
  "data": {
    "customers_count": 25,
    "fruits_count": 40,
    "suppliers_count": 8,
    "orders_count": 15,
    "total_suppliers": 10,
    "pending_orders": 5,
    "organic_fruits": 12,
    "members_count": 18
  }
}
```

---

## 👥 Customer API Routes

### Get All Customers
```http
GET /api/customers?skip=0&limit=100&is_member=true
```
**Query Parameters**:
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Number of records to return (default: 100, max: 1000)
- `is_member` (boolean, optional): Filter by membership status

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "64f1234567890abcdef12345",
      "customerId": "CUST001",
      "name": "John Doe",
      "phone": "+1234567890",
      "address": "123 Main St, City",
      "isMember": true,
      "updated_at": "2025-01-15"
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 25,
    "has_more": false
  }
}
```

### Get Single Customer
```http
GET /api/customers/{customer_id}
```
**Path Parameters**:
- `customer_id` (string): MongoDB ObjectId of the customer

**Response Example**:
```json
{
  "success": true,
  "data": {
    "_id": "64f1234567890abcdef12345",
    "customerId": "CUST001",
    "name": "John Doe",
    "phone": "+1234567890",
    "address": "123 Main St, City",
    "isMember": true,
    "updated_at": "2025-01-15"
  }
}
```

### Create Customer
```http
POST /api/customers
```
**Request Body**:
```json
{
  "customerId": "CUST002",
  "name": "Jane Smith",
  "phone": "+0987654321",
  "address": "456 Oak Ave, City",
  "isMember": false
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Customer created successfully",
  "customer_id": "64f1234567890abcdef12346"
}
```

### Update Customer
```http
PUT /api/customers/{customer_id}
```
**Request Body** (all fields optional):
```json
{
  "name": "Jane Smith Updated",
  "phone": "+0987654321",
  "address": "789 Pine St, City",
  "isMember": true
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Customer updated successfully"
}
```

### Delete Customer
```http
DELETE /api/customers/{customer_id}
```
**Response Example**:
```json
{
  "success": true,
  "message": "Customer deleted successfully"
}
```

---

## 🍊 Fruits API Routes

### Get All Fruits
```http
GET /api/fruits?skip=0&limit=100&category=citrus&is_organic=true&min_stock=10
```
**Query Parameters**:
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Number of records to return
- `category` (string, optional): Filter by fruit category
- `is_organic` (boolean, optional): Filter by organic status
- `min_stock` (int, optional): Minimum stock quantity filter

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "64f1234567890abcdef12347",
      "barCode": "123456789012",
      "name": "Organic Orange",
      "category": "Citrus",
      "pricePerKg": 4.99,
      "stockKg": 50,
      "country": "Spain",
      "supplierId": "64f1234567890abcdef12340",
      "supplierName": "Fresh Citrus Co.",
      "isOrganic": true
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 40,
    "has_more": false
  }
}
```

### Get Single Fruit
```http
GET /api/fruits/{fruit_id}
```
**Response Example**:
```json
{
  "success": true,
  "data": {
    "_id": "64f1234567890abcdef12347",
    "barCode": "123456789012",
    "name": "Organic Orange",
    "category": "Citrus",
    "pricePerKg": 4.99,
    "stockKg": 50,
    "country": "Spain",
    "supplierId": "64f1234567890abcdef12340",
    "supplierName": "Fresh Citrus Co.",
    "isOrganic": true
  }
}
```

### Create Fruit
```http
POST /api/fruits
```
**Request Body**:
```json
{
  "barCode": "123456789013",
  "name": "Fresh Apple",
  "category": "Pome",
  "pricePerKg": 3.99,
  "stockKg": 75,
  "country": "USA",
  "supplierId": "64f1234567890abcdef12340",
  "isOrganic": false
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Fruit created successfully",
  "fruit_id": "64f1234567890abcdef12348"
}
```

### Update Fruit
```http
PUT /api/fruits/{fruit_id}
```
**Request Body** (all fields optional):
```json
{
  "pricePerKg": 4.49,
  "stockKg": 80,
  "isOrganic": true
}
```

### Delete Fruit
```http
DELETE /api/fruits/{fruit_id}
```

---

## 🏪 Suppliers API Routes

### Get All Suppliers
```http
GET /api/suppliers?skip=0&limit=100&active_only=true
```
**Query Parameters**:
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Number of records to return
- `active_only` (boolean, optional): Filter only active suppliers

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "64f1234567890abcdef12340",
      "name": "Fresh Citrus Co.",
      "phone": "+1122334455",
      "location": "California, USA",
      "fruitsSupplied": ["Orange", "Lemon", "Grapefruit"],
      "active": true
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 8,
    "has_more": false
  }
}
```

### Get Single Supplier
```http
GET /api/suppliers/{supplier_id}
```

### Create Supplier
```http
POST /api/suppliers
```
**Request Body**:
```json
{
  "name": "Tropical Fruits Ltd.",
  "phone": "+1555666777",
  "location": "Florida, USA",
  "fruitsSupplied": ["Mango", "Pineapple", "Papaya"],
  "active": true
}
```

### Update Supplier
```http
PUT /api/suppliers/{supplier_id}
```
**Request Body** (all fields optional):
```json
{
  "phone": "+1555666888",
  "active": false
}
```

### Delete Supplier
```http
DELETE /api/suppliers/{supplier_id}
```

---

## 📦 Orders API Routes

### Get All Orders
```http
GET /api/orders?skip=0&limit=100&status=Pending&customer_id=CUST001
```
**Query Parameters**:
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Number of records to return
- `status` (string, optional): Filter by order status
- `customer_id` (string, optional): Filter by customer ID

**Response Example**:
```json
{
  "success": true,
  "data": [
    {
      "_id": "64f1234567890abcdef12349",
      "orderDate": "2025-01-15",
      "customerId": "CUST001",
      "customerName": "John Doe",
      "items": [
        {
          "fruitId": "64f1234567890abcdef12347",
          "fruitName": "Organic Orange",
          "fruitPrice": 4.99,
          "quantityKg": 2.5
        }
      ],
      "totalAmount": 12.48,
      "status": "Pending"
    }
  ],
  "pagination": {
    "skip": 0,
    "limit": 100,
    "total": 15,
    "has_more": false
  }
}
```

### Get Single Order
```http
GET /api/orders/{order_id}
```

### Create Order
```http
POST /api/orders
```
**Request Body**:
```json
{
  "customerId": "CUST001",
  "items": [
    {
      "fruitId": "64f1234567890abcdef12347",
      "quantityKg": 2.5
    },
    {
      "fruitId": "64f1234567890abcdef12348",
      "quantityKg": 1.0
    }
  ],
  "status": "Pending"
}
```

**Response Example**:
```json
{
  "success": true,
  "message": "Order created successfully",
  "order_id": "64f1234567890abcdef12349",
  "total_amount": 16.47
}
```

### Update Order
```http
PUT /api/orders/{order_id}
```
**Request Body**:
```json
{
  "status": "Completed"
}
```

### Delete Order
```http
DELETE /api/orders/{order_id}
```

---

## 🌐 Web Interface Routes

### Dashboard & Pages
```http
GET /                          # Dashboard homepage
GET /customers                 # Customers list page
GET /customers/create          # Create customer form
GET /customers/{id}/edit       # Edit customer form
POST /customers/create         # Submit new customer
POST /customers/{id}/edit      # Update customer
POST /customers/{id}/delete    # Delete customer

GET /fruits                    # Fruits list page
GET /fruits/create            # Create fruit form
GET /fruits/{id}/edit         # Edit fruit form
POST /fruits/create           # Submit new fruit
POST /fruits/{id}/edit        # Update fruit
POST /fruits/{id}/delete      # Delete fruit

GET /suppliers                # Suppliers list page
GET /suppliers/create         # Create supplier form
GET /suppliers/{id}/edit      # Edit supplier form
POST /suppliers/create        # Submit new supplier
POST /suppliers/{id}/edit     # Update supplier
POST /suppliers/{id}/delete   # Delete supplier

GET /orders                   # Orders list page
GET /orders/create           # Create order form
GET /orders/{id}/edit        # Edit order form
POST /orders/create          # Submit new order
POST /orders/{id}/edit       # Update order
POST /orders/{id}/delete     # Delete order
```

---

## 📋 Error Responses

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error description"
}
```

### Common HTTP Status Codes
- `200`: Success
- `404`: Resource not found
- `400`: Bad request (validation error)
- `500`: Internal server error

---

## 🔧 Usage Examples

### Using cURL

#### Get all customers
```bash
curl -X GET "http://localhost:8000/api/customers?limit=10&is_member=true"
```

#### Create a new fruit
```bash
curl -X POST "http://localhost:8000/api/fruits" \
  -H "Content-Type: application/json" \
  -d '{
    "barCode": "123456789014",
    "name": "Fresh Banana",
    "category": "Tropical",
    "pricePerKg": 2.99,
    "stockKg": 100,
    "country": "Ecuador",
    "supplierId": "64f1234567890abcdef12340",
    "isOrganic": false
  }'
```

#### Update order status
```bash
curl -X PUT "http://localhost:8000/api/orders/64f1234567890abcdef12349" \
  -H "Content-Type: application/json" \
  -d '{"status": "Completed"}'
```

### Using Python requests
```python
import requests

# Get dashboard statistics
response = requests.get("http://localhost:8000/api/stats")
stats = response.json()
print(f"Total customers: {stats['data']['customers_count']}")

# Create a new customer
customer_data = {
    "customerId": "CUST003",
    "name": "Alice Johnson",
    "phone": "+1111222333",
    "address": "789 Elm St, City",
    "isMember": True
}
response = requests.post("http://localhost:8000/api/customers", json=customer_data)
print(response.json())
```

---

## 📝 Notes

- All timestamps are in ISO format
- MongoDB ObjectIds are returned as strings
- Pagination is available for all list endpoints
- All POST/PUT requests expect JSON content type
- The API returns consistent response formats with `success` field