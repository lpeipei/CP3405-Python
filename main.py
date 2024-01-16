import hashlib
import json
from psycopg2.pool import SimpleConnectionPool

# 设置数据库连接参数
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)

def create_tables(cursor):
    # 创建 company_structure 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_structure (
            id TEXT PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            name TEXT UNIQUE NOT NULL,
            describe TEXT,
            has_children BOOLEAN NOT NULL,
            number INTEGER,
            manager JSONB,
            leader JSONB,
            parent_id TEXT REFERENCES company_structure(id)
        );
    ''')
    # 为 company_structure 表的 name 字段添加索引
    cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_company_structure_name ON company_structure (name);
        ''')
    # 创建 employee 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employee (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT NOT NULL,
            mobile TEXT,
            status INTEGER,
            age INTEGER,
            gender INTEGER,
            avatar TEXT,
            department_id TEXT REFERENCES company_structure(id),
            department_name TEXT REFERENCES company_structure(name)
        );
    ''')


def update_department_employee_count(cursor, department_id):
    # 更新 company_structure 表中指定部门的 employee 数量
    cursor.execute('''
        WITH RECURSIVE department_tree AS (
            SELECT id, parent_id
            FROM company_structure
            WHERE id = %s
            UNION
            SELECT cs.id, cs.parent_id
            FROM company_structure cs
            JOIN department_tree dt ON cs.parent_id = dt.id
        )
        UPDATE company_structure
        SET number = (
            SELECT COUNT(*) FROM employee WHERE department_id IN (SELECT id FROM department_tree)
        )
        WHERE id = %s
    ''', (department_id, department_id))


def insert_data(cursor, data, parent_id=None):
    for node in data:
        # Calculate the node's hash value as a unique ID
        node_id = hashlib.md5(node["name"].encode()).hexdigest()

        # Generate a unique code for each department
        node_code = hashlib.md5(node["name"].encode()).hexdigest()[:8]

        # Insert data into company_structure table
        cursor.execute('''
              INSERT INTO company_structure (id, code, name, describe, has_children, number, manager, leader, parent_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
          ''', (
            node_id,
            node_code,
            node["name"],
            node.get("describe", ''),
            node.get("hasChildren", False),
            0,  # Initialize number to 0
            json.dumps({
                "name": node.get("manager"),
                "employee_id": node.get("manager_employee_id"),
                "position": node.get("manager_position"),
                "department_id": node_id
            }),
            json.dumps({
                "name": node.get("leader"),
                "employee_id": node.get("leader_employee_id"),
                "position": node.get("leader_position"),
                "department_id": node_id
            }),
            parent_id
        ))

        # Insert employee information into employee table
        if "employee" in node:
            employees = node["employee"]
            for employee in employees:
                employee_id = hashlib.md5(employee["name"].encode()).hexdigest()

                # Check if the employee with the same ID already exists
                cursor.execute('''
                          SELECT id FROM employee WHERE id = %s
                      ''', (employee_id,))
                existing_employee_id = cursor.fetchone()

                if existing_employee_id:
                    # If the employee with the same ID already exists, generate a new ID
                    employee_id = hashlib.md5(
                        (employee["name"] + employee["position"]).encode()).hexdigest()

                cursor.execute('''
                          INSERT INTO employee (id, name, position, mobile, status, age, gender, avatar, department_id, department_name)
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                      ''', (
                    employee_id,
                    employee["name"],
                    employee["position"],
                    employee.get("mobile", ''),
                    employee.get("status", 0),
                    employee.get("age", 0),
                    employee.get("gender", 0),
                    employee.get("avatar", ''),
                    node_id,
                    node["name"]
                ))

            # Update the "number" field after processing the employees
            update_department_employee_count(cursor, node_id)

        # Recursively process child nodes
        if "children" in node:
            insert_data(cursor, node["children"], node_id)


def main():
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    # 创建表
    create_tables(cursor)

    # 插入数据
    insert_data(cursor, company_structure)

    # 提交事务并关闭连接
    connection.commit()
    connection.close()


if __name__ == "__main__":
    company_structure = [
        {
            "name": "Company ABC",
            "hasChildren": True,
            "number": 6,
            "id": '111',
            "manager": "John Doe",
            "leader": "Jerry",
            "children": [
                {
                    "name": "HR",
                    "hasChildren": True,
                    "number": 2,
                    "parentId": "111",
                    "id": "112",
                    "manager": "John Doe",
                    "leader": "Jerry",
                    "children": [
                        {
                            "name": "IT",
                            "number": 2,
                            "parentId": "112",
                            "id": "113",
                            "manager": "Bob Johnson",
                            "leader": "Alice",
                            "employee": [
                                {"name": "Bob Johnson", "position": "IT Manager", "code": "123", "id": "21",
                                 "mobile": "123",
                                 "status": 1, "age": 30, "gender": 1, "avatar": '',
                                 "department": {"name": "IT", "id": "113"}},
                                {"name": "Alice Lee", "position": "Software Engineer", "code": "124", "id": "22",
                                 "mobile": "124",
                                 "status": 2, "age": 25, "gender": 0, "avatar": '',
                                 "department": {"name": "IT", "id": "113"}}
                            ]
                        },
                        {
                            "name": "Finance",
                            "number": 2,
                            "id": '222',
                            "manager": "Bob Johnson",
                            "employee": [
                                {"name": "Bob Johnson", "position": "Finance Manager", "code": "125", "id": "23",
                                 "mobile": "125",
                                 "status": 3, "age": 35, "gender": 1, "avatar": '',
                                 "department": {"name": "Finance", "id": "222"}},
                                {"name": "Alice Lee", "position": "Accountant", "code": "126", "id": "24",
                                 "mobile": "126", "status": 4,
                                 "age": 28, "gender": 0, "avatar": '',
                                 "department": {"name": "Finance", "id": "222"}}
                            ]
                        }
                    ]
                },
                {
                    "name": "Marketing",
                    "number": 2,
                    "id": '333',
                    "manager": "Mary Johnson",
                    "employee": [
                        {"name": "Mary Johnson", "position": "Marketing Manager", "code": "127", "id": "25",
                         "mobile": "127",
                         "status": 2, "age": 32, "gender": 0, "avatar": '',
                         "department": {"name": "Marketing", "id": "333"}},
                        {"name": "Mark Smith", "position": "Marketing Specialist", "code": "128", "id": "26",
                         "mobile": "128",
                         "status": 1, "age": 27, "gender": 1, "avatar": '',
                         "department": {"name": "Marketing", "id": "333"}}
                    ]
                }
            ]
        },
        {
            "name": "Company XYZ",
            "hasChildren": True,
            "number": 2,
            "id": '444',
            "manager": "Alice Johnson",
            "leader": "Bob",
            "children": [
                {
                    "name": "Sales",
                    "number": 2,
                    "id": "555",
                    "manager": "Chris Smith",
                    "employee": [
                        {"name": "Chris Smith", "position": "Sales Manager", "code": "129", "id": "27",
                         "mobile": "129",
                         "status": 3, "age": 33, "gender": 1, "avatar": '', "department": {"name": "Sales", "id": "555"}},
                        {"name": "Emma White", "position": "Sales Representative", "code": "130", "id": "28",
                         "mobile": "130",
                         "status": 4, "age": 29, "gender": 0, "avatar": '', "department": {"name": "Sales", "id": "555"}}
                    ]
                }
            ]
        }
    ]

    main()
