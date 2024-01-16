from flask import Flask, request, jsonify
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Database connection parameters
connection_params = {
    "host": "127.0.0.1",
    "user": "lipeipei",
    "password": "",
    "database": "firstdb"
}

# Function to delete data from company_structure table based on ID
def delete_company_structure_by_id(cursor, employee_id):
    cursor.execute("DELETE FROM employee WHERE id = %s", (employee_id,))

# API endpoint for deleting data from company_structure
@app.route('/api/employee/delete/<employee_id>', methods=['DELETE'])
def delete_company_structure(department_id):
    try:
        # Connect to the database
        with psycopg2.connect(**connection_params) as connection:
            with connection.cursor() as cursor:
                # Delete data from company_structure table
                delete_company_structure_by_id(cursor, department_id)
                connection.commit()

        return jsonify({'message': 'Data deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5016)
