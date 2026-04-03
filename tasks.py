"""
SQLArenaEnv Task Library.

50 hand-crafted SQL tasks across 4 difficulty tiers.
Each task includes:
  - A SQLite schema (CREATE TABLE statements)
  - Seed data (INSERT statements)
  - A natural language question
  - A validator function that checks agent's result against correct answer

Difficulty tiers:
  EASY   (10 tasks) — single table, basic SELECT/WHERE/ORDER BY
  MEDIUM (15 tasks) — JOINs, GROUP BY, HAVING, subqueries
  HARD   (15 tasks) — window functions, CTEs, multi-join, aggregation
  EXPERT (10 tasks) — correlated subqueries, recursive CTEs, complex analytics
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class SQLTask:
    task_id: str
    difficulty: str  # easy / medium / hard / expert
    question: str
    schema_sql: str          # CREATE TABLE statements
    seed_sql: str            # INSERT statements
    solution_sql: str        # Reference solution (for generating expected answer)
    schema_description: str  # Human-readable schema hint for agent
    validator: Optional[Callable] = None  # custom validator, None = use default row comparison


# ─────────────────────────────────────────────
# EASY TASKS — single table operations
# ─────────────────────────────────────────────

EASY_TASKS = [
    SQLTask(
        task_id="easy_001",
        difficulty="easy",
        question="List all employees whose salary is greater than 70000, ordered by salary descending.",
        schema_sql="""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary REAL,
    hire_date TEXT
);""",
        seed_sql="""
INSERT INTO employees VALUES
(1,'Alice','Engineering',95000,'2020-01-15'),
(2,'Bob','Marketing',55000,'2019-03-20'),
(3,'Charlie','Engineering',82000,'2021-06-01'),
(4,'Diana','HR',47000,'2018-11-10'),
(5,'Eve','Engineering',110000,'2017-08-25'),
(6,'Frank','Marketing',72000,'2022-02-14'),
(7,'Grace','HR',68000,'2020-09-30'),
(8,'Hank','Engineering',78000,'2019-12-05');""",
        solution_sql="SELECT id, name, department, salary FROM employees WHERE salary > 70000 ORDER BY salary DESC;",
        schema_description="employees(id, name, department, salary, hire_date)",
    ),

    SQLTask(
        task_id="easy_002",
        difficulty="easy",
        question="How many products are there in each category? Show category and count, ordered by count descending.",
        schema_sql="""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);""",
        seed_sql="""
INSERT INTO products VALUES
(1,'Laptop','Electronics',999.99,50),
(2,'Phone','Electronics',699.99,120),
(3,'Desk','Furniture',249.99,30),
(4,'Chair','Furniture',189.99,75),
(5,'Tablet','Electronics',449.99,60),
(6,'Bookshelf','Furniture',129.99,40),
(7,'Headphones','Electronics',149.99,200),
(8,'Lamp','Furniture',59.99,90),
(9,'Monitor','Electronics',399.99,45),
(10,'Keyboard','Electronics',79.99,150);""",
        solution_sql="SELECT category, COUNT(*) as count FROM products GROUP BY category ORDER BY count DESC;",
        schema_description="products(product_id, name, category, price, stock)",
    ),

    SQLTask(
        task_id="easy_003",
        difficulty="easy",
        question="Find the top 5 most expensive products. Show name and price.",
        schema_sql="""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);""",
        seed_sql="""
INSERT INTO products VALUES
(1,'Laptop','Electronics',999.99,50),
(2,'Phone','Electronics',699.99,120),
(3,'Desk','Furniture',249.99,30),
(4,'Chair','Furniture',189.99,75),
(5,'Tablet','Electronics',449.99,60),
(6,'Bookshelf','Furniture',129.99,40),
(7,'Headphones','Electronics',149.99,200),
(8,'Lamp','Furniture',59.99,90),
(9,'Monitor','Electronics',399.99,45),
(10,'Keyboard','Electronics',79.99,150);""",
        solution_sql="SELECT name, price FROM products ORDER BY price DESC LIMIT 5;",
        schema_description="products(product_id, name, category, price, stock)",
    ),

    SQLTask(
        task_id="easy_004",
        difficulty="easy",
        question="Find all students who scored above 85 in Mathematics. Show name and score.",
        schema_sql="""
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    name TEXT,
    subject TEXT,
    score INTEGER,
    grade TEXT
);""",
        seed_sql="""
INSERT INTO students VALUES
(1,'Arjun','Mathematics',92,'A'),
(2,'Priya','Mathematics',78,'B'),
(3,'Rahul','Science',88,'A'),
(4,'Sneha','Mathematics',95,'A'),
(5,'Vikram','Science',72,'C'),
(6,'Ananya','Mathematics',65,'D'),
(7,'Karan','Mathematics',89,'A'),
(8,'Divya','Science',91,'A'),
(9,'Rohit','Mathematics',55,'F'),
(10,'Meera','Mathematics',87,'A');""",
        solution_sql="SELECT name, score FROM students WHERE subject='Mathematics' AND score > 85 ORDER BY score DESC;",
        schema_description="students(student_id, name, subject, score, grade)",
    ),

    SQLTask(
        task_id="easy_005",
        difficulty="easy",
        question="What is the total revenue (price * quantity) from all orders? Return a single number called total_revenue.",
        schema_sql="""
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer TEXT,
    product TEXT,
    price REAL,
    quantity INTEGER,
    order_date TEXT
);""",
        seed_sql="""
