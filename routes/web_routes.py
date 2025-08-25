from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from datetime import datetime
from database.connection import get_collections
from utils.helpers import serialize_doc
import os

# Configuration
TEMPLATE_DIR = os.getenv("TEMPLATE_DIR", "templates")

# Initialize router and templates
web_router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# Get database collections
collections = get_collections()
customers_collection = collections['customers']
fruits_collection = collections['fruits']
suppliers_collection = collections['suppliers']
orders_collection = collections['orders']

# ==========================================
# HOME / DASHBOARD ROUTE
# ==========================================

@web_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Dashboard homepage"""
    return templates.TemplateResponse("index.html", {"request": request})

# ==========================================
# CUSTOMERS WEB ROUTES
# ==========================================

@web_router.get("/customers", response_class=HTMLResponse)
async def list_customers(request: Request):
    """List all customers page"""
    customers = await customers_collection.find().to_list(100)
    customers = serialize_doc(customers)
    return templates.TemplateResponse("customers/list.html", {"request": request, "customers": customers})

@web_router.get("/customers/create", response_class=HTMLResponse)
async def create_customer_form(request: Request):
    """Create customer form page"""
    return templates.TemplateResponse("customers/create.html", {"request": request})

@web_router.post("/customers/create")
async def create_customer(
    request: Request,
    name: str = Form(...),
    customerId: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    isMember: bool = Form(False)
):
    """Create new customer"""
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

@web_router.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer_form(request: Request, customer_id: str):
    """Edit customer form page"""
    customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer = serialize_doc(customer)
    return templates.TemplateResponse("customers/edit.html", {"request": request, "customer": customer})

@web_router.post("/customers/{customer_id}/edit")
async def edit_customer(
    customer_id: str,
    name: str = Form(...),
    customerId: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    isMember: bool = Form(False)
):
    """Update customer"""
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

@web_router.post("/customers/{customer_id}/delete")
async def delete_customer(customer_id: str):
    """Delete customer"""
    result = await customers_collection.delete_one({"_id": ObjectId(customer_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return RedirectResponse("/customers", status_code=status.HTTP_303_SEE_OTHER)

# ==========================================
# FRUITS WEB ROUTES
# ==========================================

@web_router.get("/fruits", response_class=HTMLResponse)
async def list_fruits(request: Request):
    """List all fruits page"""
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

@web_router.get("/fruits/create", response_class=HTMLResponse)
async def create_fruit_form(request: Request):
    """Create fruit form page"""
    suppliers = await suppliers_collection.find({"active": True}).to_list(100)
    suppliers = serialize_doc(suppliers)
    return templates.TemplateResponse("fruits/create.html", {"request": request, "suppliers": suppliers})

@web_router.post("/fruits/create")
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
    """Create new fruit"""
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

@web_router.get("/fruits/{fruit_id}/edit", response_class=HTMLResponse)
async def edit_fruit_form(request: Request, fruit_id: str):
    """Edit fruit form page"""
    fruit = await fruits_collection.find_one({"_id": ObjectId(fruit_id)})
    if not fruit:
        raise HTTPException(status_code=404, detail="Fruit not found")
    fruit = serialize_doc(fruit)
    
    suppliers = await suppliers_collection.find({"active": True}).to_list(100)
    suppliers = serialize_doc(suppliers)
    
    return templates.TemplateResponse("fruits/edit.html", {"request": request, "fruit": fruit, "suppliers": suppliers})

@web_router.post("/fruits/{fruit_id}/edit")
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
    """Update fruit"""
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

@web_router.post("/fruits/{fruit_id}/delete")
async def delete_fruit(fruit_id: str):
    """Delete fruit"""
    result = await fruits_collection.delete_one({"_id": ObjectId(fruit_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Fruit not found")
    return RedirectResponse("/fruits", status_code=status.HTTP_303_SEE_OTHER)

# ==========================================
# SUPPLIERS WEB ROUTES
# ==========================================

@web_router.get("/suppliers", response_class=HTMLResponse)
async def list_suppliers(request: Request):
    """List all suppliers page"""
    suppliers = await suppliers_collection.find().to_list(100)
    suppliers = serialize_doc(suppliers)
    return templates.TemplateResponse("suppliers/list.html", {"request": request, "suppliers": suppliers})

@web_router.get("/suppliers/create", response_class=HTMLResponse)
async def create_supplier_form(request: Request):
    """Create supplier form page"""
    return templates.TemplateResponse("suppliers/create.html", {"request": request})

@web_router.post("/suppliers/create")
async def create_supplier(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    fruitsSupplied: str = Form(...),
    active: bool = Form(False)
):
    """Create new supplier"""
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

@web_router.get("/suppliers/{supplier_id}/edit", response_class=HTMLResponse)
async def edit_supplier_form(request: Request, supplier_id: str):
    """Edit supplier form page"""
    supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    supplier = serialize_doc(supplier)
    supplier["fruitsSuppliedStr"] = ", ".join(supplier.get("fruitsSupplied", []))
    return templates.TemplateResponse("suppliers/edit.html", {"request": request, "supplier": supplier})

@web_router.post("/suppliers/{supplier_id}/edit")
async def edit_supplier(
    supplier_id: str,
    name: str = Form(...),
    phone: str = Form(...),
    location: str = Form(...),
    fruitsSupplied: str = Form(...),
    active: bool = Form(False)
):
    """Update supplier"""
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

@web_router.post("/suppliers/{supplier_id}/delete")
async def delete_supplier(supplier_id: str):
    """Delete supplier"""
    result = await suppliers_collection.delete_one({"_id": ObjectId(supplier_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return RedirectResponse("/suppliers", status_code=status.HTTP_303_SEE_OTHER)

# ==========================================
# ORDERS WEB ROUTES
# ==========================================

@web_router.get("/orders", response_class=HTMLResponse)
async def list_orders(request: Request):
    """List all orders page"""
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

@web_router.get("/orders/create", response_class=HTMLResponse)
async def create_order_form(request: Request):
    """Create order form page"""
    customers = await customers_collection.find().to_list(100)
    customers = serialize_doc(customers)
    fruits = await fruits_collection.find().to_list(100)
    fruits = serialize_doc(fruits)
    return templates.TemplateResponse("orders/create.html", {"request": request, "customers": customers, "fruits": fruits})

@web_router.post("/orders/create")
async def create_order(
    request: Request,
    customerId: str = Form(...),
    fruitId: str = Form(...),
    quantityKg: float = Form(...),
    order_status: str = Form(..., alias="status")
):
    """Create new order"""
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

@web_router.get("/orders/{order_id}/edit", response_class=HTMLResponse)
async def edit_order_form(request: Request, order_id: str):
    """Edit order form page"""
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

@web_router.post("/orders/{order_id}/edit")
async def edit_order(
    order_id: str,
    order_status: str = Form(..., alias="status")
):
    """Update order"""
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

@web_router.post("/orders/{order_id}/delete")
async def delete_order(order_id: str):
    """Delete order"""
    result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return RedirectResponse("/orders", status_code=status.HTTP_303_SEE_OTHER)