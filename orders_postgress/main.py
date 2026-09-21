"""
main.py

E-commerce backend: users, products, orders, order_items - backed by a
real PostgreSQL database on Neon.

Every database call follows the same shape used throughout this course:
open a session, run parameterized SQL with text() and :placeholders,
fetch the result, commit if it was a write, always close() in finally.
"""

from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from database import SessionLocal
from models import UserCreate, ProductCreate, InventoryUpdate, OrderCreate

app = FastAPI(title="E-Commerce API - Neon PostgreSQL")


# =================================================================
# USERS
# =================================================================

@app.post("/users")
def create_user(user: UserCreate):
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                INSERT INTO users (name, email)
                VALUES (:name, :email)
                RETURNING id, name, email, created_at
            """),
            user.model_dump()
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Account created successfully", "user": dict(row._mapping)}

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    finally:
        session.close()


@app.get("/users/{user_id}")
def get_user(user_id: int):
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id})
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="User not found")
        return dict(row._mapping)
    finally:
        session.close()


# =================================================================
# PRODUCTS
# =================================================================

@app.post("/products")
def create_product(product: ProductCreate):
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                INSERT INTO products (name, description, price, stock_quantity, category)
                VALUES (:name, :description, :price, :stock_quantity, :category)
                RETURNING *
            """),
            product.model_dump()
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Product created successfully", "product": dict(row._mapping)}
    finally:
        session.close()


@app.get("/products")
def list_products(category: Optional[str] = Query(default=None)):
    """
    View all products. Uses WHERE (only when a category filter is given)
    and ORDER BY (cheapest first) - both required SQL features for this task.
    """
    session = SessionLocal()
    try:
        if category is not None:
            result = session.execute(
                text("SELECT * FROM products WHERE category = :category ORDER BY price ASC"),
                {"category": category}
            )
        else:
            result = session.execute(text("SELECT * FROM products ORDER BY price ASC"))

        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    finally:
        session.close()


@app.get("/products/{product_id}")
def get_product(product_id: int):
    session = SessionLocal()
    try:
        result = session.execute(text("SELECT * FROM products WHERE id = :id"), {"id": product_id})
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(row._mapping)
    finally:
        session.close()


@app.patch("/products/{product_id}/inventory")
def update_inventory(product_id: int, update: InventoryUpdate):
    """Sets a product's stock_quantity to an exact new number."""
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                UPDATE products SET stock_quantity = :stock_quantity
                WHERE id = :id
                RETURNING *
            """),
            {"stock_quantity": update.stock_quantity, "id": product_id}
        )
        row = result.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        session.commit()
        return {"message": "Inventory updated successfully", "product": dict(row._mapping)}
    finally:
        session.close()


# =================================================================
# ORDERS
# =================================================================

@app.post("/orders")
def place_order(order: OrderCreate):
    """
    Places an order with one or more items.
    For each item: Quantity x Unit Price = Item Total.
    Order Total = Sum of all Item Totals.
    Stock is checked and reduced for every product in the order.
    Nothing is saved (committed) until every single check has passed.
    """
    session = SessionLocal()
    try:
        user = session.execute(
            text("SELECT id FROM users WHERE id = :id"), {"id": order.user_id}
        ).fetchone()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        items_to_insert = []
        order_total = 0.0

        for item in order.items:
            product = session.execute(
                text("SELECT id, price, stock_quantity FROM products WHERE id = :id"),
                {"id": item.product_id}
            ).fetchone()

            if product is None:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough stock for product {item.product_id} "
                           f"(have {product.stock_quantity}, wanted {item.quantity})"
                )

            unit_price = float(product.price)
            item_total = unit_price * item.quantity
            order_total += item_total

            items_to_insert.append({
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "item_total": item_total
            })

        order_row = session.execute(
            text("""
                INSERT INTO orders (user_id, total_amount)
                VALUES (:user_id, :total_amount)
                RETURNING *
            """),
            {"user_id": order.user_id, "total_amount": order_total}
        ).fetchone()
        order_id = order_row.id

        inserted_items = []
        for row in items_to_insert:
            row["order_id"] = order_id
            result = session.execute(
                text("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, item_total)
                    VALUES (:order_id, :product_id, :quantity, :unit_price, :item_total)
                    RETURNING *
                """),
                row
            )
            inserted_items.append(dict(result.fetchone()._mapping))

            session.execute(
                text("UPDATE products SET stock_quantity = stock_quantity - :qty WHERE id = :id"),
                {"qty": row["quantity"], "id": row["product_id"]}
            )

        session.commit()
        return {
            "message": "Order placed successfully",
            "order": dict(order_row._mapping),
            "items": inserted_items
        }

    except HTTPException:
        session.rollback()
        raise

    finally:
        session.close()


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    """
    Shows one order's full detail: the order itself, plus every item in
    it JOINed with the products table so real product names show up,
    not just bare product ID numbers.
    """
    session = SessionLocal()
    try:
        order = session.execute(
            text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}
        ).fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")

        items = session.execute(
            text("""
                SELECT
                    oi.id AS item_id,
                    p.id AS product_id,
                    p.name AS product_name,
                    oi.quantity,
                    oi.unit_price,
                    oi.item_total
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = :order_id
                ORDER BY oi.id
            """),
            {"order_id": order_id}
        ).fetchall()

        return {
            "order": dict(order._mapping),
            "items": [dict(row._mapping) for row in items]
        }
    finally:
        session.close()


@app.get("/users/{user_id}/orders")
def list_user_orders(user_id: int):
    """Every order a user has placed, most recent first."""
    session = SessionLocal()
    try:
        result = session.execute(
            text("SELECT * FROM orders WHERE user_id = :user_id ORDER BY created_at DESC"),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    finally:
        session.close()


@app.get("/users/{user_id}/orders/summary")
def user_orders_summary(user_id: int):
    """
    Demonstrates JOIN + WHERE + GROUP BY + aggregate functions (COUNT, SUM)
    + ORDER BY together: recomputes each order's total straight from its
    order_items, as a live cross-check against the total_amount stored on
    the order itself.
    """
    session = SessionLocal()
    try:
        result = session.execute(
            text("""
                SELECT
                    o.id AS order_id,
                    o.status,
                    COUNT(oi.id) AS item_count,
                    SUM(oi.item_total) AS computed_total,
                    o.total_amount AS stored_total
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                WHERE o.user_id = :user_id
                GROUP BY o.id, o.status, o.total_amount
                ORDER BY o.created_at DESC
            """),
            {"user_id": user_id}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
    finally:
        session.close()


@app.patch("/orders/{order_id}/cancel")
def cancel_order(order_id: int):
    """Cancels an order and gives every item's stock back to the products table."""
    session = SessionLocal()
    try:
        order = session.execute(
            text("SELECT * FROM orders WHERE id = :id"), {"id": order_id}
        ).fetchone()
        if order is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if order.status == "cancelled":
            raise HTTPException(status_code=400, detail="This order is already cancelled")

        items = session.execute(
            text("SELECT product_id, quantity FROM order_items WHERE order_id = :id"),
            {"id": order_id}
        ).fetchall()

        for item in items:
            session.execute(
                text("UPDATE products SET stock_quantity = stock_quantity + :qty WHERE id = :id"),
                {"qty": item.quantity, "id": item.product_id}
            )

        result = session.execute(
            text("UPDATE orders SET status = 'cancelled' WHERE id = :id RETURNING *"),
            {"id": order_id}
        )
        row = result.fetchone()
        session.commit()
        return {"message": "Order cancelled and stock restored", "order": dict(row._mapping)}

    finally:
        session.close()