INSERT INTO orders VALUES
(1,'Alice','Laptop',999.99,2,'2024-01-10'),
(2,'Bob','Phone',699.99,1,'2024-01-11'),
(3,'Charlie','Tablet',449.99,3,'2024-01-12'),
(4,'Diana','Headphones',149.99,5,'2024-01-13'),
(5,'Eve','Monitor',399.99,1,'2024-01-14'),
(6,'Frank','Keyboard',79.99,4,'2024-01-15'),
(7,'Grace','Laptop',999.99,1,'2024-01-16'),
(8,'Hank','Phone',699.99,2,'2024-01-17');""",
        solution_sql="SELECT ROUND(SUM(price * quantity), 2) as total_revenue FROM orders;",
        schema_description="orders(order_id, customer, product, price, quantity, order_date)",
    ),

    SQLTask(
        task_id="easy_006",
        difficulty="easy",
        question="List all cities that have more than 1 million population, ordered alphabetically.",
        schema_sql="""
CREATE TABLE cities (
    city_id INTEGER PRIMARY KEY,
    name TEXT,
    country TEXT,
    population INTEGER,
    area_km2 REAL
);""",
        seed_sql="""
INSERT INTO cities VALUES
(1,'Mumbai','India',20667656,603.4),
(2,'Delhi','India',32941000,1484.0),
(3,'Kolkata','India',14850000,206.1),
(4,'Chennai','India',10971000,426.0),
(5,'Pune','India',3124000,331.3),
(6,'Hyderabad','India',10534000,650.0),
(7,'Ahmedabad','India',8450000,475.0),
(8,'Jaipur','India',3766000,467.0),
(9,'Surat','India',6936000,326.5),
(10,'Visakhapatnam','India',2035000,681.96);""",
        solution_sql="SELECT name, population FROM cities WHERE population > 1000000 ORDER BY name ASC;",
        schema_description="cities(city_id, name, country, population, area_km2)",
    ),

    SQLTask(
        task_id="easy_007",
        difficulty="easy",
        question="Find the average salary by department. Show department and avg_salary rounded to 2 decimals.",
        schema_sql="""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary REAL,
    hire_date TEXT
);""",
        seed_sql="""
INSERT INTO employees VALUES
(1,'Alice','Engineering',95000,'2020-01-15'),
(2,'Bob','Marketing',55000,'2019-03-20'),
(3,'Charlie','Engineering',82000,'2021-06-01'),
(4,'Diana','HR',47000,'2018-11-10'),
(5,'Eve','Engineering',110000,'2017-08-25'),
(6,'Frank','Marketing',72000,'2022-02-14'),
(7,'Grace','HR',68000,'2020-09-30'),
(8,'Hank','Engineering',78000,'2019-12-05'),
(9,'Ivy','Marketing',61000,'2021-03-15'),
(10,'Jack','HR',52000,'2022-07-01');""",
        solution_sql="SELECT department, ROUND(AVG(salary),2) as avg_salary FROM employees GROUP BY department ORDER BY avg_salary DESC;",
        schema_description="employees(id, name, department, salary, hire_date)",
    ),

    SQLTask(
        task_id="easy_008",
        difficulty="easy",
        question="Find all books published after 2010 with rating above 4.0. Show title, author, and rating.",
        schema_sql="""
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY,
    title TEXT,
    author TEXT,
    year INTEGER,
    rating REAL,
    genre TEXT
);""",
        seed_sql="""
INSERT INTO books VALUES
(1,'The Pragmatic Programmer','Hunt & Thomas',1999,4.8,'Tech'),
(2,'Clean Code','Robert Martin',2008,4.6,'Tech'),
(3,'Thinking Fast and Slow','Daniel Kahneman',2011,4.5,'Psychology'),
(4,'Atomic Habits','James Clear',2018,4.8,'Self-Help'),
(5,'Deep Work','Cal Newport',2016,4.4,'Self-Help'),
(6,'The Lean Startup','Eric Ries',2011,4.2,'Business'),
(7,'Zero to One','Peter Thiel',2014,4.3,'Business'),
(8,'Dune','Frank Herbert',1965,4.7,'Fiction'),
(9,'Project Hail Mary','Andy Weir',2021,4.9,'Fiction'),
(10,'The Midnight Library','Matt Haig',2020,4.2,'Fiction');""",
        solution_sql="SELECT title, author, rating FROM books WHERE year > 2010 AND rating > 4.0 ORDER BY rating DESC;",
        schema_description="books(book_id, title, author, year, rating, genre)",
    ),

    SQLTask(
        task_id="easy_009",
        difficulty="easy",
        question="Count how many employees were hired each year. Show hire_year and count, ordered by year.",
        schema_sql="""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    department TEXT,
    salary REAL,
    hire_date TEXT
);""",
        seed_sql="""
INSERT INTO employees VALUES
(1,'Alice','Engineering',95000,'2020-01-15'),
(2,'Bob','Marketing',55000,'2019-03-20'),
(3,'Charlie','Engineering',82000,'2021-06-01'),
(4,'Diana','HR',47000,'2018-11-10'),
(5,'Eve','Engineering',110000,'2017-08-25'),
(6,'Frank','Marketing',72000,'2022-02-14'),
(7,'Grace','HR',68000,'2020-09-30'),
(8,'Hank','Engineering',78000,'2019-12-05'),
(9,'Ivy','Marketing',61000,'2021-03-15'),
(10,'Jack','HR',52000,'2022-07-01');""",
        solution_sql="SELECT SUBSTR(hire_date,1,4) as hire_year, COUNT(*) as count FROM employees GROUP BY hire_year ORDER BY hire_year;",
        schema_description="employees(id, name, department, salary, hire_date — format YYYY-MM-DD)",
    ),

    SQLTask(
        task_id="easy_010",
        difficulty="easy",
        question="Find the minimum and maximum price for each product category.",
        schema_sql="""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);""",
        seed_sql="""
