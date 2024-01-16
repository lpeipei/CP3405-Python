from flask import Flask, jsonify, request
import psycopg2
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# 设置数据库连接参数
connection_params = {
    "host": "127.0.0.1",
    "user": "lipeipei",
    "password": "",
    "database": "firstdb"
}

def query_positions(cursor, keyword=None):
    # 构建 SQL 查询语句
    if keyword:
        query = '''
            SELECT * FROM position
            WHERE name ILIKE %s OR code ILIKE %s
        '''
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
    else:
        # 如果没有提供 keyword，则返回所有数据
        cursor.execute("SELECT * FROM position")

    # 获取查询结果
    result = cursor.fetchall()

    return result
# # 连接到数据库
# connection = psycopg2.connect(**connection_params)
# cursor = connection.cursor()
#
# # 创建 position 表
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS position (
#         id SERIAL PRIMARY KEY,
#         name VARCHAR(255) NOT NULL,
#         salary INTEGER,
#         code VARCHAR(255),
#         description TEXT,
#         department_id TEXT REFERENCES company_structure(id),
#         department_name TEXT REFERENCES company_structure(name)
#     )
# ''')
#
# # 提交更改并关闭连接
# connection.commit()
# cursor.close()
# connection.close()

@app.route('/api/positions', methods=['GET'])
def get_positions():
    # 连接到数据库
    connection = psycopg2.connect(**connection_params)
    cursor = connection.cursor()

    # 获取请求参数中的 keyword
    keyword = request.args.get('keyword')

    # 查询 position 表
    positions = query_positions(cursor, keyword)

    # 将查询结果格式化为 JSON 格式并返回
    result = [{'id': row[0], 'name': row[1], 'salary': row[2], 'code': row[3], 'description': row[4], 'department_id': row[5], 'department_name': row[6]} for row in positions]

    # 关闭连接
    cursor.close()
    connection.close()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5009)
