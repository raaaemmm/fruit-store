from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId
from datetime import datetime
from database.connection import get_collections
from models.customer import CustomerModel, CustomerUpdateModel
from models.fruit import FruitModel, FruitUpdateModel
from models.order import OrderModel, OrderUpdateModel
from models.supplier import SupplierModel, SupplierUpdateModel
from utils.helpers import serialize_doc

# Initialize router
api_router = APIRouter()

# Get database collections
collections = get_collections()
customers_collection = collections['customers']
fruits_collection = collections['fruits']
suppliers_collection = collections['suppliers']
orders_collection = collections['orders']

# ==========================================
# DASHBOARD STATISTICS API
# ==========================================

@api_router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics for quick stats display"""
    try:
        # Get counts for each collection
        customers_count = await customers_collection.count_documents({})
        fruits_count = await fruits_collection.count_documents({})
        suppliers_count = await suppliers_collection.count_documents({"active": True})
        orders_count = await orders_collection.count_documents({})
        
        # Additional stats
        total_suppliers = await suppliers_collection.count_documents({})
        pending_orders = await orders_collection.count_documents({"status": "Pending"})
        organic_fruits = await fruits_collection.count_documents({"isOrganic": True})
        members_count = await customers_collection.count_documents({"isMember": True})
        
        return {
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
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# ==========================================
# CUSTOMERS API ENDPOINTS
# ==========================================

@api_router.get("/customers")
async def get_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_member: Optional[bool] = Query(None)
):
    """Get list of customers with pagination and filtering"""
    try:
        # Build filter query
        filter_query = {}
        if is_member is not None:
            filter_query["isMember"] = is_member
        
        # Get customers with pagination
        customers = await customers_collection.find(filter_query).skip(skip).limit(limit).to_list(limit)
        total_count = await customers_collection.count_documents(filter_query)
        
        return {
            "success": True,
            "data": serialize_doc(customers),
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.get("/customers/{customer_id}")
async def get_customer(customer_id: str):
    """Get a specific customer by ID"""
    try:
        customer = await customers_collection.find_one({"_id": ObjectId(customer_id)})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "success": True,
            "data": serialize_doc(customer)
        }
    except Exception as e:
        if "Customer not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.post("/customers")
async def create_customer_api(customer: CustomerModel):
    """Create a new customer via API"""
    try:
        customer_data = customer.dict()
        customer_data["updated_at"] = datetime.utcnow()
        
        result = await customers_collection.insert_one(customer_data)
        
        return {
            "success": True,
            "message": "Customer created successfully",
            "customer_id": str(result.inserted_id)
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.put("/customers/{customer_id}")
async def update_customer_api(customer_id: str, customer_update: CustomerUpdateModel):
    """Update a customer via API"""
    try:
        update_data = {k: v for k, v in customer_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await customers_collection.update_one(
            {"_id": ObjectId(customer_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "success": True,
            "message": "Customer updated successfully"
        }
    except Exception as e:
        if "Customer not found" in str(e) or "No update data" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.delete("/customers/{customer_id}")
async def delete_customer_api(customer_id: str):
    """Delete a customer via API"""
    try:
        result = await customers_collection.delete_one({"_id": ObjectId(customer_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return {
            "success": True,
            "message": "Customer deleted successfully"
        }
    except Exception as e:
        if "Customer not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# ==========================================
# FRUITS API ENDPOINTS
# ==========================================

@api_router.get("/fruits")
async def get_fruits(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = Query(None),
    is_organic: Optional[bool] = Query(None),
    min_stock: Optional[int] = Query(None, ge=0)
):
    """Get list of fruits with pagination and filtering"""
    try:
        # Build filter query
        filter_query = {}
        if category:
            filter_query["category"] = category
        if is_organic is not None:
            filter_query["isOrganic"] = is_organic
        if min_stock is not None:
            filter_query["stockKg"] = {"$gte": min_stock}
        
        # Get fruits with pagination
        fruits = await fruits_collection.find(filter_query).skip(skip).limit(limit).to_list(limit)
        total_count = await fruits_collection.count_documents(filter_query)
        
        # Add supplier names
        for fruit in fruits:
            if fruit.get("supplierId"):
                try:
                    supplier = await suppliers_collection.find_one({"_id": fruit["supplierId"]})
                    fruit["supplierName"] = supplier["name"] if supplier else "Unknown"
                except:
                    fruit["supplierName"] = "Unknown"
        
        return {
            "success": True,
            "data": serialize_doc(fruits),
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.get("/fruits/{fruit_id}")
async def get_fruit(fruit_id: str):
    """Get a specific fruit by ID"""
    try:
        fruit = await fruits_collection.find_one({"_id": ObjectId(fruit_id)})
        if not fruit:
            raise HTTPException(status_code=404, detail="Fruit not found")
        
        # Add supplier name
        if fruit.get("supplierId"):
            try:
                supplier = await suppliers_collection.find_one({"_id": fruit["supplierId"]})
                fruit["supplierName"] = supplier["name"] if supplier else "Unknown"
            except:
                fruit["supplierName"] = "Unknown"
        
        return {
            "success": True,
            "data": serialize_doc(fruit)
        }
    except Exception as e:
        if "Fruit not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.post("/fruits")
async def create_fruit_api(fruit: FruitModel):
    """Create a new fruit via API"""
    try:
        fruit_data = fruit.dict()
        fruit_data["supplierId"] = ObjectId(fruit_data["supplierId"])
        
        result = await fruits_collection.insert_one(fruit_data)
        
        return {
            "success": True,
            "message": "Fruit created successfully",
            "fruit_id": str(result.inserted_id)
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.put("/fruits/{fruit_id}")
async def update_fruit_api(fruit_id: str, fruit_update: FruitUpdateModel):
    """Update a fruit via API"""
    try:
        update_data = {k: v for k, v in fruit_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        if "supplierId" in update_data:
            update_data["supplierId"] = ObjectId(update_data["supplierId"])
        
        result = await fruits_collection.update_one(
            {"_id": ObjectId(fruit_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Fruit not found")
        
        return {
            "success": True,
            "message": "Fruit updated successfully"
        }
    except Exception as e:
        if "Fruit not found" in str(e) or "No update data" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.delete("/fruits/{fruit_id}")
async def delete_fruit_api(fruit_id: str):
    """Delete a fruit via API"""
    try:
        result = await fruits_collection.delete_one({"_id": ObjectId(fruit_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Fruit not found")
        
        return {
            "success": True,
            "message": "Fruit deleted successfully"
        }
    except Exception as e:
        if "Fruit not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# ==========================================
# SUPPLIERS API ENDPOINTS
# ==========================================

@api_router.get("/suppliers")
async def get_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    active_only: bool = Query(False)
):
    """Get list of suppliers with pagination and filtering"""
    try:
        # Build filter query
        filter_query = {}
        if active_only:
            filter_query["active"] = True
        
        # Get suppliers with pagination
        suppliers = await suppliers_collection.find(filter_query).skip(skip).limit(limit).to_list(limit)
        total_count = await suppliers_collection.count_documents(filter_query)
        
        return {
            "success": True,
            "data": serialize_doc(suppliers),
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.get("/suppliers/{supplier_id}")
async def get_supplier(supplier_id: str):
    """Get a specific supplier by ID"""
    try:
        supplier = await suppliers_collection.find_one({"_id": ObjectId(supplier_id)})
        if not supplier:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        return {
            "success": True,
            "data": serialize_doc(supplier)
        }
    except Exception as e:
        if "Supplier not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.post("/suppliers")
async def create_supplier_api(supplier: SupplierModel):
    """Create a new supplier via API"""
    try:
        supplier_data = supplier.dict()
        
        result = await suppliers_collection.insert_one(supplier_data)
        
        return {
            "success": True,
            "message": "Supplier created successfully",
            "supplier_id": str(result.inserted_id)
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.put("/suppliers/{supplier_id}")
async def update_supplier_api(supplier_id: str, supplier_update: SupplierUpdateModel):
    """Update a supplier via API"""
    try:
        update_data = {k: v for k, v in supplier_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        result = await suppliers_collection.update_one(
            {"_id": ObjectId(supplier_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        return {
            "success": True,
            "message": "Supplier updated successfully"
        }
    except Exception as e:
        if "Supplier not found" in str(e) or "No update data" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.delete("/suppliers/{supplier_id}")
async def delete_supplier_api(supplier_id: str):
    """Delete a supplier via API"""
    try:
        result = await suppliers_collection.delete_one({"_id": ObjectId(supplier_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Supplier not found")
        
        return {
            "success": True,
            "message": "Supplier deleted successfully"
        }
    except Exception as e:
        if "Supplier not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

# ==========================================
# ORDERS API ENDPOINTS
# ==========================================

@api_router.get("/orders")
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    customer_id: Optional[str] = Query(None)
):
    """Get list of orders with pagination and filtering"""
    try:
        # Build filter query
        filter_query = {}
        if status:
            filter_query["status"] = status
        if customer_id:
            filter_query["customerId"] = customer_id
        
        # Get orders with pagination
        orders_raw = await orders_collection.find(filter_query).skip(skip).limit(limit).to_list(limit)
        total_count = await orders_collection.count_documents(filter_query)
        
        # Process orders with customer and item details
        processed_orders = []
        for order in orders_raw:
            processed_order = serialize_doc(order)
            
            # Get customer name
            customer_id = order.get("customerId")
            if customer_id:
                customer = await customers_collection.find_one({"customerId": customer_id})
                processed_order["customerName"] = customer["name"] if customer else "Unknown"
            
            # Get item details
            if order.get("items"):
                processed_items = []
                for item in order["items"]:
                    processed_item = serialize_doc(item)
                    # Get fruit details
                    if item.get("fruitId"):
                        fruit = await fruits_collection.find_one({"_id": item["fruitId"]})
                        if fruit:
                            processed_item["fruitName"] = fruit["name"]
                            processed_item["fruitPrice"] = fruit["pricePerKg"]
                    processed_items.append(processed_item)
                processed_order["items"] = processed_items
            
            processed_orders.append(processed_order)
        
        return {
            "success": True,
            "data": processed_orders,
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.get("/orders/{order_id}")
async def get_order(order_id: str):
    """Get a specific order by ID"""
    try:
        order = await orders_collection.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        processed_order = serialize_doc(order)
        
        # Get customer name
        customer_id = order.get("customerId")
        if customer_id:
            customer = await customers_collection.find_one({"customerId": customer_id})
            processed_order["customerName"] = customer["name"] if customer else "Unknown"
        
        # Get item details
        if order.get("items"):
            processed_items = []
            for item in order["items"]:
                processed_item = serialize_doc(item)
                # Get fruit details
                if item.get("fruitId"):
                    fruit = await fruits_collection.find_one({"_id": item["fruitId"]})
                    if fruit:
                        processed_item["fruitName"] = fruit["name"]
                        processed_item["fruitPrice"] = fruit["pricePerKg"]
                processed_items.append(processed_item)
            processed_order["items"] = processed_items
        
        return {
            "success": True,
            "data": processed_order
        }
    except Exception as e:
        if "Order not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.post("/orders")
async def create_order_api(order: OrderModel):
    """Create a new order via API"""
    try:
        # Validate customer exists
        customer = await customers_collection.find_one({"customerId": order.customerId})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Calculate total amount and validate fruits
        total_amount = 0
        processed_items = []
        
        for item in order.items:
            fruit = await fruits_collection.find_one({"_id": ObjectId(item.fruitId)})
            if not fruit:
                raise HTTPException(status_code=404, detail=f"Fruit with ID {item.fruitId} not found")
            
            # Check stock availability
            if fruit["stockKg"] < item.quantityKg:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for {fruit['name']}. Available: {fruit['stockKg']}kg")
            
            item_total = fruit["pricePerKg"] * item.quantityKg
            total_amount += item_total
            
            processed_items.append({
                "fruitId": ObjectId(item.fruitId),
                "quantityKg": item.quantityKg
            })
        
        order_data = {
            "orderDate": datetime.utcnow(),
            "customerId": order.customerId,
            "items": processed_items,
            "totalAmount": total_amount,
            "status": order.status
        }
        
        result = await orders_collection.insert_one(order_data)
        
        return {
            "success": True,
            "message": "Order created successfully",
            "order_id": str(result.inserted_id),
            "total_amount": total_amount
        }
    except Exception as e:
        if "not found" in str(e) or "Insufficient stock" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.put("/orders/{order_id}")
async def update_order_api(order_id: str, order_update: OrderUpdateModel):
    """Update an order via API"""
    try:
        update_data = {k: v for k, v in order_update.dict().items() if v is not None}
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        update_data["updated_at"] = datetime.utcnow()
        
        result = await orders_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "message": "Order updated successfully"
        }
    except Exception as e:
        if "Order not found" in str(e) or "No update data" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)

@api_router.delete("/orders/{order_id}")
async def delete_order_api(order_id: str):
    """Delete an order via API"""
    try:
        result = await orders_collection.delete_one({"_id": ObjectId(order_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "message": "Order deleted successfully"
        }
    except Exception as e:
        if "Order not found" in str(e):
            raise e
        return JSONResponse({
            "success": False,
            "error": str(e)
        }, status_code=500)