INSERT INTO products VALUES
(1,'Laptop','Electronics',999.99,50),
(2,'Phone','Electronics',699.99,120),
(3,'Desk','Furniture',249.99,30),
(4,'Chair','Furniture',189.99,75),
(5,'Tablet','Electronics',449.99,60),
(6,'Bookshelf','Furniture',129.99,40),
(7,'Headphones','Electronics',149.99,200),
(8,'Lamp','Furniture',59.99,90),
(9,'Monitor','Electronics',399.99,45),
(10,'Keyboard','Electronics',79.99,150);""",
        solution_sql="SELECT category, MIN(price) as min_price, MAX(price) as max_price FROM products GROUP BY category ORDER BY category;",
        schema_description="products(product_id, name, category, price, stock)",
    ),
]


# ─────────────────────────────────────────────
# MEDIUM TASKS — JOINs, GROUP BY, HAVING
# ─────────────────────────────────────────────

MEDIUM_SCHEMA_ECOMMERCE = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    joined_date TEXT
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    status TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_name TEXT,
    quantity INTEGER,
    unit_price REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);"""

MEDIUM_SEED_ECOMMERCE = """
INSERT INTO customers VALUES
(1,'Arjun Sharma','arjun@email.com','Mumbai','2022-01-15'),
(2,'Priya Patel','priya@email.com','Delhi','2022-03-20'),
(3,'Rahul Gupta','rahul@email.com','Bangalore','2021-11-05'),
(4,'Sneha Reddy','sneha@email.com','Hyderabad','2023-02-10'),
(5,'Vikram Singh','vikram@email.com','Chennai','2021-08-25'),
(6,'Ananya Joshi','ananya@email.com','Pune','2022-07-14'),
(7,'Karan Mehta','karan@email.com','Mumbai','2023-01-30'),
(8,'Divya Nair','divya@email.com','Bangalore','2022-05-18');

INSERT INTO orders VALUES
(101,1,'2024-01-10','completed'),
(102,1,'2024-02-15','completed'),
(103,2,'2024-01-20','completed'),
(104,3,'2024-01-25','pending'),
(105,3,'2024-02-28','completed'),
(106,4,'2024-03-05','completed'),
(107,5,'2024-01-08','cancelled'),
(108,5,'2024-03-12','completed'),
(109,6,'2024-02-20','completed'),
(110,7,'2024-03-01','pending'),
(111,8,'2024-01-30','completed'),
(112,8,'2024-02-25','completed');

INSERT INTO order_items VALUES
(1,101,'Laptop',1,999.99),
(2,101,'Mouse',2,29.99),
(3,102,'Phone',1,699.99),
(4,103,'Tablet',2,449.99),
(5,104,'Headphones',3,149.99),
(6,105,'Monitor',1,399.99),
(7,106,'Keyboard',2,79.99),
(8,107,'Laptop',1,999.99),
(9,108,'Phone',1,699.99),
(10,109,'Desk',1,249.99),
(11,110,'Chair',2,189.99),
(12,111,'Laptop',1,999.99),
(13,111,'Tablet',1,449.99),
(14,112,'Headphones',2,149.99);"""

MEDIUM_SCHEMA_HR = """
CREATE TABLE departments (
    dept_id INTEGER PRIMARY KEY,
    dept_name TEXT,
    manager_id INTEGER,
    budget REAL
);
CREATE TABLE employees (
    emp_id INTEGER PRIMARY KEY,
    name TEXT,
    dept_id INTEGER,
    salary REAL,
    hire_date TEXT,
    manager_id INTEGER,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
);"""

MEDIUM_SEED_HR = """
INSERT INTO departments VALUES
(1,'Engineering',5,5000000),
(2,'Marketing',8,2000000),
(3,'HR',12,1500000),
(4,'Finance',15,3000000),
(5,'Operations',18,2500000);

INSERT INTO employees VALUES
(1,'Alice Chen',1,95000,'2020-01-15',5),
(2,'Bob Kumar',1,82000,'2021-06-01',5),
(3,'Charlie Roy',1,78000,'2019-12-05',5),
(4,'Diana Shah',2,72000,'2022-02-14',8),
(5,'Eve Patel',1,110000,'2017-08-25',NULL),
(6,'Frank Joshi',2,55000,'2019-03-20',8),
(7,'Grace Singh',3,68000,'2020-09-30',12),
(8,'Hank Mehta',2,88000,'2018-06-15',NULL),
(9,'Ivy Reddy',3,52000,'2022-07-01',12),
(10,'Jack Nair',3,47000,'2018-11-10',12),
(11,'Kara Gupta',4,91000,'2019-04-22',15),
(12,'Leo Sharma',3,75000,'2016-03-10',NULL),
(13,'Mia Verma',4,83000,'2020-08-14',15),
(14,'Nia Bose',5,69000,'2021-01-20',18),
(15,'Omar Das',4,102000,'2015-11-30',NULL),
(16,'Pia Iyer',5,61000,'2022-03-25',18),
(17,'Quinn Rao',1,74000,'2021-09-08',5),
(18,'Rita Pillai',5,95000,'2016-07-12',NULL);"""

