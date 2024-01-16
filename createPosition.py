import psycopg2
from psycopg2 import sql

# 设置数据库连接参数
connection_params = {
    "host": "127.0.0.1",
    "user": "lipeipei",
    "password": "",
    "database": "firstdb"
}

def insert_positions(cursor, positions_data):
    # 插入数据之前检查匹配项
    for position_data in positions_data:
      cursor.execute("SELECT id FROM company_structure WHERE name = %s", (position_data[4],))
      department_id = cursor.fetchone()
      if department_id:
        position_data += (department_id[0],)
      else:
        print(f"No matching department found for {position_data[4]}")

    # 使用 executemany 插入多行数据，不包括 "id" 列
    cursor.executemany('''
          INSERT INTO position (name, salary, code, description, department_id, department_name)
          VALUES (%s, %s, %s, %s, %s, %s)
      ''', [(pos[0], pos[1], pos[2], pos[3], pos[5], pos[4]) for pos in positions_data])


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

positions_data = [
    ('Software Development Engineer', 1000, '12387', 'textetxte', 'cd32106bcb6de321930cf34574ea388c', 'IT'),
    ('Data Analyst', 800, '98765', 'data analysis role', 'cd32106bcb6de321930cf34574ea388c', 'Finance'),
    ('HR Manager', 1200, '45678', 'human resources role', 'fd4c638da5f85d025963f99fe90b1b1a', 'HR'),
    ('IT Manager', 1200, '45678', 'human resources role', 'd32106bcb6de321930cf34574ea388c', 'IT'),
    ('Financial Analyst', 900, '23456', 'finance role', 'c482980d384a9d0e7bc39e1140270870', 'Finance')
    # 添加更多示例数据...
]

# 插入数据
# insert_positions(cursor, positions_data)

# 提交更改并关闭连接
connection.commit()

# 重新连接数据库，以便打印数据
connection = psycopg2.connect(**connection_params)
cursor = connection.cursor()


# 关闭连接
cursor.close()
connection.close()
