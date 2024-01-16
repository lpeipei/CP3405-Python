from flask import Flask, jsonify
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

def delete_position(cursor, position_id):
    cursor.execute('''
        DELETE FROM position
        WHERE id = %s
    ''', (position_id,))

def fetch_position(cursor, position_id):
    cursor.execute('''
        SELECT * FROM position
        WHERE id = %s
    ''', (position_id,))
    return cursor.fetchone()

@app.route('/api/position/delete/<position_id>', methods=['DELETE'])
def delete_position_endpoint(position_id):
    try:
        with psycopg2.connect(**connection_params) as connection:
            with connection.cursor() as cursor:
                # Check if the position with the given ID exists
                existing_position = fetch_position(cursor, position_id)
                if not existing_position:
                    return jsonify({'error': 'Position not found'}), 404

                # Delete the position
                delete_position(cursor, position_id)
                connection.commit()

        deleted_position = {'position_id': position_id, 'message': 'Position deleted successfully'}
        return jsonify(deleted_position), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5013)
