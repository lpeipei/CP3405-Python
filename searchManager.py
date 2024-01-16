from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'your_database_uri'
# db = SQLAlchemy(app)

# class Employee(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)
#     position = db.Column(db.String(80), nullable=False)
#     department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
#     department = db.relationship('Department', backref=db.backref('employees', lazy=True))
#
# # 初始化数据库
# db.create_all()

def employee_to_dict(employee):
    return {
        'id': employee.id,
        'name': employee.name,
        'position': employee.position,
        'department_id': employee.department_id
    }

@app.route('/api/employee/list', methods=['GET'])
def get_employee_list():
    # 从查询参数中获取关键字
    keyword = request.args.get('keyword')

    # 构建查询条件
    filters = {}
    if keyword:
        filters['name'] = keyword

    # 根据查询条件从数据库中查询员工列表
    employees = Employee.query.filter_by(**filters).all()

    # 将查询结果转化为字典格式
    employee_list = [employee_to_dict(employee) for employee in employees]

    return jsonify(employee_list)

if __name__ == '__main__':
    app.run(debug=True)
