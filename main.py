from fastapi import FastAPI, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "fruit_store")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_RELOAD = os.getenv("APP_RELOAD", "false").lower() == "true"
APP_TITLE = os.getenv("APP_TITLE", "Fruit Store")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")
STATIC_DIR = os.getenv("STATIC_DIR", "static")

# Initialize FastAPI app
app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    debug=DEBUG,
    description="A comprehensive fruit store management system with inventory, customers, suppliers, and orders management."
)

# MongoDB connection
client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

# Collections
customers_collection = database.customers
fruits_collection = database.fruits
suppliers_collection = database.suppliers
orders_collection = database.orders

# Templates
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Static files (if you have a static directory)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print(f"🚀 Starting {APP_TITLE} v{APP_VERSION}")
    print(f"📊 MongoDB URL: {MONGODB_URL}")
    print(f"🗃️  Database: {DATABASE_NAME}")
    print(f"🌐 Server: http://{APP_HOST}:{APP_PORT}:")
    print(f"🐛 Debug mode: {DEBUG}")
    
    # Test database connection
    try:
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🔄 Shutting down application...")
    client.close()
    print("✅ MongoDB connection closed")

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        
        # Handle MongoDB's special formats first
        if "$oid" in doc:
            return doc["$oid"]
        if "$date" in doc:
            date_str = doc["$date"]
            if isinstance(date_str, str):
                
                # Extract just the date part (YYYY-MM-DD)
                return date_str.split('T')[0]
            return str(date_str).split('T')[0]
        
        # Process regular dictionary
        result = {}
        for key, value in doc.items():
            if isinstance(value, ObjectId):
                result[key] = str(value)
            elif isinstance(value, datetime):
                result[key] = value.strftime('%Y-%m-%d')
            elif isinstance(value, dict):
                result[key] = serialize_doc(value)
            elif isinstance(value, list):
                result[key] = serialize_doc(value)
            else:
                result[key] = value
        return result
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.strftime('%Y-%m-%d')
    return doc

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await client.admin.command('ping')
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app": APP_TITLE,
            "version": APP_VERSION,
            "database": "connected"
        })
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "app": APP_TITLE,
            "version": APP_VERSION,
            "database": "disconnected",
            "error": str(e)
        }, status_code=503)

# API endpoint for dashboard statistics
@app.get("/api/stats")
async def get_dashboard_stats():
    """Get dashboard statistics for quick stats display"""
    try:
        
        # Get counts for each collection
        customers_count = await customers_collection.count_documents({})
        fruits_count = await fruits_collection.count_documents({})
        suppliers_count = await suppliers_collection.count_documents({"active": True})
        orders_count = await orders_collection.count_documents({})
        
        # Additional stats you might want to add
        total_suppliers = await suppliers_collection.count_documents({})
        pending_orders = await orders_collection.count_documents({"status": "pending"})
        organic_fruits = await fruits_collection.count_documents({"isOrganic": True})
        members_count = await customers_collection.count_documents({"isMember": True})
        
        return JSONResponse({
            "success": True,
            "data": {
                "customers_count": customers_count,
                "fruits_count": fruits_count,
                "suppliers_count": suppliers_count,
                "orders_count": orders_count,
                "total_suppliers": total_suppliers,
                "pending_orders": pending_orders,
                "organic_fruits": organic_fruits,
                "members_count": members_count
            }
        })
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# CUSTOMERS CRUD
@app.get("/customers", response_class=HTMLResponse)
async def list_customers(request: Request):
    customers = await customers_collection.find().to_list(100)
    customers = serialize_doc(customers)
    return templates.TemplateResponse("customers/list.html", {"request": request, "customers": customers})

@app.get("/customers/create", response_class=HTMLResponse)
async def create_customer_form(request: Request):
    return templates.TemplateResponse("customers/create.html", {"request": request})

