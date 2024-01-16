from flask import Flask, request, jsonify
import psycopg2
import uuid
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

# Database connection parameters
connection_params = {
  "host": "127.0.0.1",
  "user": "lipeipei",
  "password": "",
  "database": "firstdb"
}

def check_unique_code(cursor, code):
  cursor.execute("SELECT COUNT(*) FROM position WHERE code = %s", (code,))
  count = cursor.fetchone()[0]
  return count == 0

def generate_unique_hash(data):
    # Convert data to bytes
    data_bytes = str(data).encode('utf-8')

    # Generate MD5 hash
    md5_hash = hashlib.md5(data_bytes).hexdigest()

    return md5_hash


def insert_position(cursor, position_data):
    # Generate a unique ID for the position
    position_id = generate_unique_hash(position_data)

    # Extract values from position_data
    name = position_data['name']
    salary = position_data['salary']
    code = position_data['code']
    description = position_data.get('description', '')  # Handle the case where description might be missing
    department_id = position_data['department_id']
    department_name = position_data['department_name']

    print(position_id, name, salary, code, description, department_id, department_name)
    # Insert data into the position table
    cursor.execute('''
              INSERT INTO position (id, name, salary, code, description, department_id, department_name)
              VALUES (%s, %s, %s, %s, %s, %s, %s)
          ''', (position_id, name, salary, code, description, department_id, department_name))

    return position_id


def update_employees_count(cursor, department_id):
  # Update the employees count in the company_structure table
  cursor.execute('''
        UPDATE company_structure
        SET employees = employees + 1
        WHERE id = %s
    ''', (department_id,))

@app.route('/api/position/add', methods=['POST'])
def add_position():
    try:
      data = request.json
      name = data.get('name')
      code = data.get('code')
      department_id = data['department']['id']
      department_name = data['department']['name']
      salary = data.get('salary')
      description = data.get('description')
      # Validate code uniqueness
      with psycopg2.connect(**connection_params) as connection:
        with connection.cursor() as cursor:
          if not check_unique_code(cursor, code):
            return jsonify({'error': 'Code must be unique'}), 400

      # Insert data into the position table
      with psycopg2.connect(**connection_params) as connection:
        with connection.cursor() as cursor:
          position_id = insert_position(cursor, {
              'name': name,
              'salary': salary,
              'code': code,
              'description': description,
              'department_id': department_id,
              'department_name': department_name
          })
          print(name, salary, code, description, department_id, department_name)
          # update_employees_count(cursor, department_id)

          connection.commit()

      return jsonify({'position_id': position_id}), 200

    except Exception as e:
        return jsonify({'error11': str(e)}), 500


# 连接到数据库
connection = psycopg2.connect(**connection_params)
cursor = connection.cursor()

# 创建 position 表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS position (
        id TEXT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        salary INTEGER,
        code VARCHAR(255),
        description TEXT,
        department_id TEXT REFERENCES company_structure(id),
        department_name TEXT REFERENCES company_structure(name)
    )
''')

# 提交更改并关闭连接
connection.commit()
cursor.close()
connection.close()
if __name__ == '__main__':
  app.run(debug=True, port=5011)
