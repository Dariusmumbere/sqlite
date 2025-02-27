from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic import BaseModel
import sqlite3
from sqlite3 import Connection
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (replace with specific origins in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# SQLite database connection
def get_db():
    conn = sqlite3.connect('itech.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access to rows
    return conn

# Create tables if they don't exist
def init_db(conn: Connection):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            buying_price REAL NOT NULL,
            selling_price REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()

# Pydantic models for request validation
class Product(BaseModel):
    name: str
    type: str
    buying_price: float
    selling_price: float

class Service(BaseModel):
    name: str
    description: str
    price: float

# Initialize the database
@app.on_event("startup")
def startup():
    conn = get_db()
    init_db(conn)

# CRUD operations for Products
@app.post("/products/")
def create_product(product: Product, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products (name, type, buying_price, selling_price)
            VALUES (?, ?, ?, ?)
        ''', (product.name, product.type, product.buying_price, product.selling_price))
        conn.commit()
        return {"message": "Product added successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/products/")
def read_products(conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    return {"products": [dict(product) for product in products]}  # Convert rows to dictionaries

@app.get("/products/{product_id}")
def read_product(product_id: int, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    product = cursor.fetchone()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(product)  # Convert row to dictionary

@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE products
        SET name = ?, type = ?, buying_price = ?, selling_price = ?
        WHERE id = ?
    ''', (product.name, product.type, product.buying_price, product.selling_price, product_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product updated successfully"}

@app.delete("/products/{product_id}")
def delete_product(product_id: int, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

# CRUD operations for Services
@app.post("/services/")
def create_service(service: Service, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO services (name, description, price)
            VALUES (?, ?, ?)
        ''', (service.name, service.description, service.price))
        conn.commit()
        return {"message": "Service added successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/services/")
def read_services(conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services')
    services = cursor.fetchall()
    return {"services": [dict(service) for service in services]}  # Convert rows to dictionaries

@app.get("/services/{service_id}")
def read_service(service_id: int, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services WHERE id = ?', (service_id,))
    service = cursor.fetchone()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return dict(service)  # Convert row to dictionary

@app.put("/services/{service_id}")
def update_service(service_id: int, service: Service, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE services
        SET name = ?, description = ?, price = ?
        WHERE id = ?
    ''', (service.name, service.description, service.price, service_id))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service updated successfully"}

@app.delete("/services/{service_id}")
def delete_service(service_id: int, conn: Connection = Depends(get_db)):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
    conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Service not found")
    return {"message": "Service deleted successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
