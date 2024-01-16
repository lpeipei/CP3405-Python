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

def update_position(cursor, position_id, new_data):
    cursor.execute('''
        UPDATE position
        SET name = %s, salary = %s, code = %s, description = %s, department_id = %s, department_name = %s
        WHERE id = %s
    ''', (new_data['name'], new_data['salary'], new_data['code'], new_data['description'],
          new_data['department']['id'], new_data['department']['name'], position_id))

def fetch_position(cursor, position_id):
    cursor.execute('''
        SELECT * FROM position
        WHERE id = %s
    ''', (position_id,))
    return cursor.fetchone()

@app.route('/api/position/edit/<position_id>', methods=['PUT'])
def edit_position(position_id):
    try:
        new_data = request.json

        with psycopg2.connect(**connection_params) as connection:
            with connection.cursor() as cursor:
                # Check if the position with the given ID exists
                existing_position = fetch_position(cursor, position_id)
                if not existing_position:
                    return jsonify({'error': 'Position not found'}), 404

                # Update the position
                update_position(cursor, position_id, new_data)
                connection.commit()

        updated_position = {'position_id': position_id, **new_data}
        return jsonify(updated_position), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5012)