MEDIUM_TASKS = [
    SQLTask(
        task_id="medium_001",
        difficulty="medium",
        question="Find customers who have placed more than 1 completed order. Show customer name and order count.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT c.name, COUNT(o.order_id) as order_count
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) > 1
ORDER BY order_count DESC;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_002",
        difficulty="medium",
        question="Calculate total spending per customer (only completed orders). Show customer name and total_spent, ordered by total_spent descending.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT c.name, ROUND(SUM(oi.quantity * oi.unit_price), 2) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'completed'
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_003",
        difficulty="medium",
        question="Find the most popular product (by total quantity sold across all completed orders).",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT oi.product_name, SUM(oi.quantity) as total_sold
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY oi.product_name
ORDER BY total_sold DESC
LIMIT 1;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_004",
        difficulty="medium",
        question="Find departments where average salary exceeds 80000. Show dept_name and avg_salary.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT d.dept_name, ROUND(AVG(e.salary), 2) as avg_salary
FROM departments d
JOIN employees e ON d.dept_id = e.dept_id
GROUP BY d.dept_id, d.dept_name
HAVING AVG(e.salary) > 80000
ORDER BY avg_salary DESC;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_005",
        difficulty="medium",
        question="For each department, find the highest-paid employee. Show dept_name, employee name, and salary.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT d.dept_name, e.name, e.salary
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE e.salary = (
    SELECT MAX(e2.salary) FROM employees e2 WHERE e2.dept_id = e.dept_id
)
ORDER BY e.salary DESC;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_006",
        difficulty="medium",
        question="List customers from Mumbai or Bangalore who have at least one order. Show name and city.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT DISTINCT c.name, c.city
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.city IN ('Mumbai','Bangalore')
ORDER BY c.city, c.name;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_007",
        difficulty="medium",
        question="Find employees who earn more than their department's average salary. Show name, salary, and dept_name.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT e.name, e.salary, d.dept_name
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE e.salary > (
    SELECT AVG(e2.salary) FROM employees e2 WHERE e2.dept_id = e.dept_id
)
ORDER BY d.dept_name, e.salary DESC;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_008",
        difficulty="medium",
        question="Calculate the cancellation rate per customer (cancelled orders / total orders). Show only customers with cancellation rate > 0. Show name and cancellation_rate rounded to 2 decimals.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT c.name,
       ROUND(CAST(SUM(CASE WHEN o.status='cancelled' THEN 1 ELSE 0 END) AS REAL) / COUNT(o.order_id), 2) as cancellation_rate
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING SUM(CASE WHEN o.status='cancelled' THEN 1 ELSE 0 END) > 0
ORDER BY cancellation_rate DESC;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_009",
        difficulty="medium",
        question="Find total salary cost per department and what percentage of total company salary each dept represents. Show dept_name, total_salary, salary_pct rounded to 1 decimal.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT d.dept_name,
       SUM(e.salary) as total_salary,
       ROUND(SUM(e.salary) * 100.0 / (SELECT SUM(salary) FROM employees), 1) as salary_pct
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
GROUP BY d.dept_id, d.dept_name
ORDER BY total_salary DESC;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_010",
        difficulty="medium",
        question="Find orders placed in January 2024. Show customer name, order_date, and order total (sum of quantity*unit_price).",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT c.name, o.order_date, ROUND(SUM(oi.quantity * oi.unit_price),2) as order_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date LIKE '2024-01%'
GROUP BY o.order_id, c.name, o.order_date
ORDER BY o.order_date;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_011",
        difficulty="medium",
        question="Which product has generated the most revenue across all completed orders? Show product_name and total_revenue.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT oi.product_name, ROUND(SUM(oi.quantity * oi.unit_price),2) as total_revenue
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY oi.product_name
ORDER BY total_revenue DESC
LIMIT 1;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),

    SQLTask(
        task_id="medium_012",
        difficulty="medium",
        question="Find employees who have been at the company for more than 4 years (hired before 2021). Show name, hire_date, and dept_name.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT e.name, e.hire_date, d.dept_name
FROM employees e
JOIN departments d ON e.dept_id = d.dept_id
WHERE e.hire_date < '2021-01-01'
ORDER BY e.hire_date;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_013",
        difficulty="medium",
        question="Find the second highest salary in the company (single value, call it second_highest_salary).",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT MAX(salary) as second_highest_salary
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id)",
    ),

    SQLTask(
        task_id="medium_014",
        difficulty="medium",
        question="Count the number of employees per manager (only show managers with 2+ direct reports). Show manager name and report_count.",
        schema_sql=MEDIUM_SCHEMA_HR,
        seed_sql=MEDIUM_SEED_HR,
        solution_sql="""
SELECT m.name as manager_name, COUNT(e.emp_id) as report_count
FROM employees e
JOIN employees m ON e.manager_id = m.emp_id
GROUP BY m.emp_id, m.name
HAVING COUNT(e.emp_id) >= 2
ORDER BY report_count DESC;""",
        schema_description="departments(dept_id, dept_name, manager_id, budget), employees(emp_id, name, dept_id, salary, hire_date, manager_id) — manager_id refers to emp_id of the manager",
    ),

    SQLTask(
        task_id="medium_015",
        difficulty="medium",
        question="Find customers who have never placed an order. Show their name and email.",
        schema_sql=MEDIUM_SCHEMA_ECOMMERCE,
        seed_sql=MEDIUM_SEED_ECOMMERCE,
        solution_sql="""
SELECT c.name, c.email
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.name;""",
        schema_description="customers(customer_id, name, email, city, joined_date), orders(order_id, customer_id, order_date, status), order_items(item_id, order_id, product_name, quantity, unit_price)",
    ),
]


