# E-Commerce API — Users, Products, Orders, Order Items (Neon PostgreSQL)

## 1. Set up Neon and create your tables

1. Log into Neon and open the SQL editor.
2. Run the entire contents of `schema.sql` to create `users`, `products`,
   `orders`, and `order_items`, with proper primary keys, foreign keys,
   constraints, and timestamps.

## 2. Set up your `.env` file

```bash
cp .env.example .env
```
Paste your real Neon connection string into `.env`. Never commit the real
`.env` file — `.gitignore` already excludes it.

## 3. Install and run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Open **http://127.0.0.1:8000/docs** to try every endpoint interactively.

## 4. Proving data survives a restart

1. Create a user, a product, and place an order.
2. Confirm it all shows up via `GET /products` and `GET /orders/{id}`.
3. Fully kill the server (not just Ctrl+C-then-instantly-restart — actually
   stop the process, e.g. `pkill -f uvicorn` from a second terminal).
4. Start it again: `uvicorn main:app --reload`.
5. Call `GET /products` and `GET /orders/{id}` again — same data, same
   timestamps. It was never sitting in Python memory — it lived in Neon
   the entire time.

## Database design

- **users**: `id` (PK), `name`, `email` (unique), `created_at`.
- **products**: `id` (PK), `name`, `description`, `price` (checked > 0),
  `stock_quantity` (checked >= 0), `category`, `created_at`.
- **orders**: `id` (PK), `user_id` (FK → `users.id`, `ON DELETE CASCADE`),
  `status` (`placed` or `cancelled`), `total_amount`, `created_at`.
- **order_items**: `id` (PK), `order_id` (FK → `orders.id`,
  `ON DELETE CASCADE`), `product_id` (FK → `products.id`), `quantity`
  (checked > 0), `unit_price` (a price snapshot at order time), `item_total`
  (`quantity x unit_price`).

**Relationships:** one user has many orders. One order has many order
items. One product can appear in many order items (across many different
orders). `order_items` is the junction table connecting orders and
products — this is how one order can contain many products, and one
product can appear in many orders.

## Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/users` | Create an account |
| GET | `/users/{id}` | Get one user |
| POST | `/products` | Create a product |
| GET | `/products` | View products (optional `?category=` filter) |
| GET | `/products/{id}` | Get one product |
| PATCH | `/products/{id}/inventory` | Update a product's stock quantity |
| POST | `/orders` | Place an order (one or more items) |
| GET | `/orders/{id}` | View one order's full detail (joined with product names) |
| GET | `/users/{id}/orders` | View all of a user's orders |
| GET | `/users/{id}/orders/summary` | Aggregate report: item count + computed total per order (JOIN + GROUP BY + SUM/COUNT) |
| PATCH | `/orders/{id}/cancel` | Cancel an order and restock every item |

## SQL features used

- **JOIN**: `GET /orders/{id}` (order_items + products), `GET /users/{id}/orders/summary` (orders + order_items)
- **WHERE**: `GET /products?category=`, every single lookup-by-id endpoint
- **GROUP BY** + **aggregate functions** (`COUNT`, `SUM`): `GET /users/{id}/orders/summary`
- **ORDER BY**: `GET /products` (by price), `GET /users/{id}/orders` (newest first), `GET /users/{id}/orders/summary` (newest first)

## Order total calculation

For every item in an order: `Quantity x Unit Price = Item Total`.
The order's `total_amount` is the sum of every item's `Item Total`.
Both values are calculated in Python at order-creation time (using the
product's *current* price, captured as a snapshot into `unit_price` on
each order item) and then verified independently via the aggregate SQL
`SUM()` in `/users/{id}/orders/summary`, confirmed by testing to always
match exactly.