@app.post("/customers/create")
async def create_customer(
    request: Request,
    name: str = Form(...),
    customerId: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    isMember: bool = Form(False)
):
    customer_data = {
        "customerId": customerId,
        "name": name,
        "phone": phone,
        "address": address,
        "isMember": isMember,
        "updated_at": datetime.utcnow()
    }
    await customers_collection.insert_one(customer_data)
    return RedirectResponse("/customers", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer_form(request: Request, customer_id: str):
    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer = serialize_doc(customer)
    return templates.TemplateResponse("customers/edit.html", {"request": request, "customer": customer})

@app.post("/customers/{customer_id}/edit")
async def edit_customer(
    customer_id: str,
    name: str = Form(...),
    customerId: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    isMember: bool = Form(False)
):
    update_data = {
        "customerId": customerId,
        "name": name,
        "phone": phone,
        "address": address,
        "isMember": isMember,
        "updated_at": datetime.utcnow()
    }
    result = await customers_collection.update_one(
        {"_id": ObjectId(customer_id)}, 
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RedirectResponse("/customers", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/customers/{customer_id}/delete")
async def delete_customer(customer_id: str):
    result = await customers_collection.delete_one({"_id": ObjectId(customer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RedirectResponse("/customers", status_code=status.HTTP_303_SEE_OTHER)

# FRUITS CRUD
@app.get("/fruits", response_class=HTMLResponse)
async def list_fruits(request: Request):
    fruits = await fruits_collection.find().to_list(100)
    fruits = serialize_doc(fruits)
    
    # Get supplier names for display
    for fruit in fruits:
        if fruit.get("supplierId"):
            try:
                supplier = await suppliers_collection.find_one({"_id": ObjectId(fruit["supplierId"])})
                fruit["supplierName"] = supplier["name"] if supplier else "Unknown"
            except:
                fruit["supplierName"] = "Unknown"
    
    return templates.TemplateResponse("fruits/list.html", {"request": request, "fruits": fruits})

@app.get("/fruits/create", response_class=HTMLResponse)
async def create_fruit_form(request: Request):
    suppliers = await suppliers_collection.find({"active": True}).to_list(100)
    suppliers = serialize_doc(suppliers)
    return templates.TemplateResponse("fruits/create.html", {"request": request, "suppliers": suppliers})

@app.post("/fruits/create")
async def create_fruit(
    request: Request,
    barCode: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    pricePerKg: float = Form(...),
    stockKg: int = Form(...),
    country: str = Form(...),
    supplierId: str = Form(...),
    isOrganic: bool = Form(False)
):
    fruit_data = {
        "barCode": barCode,
        "name": name,
        "category": category,
        "pricePerKg": pricePerKg,
        "stockKg": stockKg,
        "country": country,
        "supplierId": ObjectId(supplierId),
        "isOrganic": isOrganic
    }
    await fruits_collection.insert_one(fruit_data)
    return RedirectResponse("/fruits", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/fruits/{fruit_id}/edit", response_class=HTMLResponse)
async def edit_fruit_form(request: Request, fruit_id: str):
    fruit = await fruits_collection.find_one({"_id": ObjectId(fruit_id)})
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    fruit = serialize_doc(fruit)
    
    suppliers = await suppliers_collection.find({"active": True}).to_list(100)
    suppliers = serialize_doc(suppliers)
    
    return templates.TemplateResponse("fruits/edit.html", {"request": request, "fruit": fruit, "suppliers": suppliers})

@app.post("/fruits/{fruit_id}/edit")
async def edit_fruit(
    fruit_id: str,
    barCode: str = Form(...),
    name: str = Form(...),
    category: str = Form(...),
    pricePerKg: float = Form(...),
    stockKg: int = Form(...),
    country: str = Form(...),
    supplierId: str = Form(...),
    isOrganic: bool = Form(False)
):
    update_data = {
        "barCode": barCode,
        "name": name,
        "category": category,
        "pricePerKg": pricePerKg,
        "stockKg": stockKg,
        "country": country,
        "supplierId": ObjectId(supplierId),
        "isOrganic": isOrganic
    }
    result = await fruits_collection.update_one(
        {"_id": ObjectId(fruit_id)}, 
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return RedirectResponse("/fruits", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/fruits/{fruit_id}/delete")
async def delete_fruit(fruit_id: str):
    result = await fruits_collection.delete_one({"_id": ObjectId(fruit_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return RedirectResponse("/fruits", status_code=status.HTTP_303_SEE_OTHER)

# SUPPLIERS CRUD
@app.get("/suppliers", response_class=HTMLResponse)
async def list_suppliers(request: Request):
    suppliers = await suppliers_collection.find().to_list(100)
    suppliers = serialize_doc(suppliers)
    return templates.TemplateResponse("suppliers/list.html", {"request": request, "suppliers": suppliers})

@app.get("/suppliers/create", response_class=HTMLResponse)
async def create_supplier_form(request: Request):
    return templates.TemplateResponse("suppliers/create.html", {"request": request})

@app.post("/suppliers/create")
async def create_supplier(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    fruitsSupplied: str = Form(...),
    active: bool = Form(False)
):
    fruits_list = [fruit.strip() for fruit in fruitsSupplied.split(",") if fruit.strip()]
    supplier_data = {
        "name": name,
        "phone": phone,
        "location": location,
        "fruitsSupplied": fruits_list,
        "active": active
    }
    await suppliers_collection.insert_one(supplier_data)
    return RedirectResponse("/suppliers", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/suppliers/{supplier_id}/edit", response_class=HTMLResponse)
async def edit_supplier_form(request: Request, supplier_id: str):
    supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier = serialize_doc(supplier)
    supplier["fruitsSuppliedStr"] = ", ".join(supplier.get("fruitsSupplied", []))
    return templates.TemplateResponse("suppliers/edit.html", {"request": request, "supplier": supplier})

@app.post("/suppliers/{supplier_id}/edit")
async def edit_supplier(
    supplier_id: str,
    name: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    fruitsSupplied: str = Form(...),
    active: bool = Form(False)
):
    fruits_list = [fruit.strip() for fruit in fruitsSupplied.split(",") if fruit.strip()]
    update_data = {
        "name": name,
        "phone": phone,
        "location": location,
        "fruitsSupplied": fruits_list,
        "active": active
    }
    result = await suppliers_collection.update_one(
        {"_id": ObjectId(supplier_id)}, 
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return RedirectResponse("/suppliers", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/suppliers/{supplier_id}/delete")
async def delete_supplier(supplier_id: str):
    result = await suppliers_collection.delete_one({"_id": ObjectId(supplier_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return RedirectResponse("/suppliers", status_code=status.HTTP_303_SEE_OTHER)

# ORDERS CRUD - FIXED VERSION
@app.get("/orders", response_class=HTMLResponse)
async def list_orders(request: Request):
    try:
        # Get raw orders from database with explicit conversion
        orders_raw = []
        async for order in orders_collection.find():
            orders_raw.append(order)
        
        # Process each order individually
        processed_orders = []
        
        for order in orders_raw:
            # Create a clean order dictionary
            processed_order = {
                "_id": str(order["_id"]),
                "orderDate": order.get("orderDate").strftime('%Y-%m-%d') if order.get("orderDate") else 'N/A',
                "customerId": order.get("customerId"),
                "totalAmount": order.get("totalAmount", 0),
                "status": order.get("status", "Unknown"),
                "orderItems": []
            }
            
            # Get customer name using customerId - FIXED LOGIC
            customer_id = order.get("customerId")
            if customer_id:
                try:
                    # First try to find by customerId field (string)
                    customer = await customers_collection.find_one({"customerId": customer_id})
                    
                    # If not found and customer_id looks like ObjectId, try _id
                    if not customer:
                        try:
                            customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
                        except:
                            pass
                    
                    # If still not found, try converting customer_id to different types
                    if not customer:
                        # Try as integer
                        try:
                            customer_id_int = int(customer_id)
                            customer = await customers_collection.find_one({"customerId": customer_id_int})
                        except:
                            pass
                    
                    # If still not found, try as string version of number
                    if not customer:
                        try:
                            customer_id_str = str(customer_id)
                            customer = await customers_collection.find_one({"customerId": customer_id_str})
                        except:
                            pass
                    
                    processed_order["customerName"] = customer["name"] if customer else f"Unknown ({customer_id})"
                    
                except Exception as e:
                    print(f"Error finding customer {customer_id}: {e}")
                    processed_order["customerName"] = f"Unknown ({customer_id})"
            else:
                processed_order["customerName"] = "No Customer ID"
            
            # Process items safely
            raw_items = order.get("items")
            if raw_items and hasattr(raw_items, '__iter__') and not isinstance(raw_items, str):
                try:
                    # Convert to list if it's not already
                    items_list = list(raw_items) if not isinstance(raw_items, list) else raw_items
                    
                    for item in items_list:
                        if isinstance(item, dict):
                            processed_item = {
                                "quantityKg": item.get("quantityKg", 0)
                            }
                            
                            # Get fruit name
                            fruit_id = item.get("fruitId")
                            if fruit_id:
                                try:
                                    fruit = await fruits_collection.find_one({"_id": fruit_id})
                                    processed_item["fruitName"] = fruit["name"] if fruit else f"Unknown Fruit"
                                    processed_item["fruitId"] = str(fruit_id)
                                except Exception as e:
                                    print(f"Error finding fruit {fruit_id}: {e}")
                                    processed_item["fruitName"] = "Unknown Fruit"
                                    processed_item["fruitId"] = str(fruit_id) if fruit_id else ""
                            else:
                                processed_item["fruitName"] = "No Fruit ID"
                                processed_item["fruitId"] = ""
                            
                            processed_order["orderItems"].append(processed_item)
                except Exception as e:
                    print(f"Error processing items for order {order['_id']}: {e}")
                    processed_order["orderItems"] = []
            
            processed_orders.append(processed_order)
        
        return templates.TemplateResponse("orders/list.html", {"request": request, "orders": processed_orders})
        
    except Exception as e:
        print(f"Error in list_orders: {e}")
        import traceback
        traceback.print_exc()
        # Return empty orders list in case of error
        return templates.TemplateResponse("orders/list.html", {"request": request, "orders": []})

@app.get("/orders/create", response_class=HTMLResponse)
async def create_order_form(request: Request):
    customers = await customers_collection.find().to_list(100)
    customers = serialize_doc(customers)
    fruits = await fruits_collection.find().to_list(100)
    fruits = serialize_doc(fruits)
    return templates.TemplateResponse("orders/create.html", {"request": request, "customers": customers, "fruits": fruits})

@app.post("/orders/create")
async def create_order(
    request: Request,
    customerId: str = Form(...),
    fruitId: str = Form(...),
    quantityKg: float = Form(...),
    order_status: str = Form(..., alias="status")
):
    # Get fruit price
    fruit = await fruits_collection.find_one({"_id": ObjectId(fruitId)})
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    
    total_amount = fruit["pricePerKg"] * quantityKg
    
    # Validate customer exists by customerId (not _id)
    customer = await customers_collection.find_one({"customerId": customerId})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    order_data = {
        "orderDate": datetime.utcnow(),
        "customerId": customerId,  # Store the customerId field consistently
        "items": [
            {
                "fruitId": ObjectId(fruitId),
                "quantityKg": quantityKg
            }
        ],
        "totalAmount": total_amount,
        "status": order_status
    }
    await orders_collection.insert_one(order_data)
    return RedirectResponse("/orders", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/orders/{order_id}/edit", response_class=HTMLResponse)
async def edit_order_form(request: Request, order_id: str):
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Process order safely
    processed_order = {
        "_id": str(order["_id"]),
        "orderDate": order.get("orderDate").strftime('%Y-%m-%d') if order.get("orderDate") else 'N/A',
        "customerId": order.get("customerId"),
        "totalAmount": order.get("totalAmount", 0),
        "status": order.get("status", "Unknown"),
        "orderItems": []
    }
    
    # Process items safely
    raw_items = order.get("items", [])
    if isinstance(raw_items, list):
        for item in raw_items:
            if isinstance(item, dict):
                processed_item = {
                    "quantityKg": item.get("quantityKg", 0)
                }
                
                # Get fruit name
                fruit_id = item.get("fruitId")
                if fruit_id:
                    try:
                        fruit = await fruits_collection.find_one({"_id": fruit_id})
                        processed_item["fruitName"] = fruit["name"] if fruit else "Unknown Fruit"
                    except Exception as e:
                        print(f"Error finding fruit {fruit_id}: {e}")
                        processed_item["fruitName"] = "Unknown Fruit"
                else:
                    processed_item["fruitName"] = "No Fruit ID"
                
                processed_order["orderItems"].append(processed_item)
    
    customers = await customers_collection.find().to_list(100)
    customers = serialize_doc(customers)
    fruits = await fruits_collection.find().to_list(100)
    fruits = serialize_doc(fruits)
    
    return templates.TemplateResponse("orders/edit.html", {"request": request, "order": processed_order, "customers": customers, "fruits": fruits})

@app.post("/orders/{order_id}/edit")
async def edit_order(
    order_id: str,
    order_status: str = Form(..., alias="status")
):
    update_data = {
        "status": order_status,
        "updated_at": datetime.utcnow()
    }
    result = await orders_collection.update_one(
        {"_id": ObjectId(order_id)}, 
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return RedirectResponse("/orders", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/orders/{order_id}/delete")
async def delete_order(order_id: str):
    result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return RedirectResponse("/orders", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app, 
        host=APP_HOST, 
        port=APP_PORT, 
        reload=APP_RELOAD
    )