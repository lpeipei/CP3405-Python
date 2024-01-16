from flask import Flask, jsonify
from psycopg2.pool import SimpleConnectionPool
from flask_cors import CORS

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

def get_status_data():
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    # 查询所有的status以及对应的数据量
    cursor.execute('''
        SELECT status, COUNT(*) as number FROM employee GROUP BY status
    ''')
    status_data = cursor.fetchall()

    connection_pool.putconn(connection)

    return status_data

@app.route('/api/status/list', methods=['GET'])
def status_list():
    status_data = get_status_data()

    # 将查询结果格式化为接口返回的JSON格式
    result = [{'value': status, 'number': number} for status, number in status_data]

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5008)