# ─────────────────────────────────────────────
# HARD TASKS — CTEs, Window Functions
# ─────────────────────────────────────────────

HARD_SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT, city TEXT, segment TEXT
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date TEXT,
    ship_date TEXT,
    category TEXT,
    amount REAL
);
CREATE TABLE returns (
    return_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    return_date TEXT,
    reason TEXT
);"""

HARD_SEED = """
INSERT INTO customers VALUES
(1,'Arjun','Mumbai','Consumer'),
(2,'Priya','Delhi','Corporate'),
(3,'Rahul','Bangalore','Consumer'),
(4,'Sneha','Hyderabad','Corporate'),
(5,'Vikram','Chennai','Home Office'),
(6,'Ananya','Pune','Consumer'),
(7,'Karan','Mumbai','Corporate'),
(8,'Divya','Bangalore','Consumer');

INSERT INTO orders VALUES
(1001,1,'2023-01-10','2023-01-15','Technology',2500.00),
(1002,1,'2023-03-20','2023-03-25','Furniture',1200.00),
(1003,1,'2023-06-15','2023-06-20','Technology',3800.00),
(1004,2,'2023-02-05','2023-02-10','Office Supplies',450.00),
(1005,2,'2023-04-18','2023-04-23','Technology',5200.00),
(1006,2,'2023-07-30','2023-08-04','Furniture',890.00),
(1007,3,'2023-01-25','2023-01-30','Technology',1100.00),
(1008,3,'2023-05-12','2023-05-17','Office Supplies',320.00),
(1009,4,'2023-03-08','2023-03-13','Furniture',2200.00),
(1010,4,'2023-08-22','2023-08-27','Technology',4100.00),
(1011,5,'2023-02-14','2023-02-19','Office Supplies',180.00),
(1012,5,'2023-06-28','2023-07-03','Technology',2900.00),
(1013,6,'2023-01-05','2023-01-10','Furniture',750.00),
(1014,6,'2023-04-25','2023-04-30','Office Supplies',290.00),
(1015,7,'2023-03-15','2023-03-20','Technology',6800.00),
(1016,7,'2023-07-10','2023-07-15','Furniture',1500.00),
(1017,8,'2023-02-28','2023-03-05','Technology',3200.00),
(1018,8,'2023-05-20','2023-05-25','Office Supplies',410.00);

