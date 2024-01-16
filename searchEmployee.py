from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.pool import SimpleConnectionPool

app = Flask(__name__)
CORS(app)

# Initialize your database connection pool
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)

def fetch_employee_by_keyword(cursor, keyword):
    cursor.execute('''
        SELECT id, name, position, department_id
        FROM employee
        WHERE LOWER(name) ILIKE %s OR id ILIKE %s
    ''', (f'%{keyword}%', f'%{keyword}%'))
    results = cursor.fetchall()
    return results

@app.route('/api/employee/search', methods=['GET'])
def search_employee():
    keyword = request.args.get('keyword')
    connection = connection_pool.getconn()
    cursor = connection.cursor()


    try:

        results = fetch_employee_by_keyword(cursor, keyword)
        employees = []
        for result in results:
            employee = {
                'id': result[0],
                'name': result[1],
                'position': result[2],
                'department_id': result[3]
            }
            employees.append(employee)

        return jsonify(employees)
    finally:
        cursor.close()
        connection_pool.putconn(connection)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
