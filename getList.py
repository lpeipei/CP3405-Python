import psycopg2
from psycopg2.pool import SimpleConnectionPool
from flask import Flask, jsonify, request
from flask_cors import CORS

# Create a connection pool
connection_pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host='127.0.0.1',
    user='lipeipei',
    password='',
    database='firstdb'
)

app = Flask(__name__)
CORS(app)


def search_records(cursor, keyword):
  if not keyword:
    cursor.execute('''
          WITH RECURSIVE org_tree AS (
              SELECT id, code, name, describe, has_children, number, manager, leader, parent_id
              FROM company_structure
              WHERE parent_id IS NULL
              UNION
              SELECT cs.id, cs.code, cs.name, cs.describe cs.has_children, cs.number, cs.manager, cs.leader, cs.parent_id
              FROM company_structure cs
              JOIN org_tree ot ON cs.parent_id = ot.id
          )
          SELECT * FROM org_tree;
      ''')
  else:
    cursor.execute('''
          WITH RECURSIVE org_tree AS (
              SELECT id, code, name, describe, has_children, number, manager, leader, parent_id
              FROM company_structure
              WHERE parent_id IS NULL
              UNION
              SELECT cs.id, cs.code, cs.name, cs.describe, cs.has_children, cs.number, cs.manager, cs.leader, cs.parent_id
              FROM company_structure cs
              JOIN org_tree ot ON cs.parent_id = ot.id
          )
          SELECT * FROM org_tree
          WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(code) LIKE LOWER(%s);
      ''', (f'%{keyword}%', f'%{keyword}%'))

  results = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
  return results

def build_tree_structure(rows, parent_id=None):
    tree_structure = []
    for row in rows:
      if row[8] == parent_id:
          node = {
            'id': row[0],
            'code': row[1],
            'name': row[2],
            'describe': row[3],
            'has_children': row[4],
            'number': row[5],
            'manager': row[6],
            'leader': row[7],
            'children': build_tree_structure(rows, row[0])
          }
          tree_structure.append(node)
    return tree_structure


@app.route('/api/organization/list', methods=['GET'])
def get_organization_structure():
  keyword = request.args.get('keyword')
  print(keyword, 'keyword11')
  connection = connection_pool.getconn()
  cursor = connection.cursor()
  try:
    if not keyword:
      cursor.execute('SELECT * FROM company_structure')
      rows = cursor.fetchall()
      organization_structure = build_tree_structure(rows)
      return jsonify(organization_structure)
    else:
      cursor.execute('''
                        WITH RECURSIVE org_tree AS (
                            SELECT id, code, name, describe, has_children, number, manager, leader, parent_id
                            FROM company_structure
                            WHERE parent_id IS NULL
                            UNION
                            SELECT cs.id, cs.code, cs.name, cs.describe, cs.has_children, cs.number, cs.manager, cs.leader, cs.parent_id
                            FROM company_structure cs
                            JOIN org_tree ot ON cs.parent_id = ot.id
                        )
                        SELECT * FROM org_tree
                        WHERE LOWER(name) LIKE LOWER(%s) OR LOWER(code) LIKE LOWER(%s);
                    ''', (f'%{keyword}%', f'%{keyword}%'))

      results = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
      return results
  finally:
    cursor.close()
    connection_pool.putconn(connection)


if __name__ == "__main__":
    app.run(debug=True)