INSERT INTO returns VALUES
(1,1002,'2023-04-01','Defective'),
(2,1004,'2023-02-20','Wrong item'),
(3,1008,'2023-05-25','Not needed'),
(4,1011,'2023-02-25','Defective'),
(5,1013,'2023-01-20','Wrong item');"""

HARD_TASKS = [
    SQLTask(
        task_id="hard_001",
        difficulty="hard",
        question="Using a window function, rank customers by their total order amount within each city segment. Show customer name, city, total_amount, and their rank within city.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT c.name, c.city,
       SUM(o.amount) as total_amount,
       RANK() OVER (PARTITION BY c.city ORDER BY SUM(o.amount) DESC) as city_rank
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.city
ORDER BY c.city, city_rank;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_002",
        difficulty="hard",
        question="Using a CTE, find the running total of order amounts for each customer ordered by order_date. Show customer name, order_date, amount, and running_total.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH customer_orders AS (
    SELECT c.name, o.order_date, o.amount,
           SUM(o.amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as running_total
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
)
SELECT name, order_date, amount, running_total
FROM customer_orders
ORDER BY name, order_date;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_003",
        difficulty="hard",
        question="Find the return rate by category (returned orders / total orders). Show category and return_rate as a percentage rounded to 1 decimal.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT o.category,
       ROUND(COUNT(r.return_id) * 100.0 / COUNT(o.order_id), 1) as return_rate
FROM orders o
LEFT JOIN returns r ON o.order_id = r.order_id
GROUP BY o.category
ORDER BY return_rate DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_004",
        difficulty="hard",
        question="For each customer, find the month with their highest single order amount. Show customer name, best_month (YYYY-MM format), and max_amount.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH monthly_max AS (
    SELECT c.name, SUBSTR(o.order_date,1,7) as month, MAX(o.amount) as max_amount,
           RANK() OVER (PARTITION BY c.customer_id ORDER BY MAX(o.amount) DESC) as rnk
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, month
)
SELECT name, month as best_month, max_amount
FROM monthly_max
WHERE rnk = 1
ORDER BY max_amount DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_005",
        difficulty="hard",
        question="Calculate average shipping time (days between order_date and ship_date) per category. Show category and avg_ship_days rounded to 1 decimal.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT category,
       ROUND(AVG(julianday(ship_date) - julianday(order_date)), 1) as avg_ship_days
FROM orders
GROUP BY category
ORDER BY avg_ship_days;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_006",
        difficulty="hard",
        question="Find customers whose total order value in Technology exceeds their total in all other categories combined. Show customer name, tech_total, and other_total.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH category_totals AS (
    SELECT c.customer_id, c.name,
           SUM(CASE WHEN o.category='Technology' THEN o.amount ELSE 0 END) as tech_total,
           SUM(CASE WHEN o.category!='Technology' THEN o.amount ELSE 0 END) as other_total
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
)
SELECT name, tech_total, other_total
FROM category_totals
WHERE tech_total > other_total
ORDER BY tech_total DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_007",
        difficulty="hard",
        question="Using LAG window function, for each customer show each order amount and the difference from their previous order amount. Show name, order_date, amount, prev_amount, and amount_change.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT c.name, o.order_date, o.amount,
       LAG(o.amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as prev_amount,
       o.amount - LAG(o.amount) OVER (PARTITION BY c.customer_id ORDER BY o.order_date) as amount_change
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.name, o.order_date;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_008",
        difficulty="hard",
        question="Identify the top 2 customers by total order amount in each customer segment. Show segment, customer name, total_amount, and rank within segment.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH ranked AS (
    SELECT c.segment, c.name,
           SUM(o.amount) as total_amount,
           RANK() OVER (PARTITION BY c.segment ORDER BY SUM(o.amount) DESC) as rnk
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.segment, c.name
)
SELECT segment, name, total_amount, rnk
FROM ranked
WHERE rnk <= 2
ORDER BY segment, rnk;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_009",
        difficulty="hard",
        question="Find the percentage of total revenue contributed by each customer. Show name and revenue_pct rounded to 2 decimals, ordered by pct descending.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT c.name,
       ROUND(SUM(o.amount) * 100.0 / (SELECT SUM(amount) FROM orders), 2) as revenue_pct
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY revenue_pct DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_010",
        difficulty="hard",
        question="For each category, show total revenue, average order size, and count of unique customers who ordered in that category.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT o.category,
       ROUND(SUM(o.amount), 2) as total_revenue,
       ROUND(AVG(o.amount), 2) as avg_order_size,
       COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
GROUP BY o.category
ORDER BY total_revenue DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_011",
        difficulty="hard",
        question="Find customers who have ordered in ALL three categories (Technology, Furniture, Office Supplies). Show customer name.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT c.name
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.category IN ('Technology','Furniture','Office Supplies')
GROUP BY c.customer_id, c.name
HAVING COUNT(DISTINCT o.category) = 3
ORDER BY c.name;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_012",
        difficulty="hard",
        question="For each order, show the order amount as a percentile rank (0 to 1) among all orders. Show order_id, amount, and percentile_rank rounded to 2 decimals.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT order_id, amount,
       ROUND(PERCENT_RANK() OVER (ORDER BY amount), 2) as percentile_rank
FROM orders
ORDER BY amount;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_013",
        difficulty="hard",
        question="Find orders where the shipping time was above the average shipping time for their category. Show order_id, category, ship_days, and category_avg_days (both rounded to 1 decimal).",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH ship_times AS (
    SELECT order_id, category,
           ROUND(julianday(ship_date) - julianday(order_date), 1) as ship_days,
           ROUND(AVG(julianday(ship_date) - julianday(order_date)) OVER (PARTITION BY category), 1) as category_avg_days
    FROM orders
)
SELECT order_id, category, ship_days, category_avg_days
FROM ship_times
WHERE ship_days > category_avg_days
ORDER BY ship_days DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_014",
        difficulty="hard",
        question="Find the first and last order date for each customer, and number of days between them (customer tenure in days). Show name, first_order, last_order, tenure_days.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
SELECT c.name,
       MIN(o.order_date) as first_order,
       MAX(o.order_date) as last_order,
       CAST(julianday(MAX(o.order_date)) - julianday(MIN(o.order_date)) AS INTEGER) as tenure_days
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY tenure_days DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),

    SQLTask(
        task_id="hard_015",
        difficulty="hard",
        question="Using a CTE, find customers with above-average order count AND above-average total spend. Show name, order_count, and total_spend.",
        schema_sql=HARD_SCHEMA,
        seed_sql=HARD_SEED,
        solution_sql="""
WITH customer_stats AS (
    SELECT c.customer_id, c.name,
           COUNT(o.order_id) as order_count,
           SUM(o.amount) as total_spend
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
),
averages AS (
    SELECT AVG(order_count) as avg_orders, AVG(total_spend) as avg_spend
    FROM customer_stats
)
SELECT cs.name, cs.order_count, cs.total_spend
FROM customer_stats cs, averages
WHERE cs.order_count > averages.avg_orders
  AND cs.total_spend > averages.avg_spend
ORDER BY cs.total_spend DESC;""",
        schema_description="customers(customer_id, name, city, segment), orders(order_id, customer_id, order_date, ship_date, category, amount), returns(return_id, order_id, return_date, reason)",
    ),
]


# ─────────────────────────────────────────────
# EXPERT TASKS — Correlated subqueries, complex analytics
# ─────────────────────────────────────────────

EXPERT_SCHEMA = """
CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY,
    holder_name TEXT,
    account_type TEXT,
    city TEXT,
    opened_date TEXT,
    balance REAL
);
CREATE TABLE transactions (
    txn_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    txn_date TEXT,
    txn_type TEXT,
    amount REAL,
    category TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY,
    account_id INTEGER,
    loan_type TEXT,
    principal REAL,
    interest_rate REAL,
    start_date TEXT,
    status TEXT,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);"""

EXPERT_SEED = """
INSERT INTO accounts VALUES
(1,'Arjun Sharma','Savings','Mumbai','2018-03-15',125000.00),
(2,'Priya Patel','Current','Delhi','2016-07-22',450000.00),
(3,'Rahul Gupta','Savings','Bangalore','2020-01-10',78000.00),
(4,'Sneha Reddy','Current','Hyderabad','2015-11-30',890000.00),
(5,'Vikram Singh','Savings','Chennai','2019-05-14',42000.00),
(6,'Ananya Joshi','Savings','Pune','2021-08-09',195000.00),
(7,'Karan Mehta','Current','Mumbai','2017-02-28',320000.00),
(8,'Divya Nair','Savings','Bangalore','2022-04-17',55000.00);

