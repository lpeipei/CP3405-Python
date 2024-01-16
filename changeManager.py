from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool

app = Flask(__name__)
CORS(app)

# Define your PostgreSQL connection pool
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)

@app.route('/api/update_manager/<id>', methods=['PUT'])
def update_manager(id):
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    try:
        # Get the new manager data from the request body
        new_manager_data = request.json

        # Convert the dictionary to a JSON string
        new_manager_json = json.dumps(new_manager_data)

        # Update the manager field in the database
        cursor.execute('''
            UPDATE company_structure
            SET manager = %s
            WHERE id = %s
        ''', (new_manager_json, id))

        # Commit the changes
        connection.commit()

        return jsonify({"message": "Manager updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        connection_pool.putconn(connection)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
