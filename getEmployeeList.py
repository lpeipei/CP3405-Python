from flask import Flask, jsonify, request
from psycopg2.pool import SimpleConnectionPool
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# 设置数据库连接参数
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)


def get_employee_data(keyword, status):
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    if keyword:
      if status == 0:
        # Return all employees matching the keyword
        cursor.execute('SELECT * FROM employee WHERE name ILIKE %s', ('%' + keyword + '%',))
      else:
        # Return employees with the specified status matching the keyword
        cursor.execute('SELECT * FROM employee WHERE name ILIKE %s AND status = %s', ('%' + keyword + '%', status))
    else:
      if status == 0:
        # Return all employees
        cursor.execute('SELECT * FROM employee')
      else:
        # Return employees with the specified status
        cursor.execute('SELECT * FROM employee WHERE status = %s', (status,))

    employee_data = cursor.fetchall()

    connection_pool.putconn(connection)
    return employee_data

@app.route('/api/employee/list', methods=['GET'])
def get_employees():
    try:
        status = int(request.args.get('status', 0))
    except ValueError:
        return jsonify({"error": "Invalid status value"}), 400

    keyword = request.args.get('keyword', '')

    employee_data = get_employee_data(keyword, status)

    employees = []
    for employee in employee_data:
        employee_dict = {
            "id": employee[0],
            "name": employee[1],
            "position": employee[2],
            "mobile": employee[3],
            "status": employee[4],
            "age": employee[5],
            "gender": employee[6],
            "avatar": employee[7],
            "department_id": employee[8],
            "department_name": employee[9]
        }
        employees.append(employee_dict)

    return jsonify(employees)

if __name__ == '__main__':
    app.run(debug=True, port=5006)