INSERT INTO transactions VALUES
(1,1,'2024-01-05','credit',50000,'salary'),
(2,1,'2024-01-12','debit',15000,'rent'),
(3,1,'2024-01-20','debit',8000,'groceries'),
(4,1,'2024-02-05','credit',50000,'salary'),
(5,1,'2024-02-18','debit',22000,'utilities'),
(6,2,'2024-01-08','credit',200000,'business'),
(7,2,'2024-01-15','debit',80000,'supplier'),
(8,2,'2024-01-28','debit',45000,'rent'),
(9,2,'2024-02-10','credit',175000,'business'),
(10,2,'2024-02-22','debit',60000,'supplier'),
(11,3,'2024-01-10','credit',45000,'salary'),
(12,3,'2024-01-25','debit',12000,'rent'),
(13,3,'2024-02-10','credit',45000,'salary'),
(14,3,'2024-02-20','debit',18000,'utilities'),
(15,4,'2024-01-03','credit',500000,'business'),
(16,4,'2024-01-20','debit',200000,'investment'),
(17,4,'2024-02-05','credit',480000,'business'),
(18,4,'2024-02-25','debit',150000,'supplier'),
(19,5,'2024-01-15','credit',38000,'salary'),
(20,5,'2024-01-30','debit',15000,'rent'),
(21,6,'2024-01-08','credit',85000,'salary'),
(22,6,'2024-01-22','debit',25000,'rent'),
(23,6,'2024-02-08','credit',85000,'salary'),
(24,6,'2024-02-20','debit',30000,'investment'),
(25,7,'2024-01-12','credit',150000,'business'),
(26,7,'2024-01-28','debit',75000,'supplier'),
(27,7,'2024-02-15','credit',160000,'business'),
(28,8,'2024-01-18','credit',52000,'salary'),
(29,8,'2024-02-18','credit',52000,'salary'),
(30,8,'2024-02-25','debit',20000,'rent');

INSERT INTO loans VALUES
(1,1,'Home Loan',2500000,8.5,'2020-06-15','active'),
(2,2,'Business Loan',5000000,10.2,'2019-03-20','active'),
(3,3,'Personal Loan',150000,14.5,'2022-08-10','active'),
(4,5,'Vehicle Loan',800000,9.8,'2021-12-05','active'),
(5,6,'Home Loan',3500000,8.2,'2022-09-15','active'),
(6,7,'Business Loan',2000000,11.5,'2018-04-22','closed'),
(7,8,'Personal Loan',100000,15.2,'2023-01-30','active');"""

EXPERT_TASKS = [
    SQLTask(
        task_id="expert_001",
        difficulty="expert",
        question="For each account, calculate the net cash flow (total credits minus total debits) per month in 2024. Show holder_name, month (YYYY-MM), and net_flow. Order by holder_name, month.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.holder_name,
       SUBSTR(t.txn_date,1,7) as month,
       ROUND(SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE -t.amount END), 2) as net_flow
FROM accounts a
JOIN transactions t ON a.account_id = t.account_id
WHERE t.txn_date LIKE '2024%'
GROUP BY a.account_id, a.holder_name, month
ORDER BY a.holder_name, month;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_002",
        difficulty="expert",
        question="Find accounts where the total loan principal exceeds 5x their current account balance. Show holder_name, balance, total_loan_principal, and the ratio (rounded to 2 decimals).",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.holder_name, a.balance,
       SUM(l.principal) as total_loan_principal,
       ROUND(SUM(l.principal) / a.balance, 2) as debt_to_balance_ratio
FROM accounts a
JOIN loans l ON a.account_id = l.account_id
WHERE l.status = 'active'
GROUP BY a.account_id, a.holder_name, a.balance
HAVING SUM(l.principal) > 5 * a.balance
ORDER BY debt_to_balance_ratio DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_003",
        difficulty="expert",
        question="Using a CTE chain, find the top spending category per account (by total debit amount). Show holder_name, top_category, and category_spend.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
WITH category_spend AS (
    SELECT a.account_id, a.holder_name, t.category,
           SUM(t.amount) as spend,
           RANK() OVER (PARTITION BY a.account_id ORDER BY SUM(t.amount) DESC) as rnk
    FROM accounts a
    JOIN transactions t ON a.account_id = t.account_id
    WHERE t.txn_type = 'debit'
    GROUP BY a.account_id, a.holder_name, t.category
)
SELECT holder_name, category as top_category, spend as category_spend
FROM category_spend
WHERE rnk = 1
ORDER BY category_spend DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_004",
        difficulty="expert",
        question="Calculate the estimated annual interest cost for each active loan. Show holder_name, loan_type, principal, interest_rate, and annual_interest_cost (principal * interest_rate / 100), ordered by annual_interest_cost descending.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.holder_name, l.loan_type, l.principal, l.interest_rate,
       ROUND(l.principal * l.interest_rate / 100, 2) as annual_interest_cost
FROM accounts a
JOIN loans l ON a.account_id = l.account_id
WHERE l.status = 'active'
ORDER BY annual_interest_cost DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_005",
        difficulty="expert",
        question="For each city, calculate the average account balance, total transaction volume, and number of active loans. Show city, avg_balance, total_txn_volume, and active_loan_count.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.city,
       ROUND(AVG(a.balance), 2) as avg_balance,
       ROUND(SUM(t.amount), 2) as total_txn_volume,
       COUNT(DISTINCT l.loan_id) as active_loan_count
FROM accounts a
LEFT JOIN transactions t ON a.account_id = t.account_id
LEFT JOIN loans l ON a.account_id = l.account_id AND l.status = 'active'
GROUP BY a.city
ORDER BY avg_balance DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_006",
        difficulty="expert",
        question="Find accounts that received salary credits in both January and February 2024. Show holder_name.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.holder_name
FROM accounts a
WHERE EXISTS (
    SELECT 1 FROM transactions t
    WHERE t.account_id = a.account_id
      AND t.txn_type = 'credit'
      AND t.category = 'salary'
      AND t.txn_date LIKE '2024-01%'
)
AND EXISTS (
    SELECT 1 FROM transactions t
    WHERE t.account_id = a.account_id
      AND t.txn_type = 'credit'
      AND t.category = 'salary'
      AND t.txn_date LIKE '2024-02%'
)
ORDER BY a.holder_name;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_007",
        difficulty="expert",
        question="Calculate savings rate for each salary earner: (total_credits - total_debits) / total_credits. Show holder_name and savings_rate as percentage rounded to 1 decimal. Only include accounts with salary transactions.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
WITH flows AS (
    SELECT a.account_id, a.holder_name,
           SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE 0 END) as total_credits,
           SUM(CASE WHEN t.txn_type='debit' THEN t.amount ELSE 0 END) as total_debits
    FROM accounts a
    JOIN transactions t ON a.account_id = t.account_id
    GROUP BY a.account_id, a.holder_name
)
SELECT f.holder_name,
       ROUND((f.total_credits - f.total_debits) * 100.0 / f.total_credits, 1) as savings_rate
FROM flows f
WHERE f.account_id IN (
    SELECT DISTINCT account_id FROM transactions WHERE category = 'salary'
)
ORDER BY savings_rate DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_008",
        difficulty="expert",
        question="Find the account with the highest transaction frequency (most transactions per month on average). Show holder_name, total_transactions, months_active (distinct months with transactions), and avg_txn_per_month rounded to 2 decimals.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
SELECT a.holder_name,
       COUNT(t.txn_id) as total_transactions,
       COUNT(DISTINCT SUBSTR(t.txn_date,1,7)) as months_active,
       ROUND(CAST(COUNT(t.txn_id) AS REAL) / COUNT(DISTINCT SUBSTR(t.txn_date,1,7)), 2) as avg_txn_per_month
FROM accounts a
JOIN transactions t ON a.account_id = t.account_id
GROUP BY a.account_id, a.holder_name
ORDER BY avg_txn_per_month DESC
LIMIT 1;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_009",
        difficulty="expert",
        question="Identify accounts that have both an active loan AND whose total debits in 2024 exceed their total credits in 2024 (cash flow negative). Show holder_name, net_flow_2024, and total_active_loan_principal.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
WITH cash_flow AS (
    SELECT account_id,
           SUM(CASE WHEN txn_type='credit' THEN amount ELSE -amount END) as net_flow
    FROM transactions
    WHERE txn_date LIKE '2024%'
    GROUP BY account_id
),
active_loans AS (
    SELECT account_id, SUM(principal) as total_principal
    FROM loans WHERE status='active'
    GROUP BY account_id
)
SELECT a.holder_name, ROUND(cf.net_flow, 2) as net_flow_2024, al.total_principal
FROM accounts a
JOIN cash_flow cf ON a.account_id = cf.account_id
JOIN active_loans al ON a.account_id = al.account_id
WHERE cf.net_flow < 0
ORDER BY cf.net_flow;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),

    SQLTask(
        task_id="expert_010",
        difficulty="expert",
        question="Create a financial health score for each account: score = (balance/100000)*40 + (net_credits_2024/50000)*40 - (active_loan_principal/1000000)*20, capped between 0 and 100. Show holder_name and health_score rounded to 1 decimal, ordered by score descending.",
        schema_sql=EXPERT_SCHEMA,
        seed_sql=EXPERT_SEED,
        solution_sql="""
