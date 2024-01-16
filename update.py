from flask import Flask, request, jsonify
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import hashlib
from flask_cors import CORS
from psycopg2.extras import Json  # Add this import statement

app = Flask(__name__)
CORS(app)

# Assuming you have a SimpleConnectionPool defined
# Example pool: connection_pool = SimpleConnectionPool(...)
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)
# Other configurations, routes, and definitions...

@app.route('/api/organization/department', methods=['POST'])
def add_edit_department():
    data = request.get_json()

    # Check if the request contains an 'id' field
    department_id = data.get('id')

    if department_id:
        # If 'id' is present, it's an update
        update_department(data, department_id)
        message = f"Department with id {department_id} updated successfully"
    else:
        # If 'id' is not present, it's an add
        add_department(data)
        message = "Department added successfully"

    return jsonify({"message": message})


def add_department(new_department):
    # Assuming connection_pool is a global variable
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        # Generate a unique id and code for the new department
        new_department['id'] = hashlib.md5(new_department['name'].encode()).hexdigest()
        new_department['code'] = new_department['id'][:8]

        # Insert data into the 'company_structure' table
        insert_department(cursor, new_department)
        connection.commit()
    finally:
        cursor.close()
        connection_pool.putconn(connection)

def update_department(updated_department, department_id):
    # Assuming connection_pool is a global variable
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        # Update data in the 'company_structure' table
        update_department_data(cursor, updated_department, department_id)
        connection.commit()
    finally:
        cursor.close()
        connection_pool.putconn(connection)


def insert_department(cursor, department):
    cursor.execute('''
        INSERT INTO company_structure (id, code, name, describe, has_children, number, manager, leader, parent_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
      department['id'],
      department['code'],
      department['name'],
      department.get('describe', ''),
      department.get('has_children', False),
      department.get('number', 0),
      psycopg2.extras.Json(department['manager']),  # Use psycopg2.extras.Json for JSON data
      psycopg2.extras.Json(department['leader']),  # Use psycopg2.extras.Json for JSON data
      department.get('parent_id', '')
    ))


def update_department_data(cursor, updated_department, department_id):
    # Update data in the 'company_structure' table
    cursor.execute('''
        UPDATE company_structure
        SET name = %s, describe = %s, has_children = %s, number = %s, manager = %s, leader = %s, parent_id = %s
        WHERE id = %s
    ''', (
        updated_department.get('name'),
        updated_department.get('describe'),
        updated_department.get('hasChildren', False),
        updated_department.get('number'),
        updated_department.get('manager', {}),
        updated_department.get('leader', {}),
        updated_department.get('parent_id'),
        department_id
    ))

# Your other route handlers...

if __name__ == '__main__':
    app.run(debug=True, port=5004)