WITH metrics AS (
    SELECT a.account_id, a.holder_name, a.balance,
           COALESCE(SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE 0 END), 0) as net_credits,
           COALESCE((SELECT SUM(principal) FROM loans l WHERE l.account_id=a.account_id AND l.status='active'), 0) as loan_principal
    FROM accounts a
    LEFT JOIN transactions t ON a.account_id = t.account_id AND t.txn_date LIKE '2024%'
    GROUP BY a.account_id, a.holder_name, a.balance
)
SELECT holder_name,
       ROUND(MIN(100, MAX(0,
           (balance/100000.0)*40 +
           (net_credits/50000.0)*40 -
           (loan_principal/1000000.0)*20
       )), 1) as health_score
FROM metrics
ORDER BY health_score DESC;""",
        schema_description="accounts(account_id, holder_name, account_type, city, opened_date, balance), transactions(txn_id, account_id, txn_date, txn_type[credit/debit], amount, category), loans(loan_id, account_id, loan_type, principal, interest_rate, start_date, status)",
    ),
]


# ─────────────────────────────────────────────
# Task registry
# ─────────────────────────────────────────────

ALL_TASKS: Dict[str, SQLTask] = {}
for _t in EASY_TASKS + MEDIUM_TASKS + HARD_TASKS + EXPERT_TASKS:
    ALL_TASKS[_t.task_id] = _t

TASKS_BY_DIFFICULTY: Dict[str, List[SQLTask]] = {
    "easy": EASY_TASKS,
    "medium": MEDIUM_TASKS,
    "hard": HARD_TASKS,
    "expert": EXPERT_TASKS,
}

def get_task(task_id: str) -> Optional[SQLTask]:
    return ALL_TASKS.get(task_id)

def get_tasks_by_difficulty(difficulty: str) -> List[SQLTask]:
    return TASKS_BY_DIFFICULTY.get(difficulty, [])