from flask import render_template, request, send_file, jsonify,flash
from app.dashboard import dash_bp
from app.models import Department, db, Employee, Checkpoints, Position, Admin
from flask_login import login_required, current_user
from collections import defaultdict
from datetime import timedelta, datetime, time
from sqlalchemy import desc
from weasyprint import HTML
from app.utils import admin_required, employee_required
import pandas as pd 
import io


@dash_bp.route('/admin_dash')
@login_required
@admin_required
def admin_dash():
    return render_template('admin_dash.html', user=current_user)

@dash_bp.route('/load/reports')
@login_required
@admin_required
def reportsdata():
    departments = Department.query.all()
    return render_template('partials/report.html', departments=departments)

@dash_bp.route('/load/report_data', methods=['POST'])
@login_required
@admin_required
def load_datas():
    department_id = request.form.get('department_id')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    if not start_date or not end_date:
        return "<div class='alert alert-warning mt-3' style='width:400px;'><p>Start date and end date are required.</p></div>"
    else :
        
        starting = datetime.strptime(start_date, "%Y-%m-%d").date()
        ending = datetime.strptime(end_date, "%Y-%m-%d").date()

        dates = []
        current = starting
        while current <= ending:
            if current.weekday() != 6:
                dates.append(current)
            current += timedelta(days=1)

        employees = Employee.query.filter_by(department_id=department_id).all()

        work_time = timedelta()
        status = None
        new_report_rows = []
        on_time = time(8, 30)
        
        for employee in employees:
            for date in dates:
                checkpoints_in = Checkpoints.query.filter(
                    Checkpoints.employee_id == employee.id,
                    Checkpoints.moment >= datetime.combine(date, datetime.min.time()),
                    Checkpoints.moment <= datetime.combine(date, datetime.max.time()),
                    Checkpoints.type_id == 1
                ).order_by(Checkpoints.moment).first()
                checkpoints_out = Checkpoints.query.filter(
                    Checkpoints.employee_id == employee.id,
                    Checkpoints.moment >= datetime.combine(date, datetime.min.time()),
                    Checkpoints.moment <= datetime.combine(date, datetime.max.time()),
                    Checkpoints.type_id == 2
                ).order_by(Checkpoints.moment).first()

                if checkpoints_in and checkpoints_out:
                    entry = checkpoints_in.moment.time()
                    out = checkpoints_out.moment.time()
                    work_time = datetime.combine(date, out) - datetime.combine(date, entry)
                    if entry > on_time:
                        status = "late"
                    else:
                        status = "on time"
                elif checkpoints_in and not checkpoints_out:
                    entry = checkpoints_in.moment.time()
                    out = "-:-"
                    work_time = None
                    status = "incomplete"
                elif checkpoints_out and not checkpoints_in:
                    out = checkpoints_out.moment.time()
                    entry = "-:-"
                    work_time = None
                    status = "incomplete"
                else:
                    entry = "-:-"
                    out = "-:-"
                    work_time = None
                    status = "absent"
                new_report_rows.append({
                    'name': employee.name,
                    'date': date,
                    'entry': entry,
                    'exit': out,
                    'work_time': work_time,
                    'status': status
                })

        #data analysis
        df = pd.DataFrame(new_report_rows)

        df["entry"] = pd.to_datetime(df["entry"], format="%H:%M:%S", errors="coerce").dt.time
        df["exit"] = pd.to_datetime(df["exit"], format="%H:%M:%S", errors="coerce").dt.time

        df["date"] = pd.to_datetime(df["date"])
        periode = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        nb_days = len(periode)
        nb_absent = (periode["status"] == "absent").sum()
        absence_percentage = (nb_absent / nb_days) * 100

        valid_entry = periode.dropna(subset=["entry"])
        df_entry_data = pd.to_datetime(valid_entry["entry"].astype(str), format="%H:%M:%S")
        average_entry = df_entry_data.mean().time() if not df_entry_data.empty else None

        valid_out = periode.dropna(subset=["exit"])
        df_exit_data = pd.to_datetime(valid_out["exit"].astype(str), format="%H:%M:%S")
        average_out = df_exit_data.mean().time() if not df_exit_data.empty else None

        regular_entry = df_entry_data.dt.time.mode().iloc[0] if not df_entry_data.empty else None
        regular_exit = df_exit_data.dt.time.mode().iloc[0] if not df_exit_data.empty else None

        work_time_per_employee = periode.groupby("name")["work_time"].sum()

        resume = df.groupby("name").agg(
            nb_abs = ("status", lambda x: (x=="absent").sum()),
            work_day = ("work_time", lambda x: x.notna().sum()),
            total_work_time = ("work_time", "sum")
        )

        resume["mean_work_time"] = resume["total_work_time"] / resume["work_day"]

        mean_arrival_emp = valid_entry.groupby("name")["entry"].apply(
            lambda x: pd.to_datetime(x, format="%H:%M:%S", errors="coerce").mean().time() if not x.empty else None
        )
        mean_departure_emp = valid_out.groupby("name")["exit"].apply(
            lambda x: pd.to_datetime(x, format="%H:%M:%S", errors="coerce").mean().time() if not x.empty else None
        )

        resume["average_arrival"] = mean_arrival_emp
        resume["average_departure"] = mean_departure_emp

        resume_reset = resume.reset_index()
        resume_template = resume_reset.to_dict(orient="records")

        stats = {
            "absence_percentage": round(absence_percentage, 2),
            "average_entry": average_entry.strftime("%H:%M:%S") if average_entry else "N/A",
            "average_exit": average_out.strftime("%H:%M:%S") if average_out else "N/A",
            "frequent_arrival": regular_entry.strftime("%H:%M:%S") if regular_entry else "N/A",
            "frequent_departure": regular_exit.strftime("%H:%M:%S") if regular_exit else "N/A"
        }

    return render_template('partials/report_table.html', report_rows=new_report_rows, stats=stats, resume=resume_template)

#management logic
@dash_bp.route('/load/manage')
@login_required
@admin_required
def managedata():
    departments = Department.query.all()
    positions = Position.query.all()
    return render_template('partials/manage.html', departments=departments, positions=positions)

@dash_bp.route('/load/manage_data', methods=['POST'])
@login_required
@admin_required
def load_managed_data():
    department_id = request.form.get('department_id')
    employee = db.session.query(Employee).filter(Employee.department_id==department_id)
    list_employee = []
    for emp in employee:
        position = Position.query.filter(Position.id==emp.position_id).first()
        department = Department.query.filter(Department.id==emp.department_id).first()
        print('sa position est ', position)
        list_employee.append({
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'sex': emp.sex,
            'department': department.name if department else 'Unknow',
            'position': position.name if position else 'Unknown',
            'department_id': emp.department_id,
            'position_id': emp.position_id
        })
    return render_template('partials/manage_table.html', employee_list=list_employee)


@dash_bp.route('/load/admin-manager')
@login_required
@admin_required
def laod_admin():
    admin = Admin.query.all()
    return render_template('partials/admin-manager.html', admin_list=admin)


@dash_bp.route('/update_emp', methods=['POST'])
@login_required
@admin_required
def update_infos_emp():
    emp_id = request.form.get("emp_id")
    if emp_id and emp_id.strip():
        emp_id = int(emp_id)
    else:
        return "<div class='alert alert-warning mt-3' style='width:400px;'><p>Employee ID is required.</p></div>", 400
    emp_pos = request.form.get("emp_position")
    emp_dep = request.form.get("emp_department")
    emp_name = request.form.get("emp_name")

    if not emp_name or emp_name.isdigit() or emp_name.strip() == "":
        return "<div class='alert alert-warning mt-3' style='width:400px;'><p>Enter a valid name !</p></div>", 400

    emp_email = request.form.get("emp_email")

    if not emp_email or emp_email.isdigit() or emp_email.strip() == "":
        return "<div class='alert alert-warning mt-3' style='width:400px;'><p>Enter a valid email !</p></div>", 400

    emp_sex = request.form.get("emp_sex")

    if not emp_sex or emp_sex.isdigit() or emp_sex.strip() == "" or (emp_sex.upper() != "F" and emp_sex.upper() != "M"):
        return "<div class='alert alert-warning mt-3' style='width:400px;'><p>Enter F or M in the Sex field !</p></div>", 400

    employee = Employee.query.filter(Employee.id==emp_id).first()
    emp_position = Position.query.filter(Position.name==emp_pos).first()
    emp_department = Department.query.filter(Department.id==emp_dep).first()
    
    if employee is not None :
        employee.name = emp_name
        employee.email = emp_email
        employee.sex = emp_sex
        if emp_department and emp_position is not None :
            employee.department_id = emp_department.id 
            employee.position_id = emp_position.id

    db.session.commit()

    if emp_department is not None :
        employee = db.session.query(Employee).filter(Employee.department_id==emp_department.id).all()
    else:
        employee = [employee] if employee is not None else []
    list_employee = []
    if employee is not None:
        for emp in employee:
            position = Position.query.filter(Position.id==emp.position_id).first()
            department = Department.query.filter(Department.id==emp.department_id).first()
            list_employee.append({
                'id': emp.id,
                'name': emp.name,
                'email': emp.email,
                'sex': emp.sex,
                'department': department.name if department else 'Unknow',
                'position': position.name if position else 'Unknown',
                'department_id': emp.department_id,
                'position_id': emp.position_id
            })
    return render_template('partials/manage_table.html', employee_list=list_employee)

@dash_bp.route('/create_emp', methods=["POST"])
@login_required
@admin_required
def create_emp_account():
    new_emp_name = request.form.get('new_emp_name')
    new_emp_email = request.form.get('new_emp_email')
    new_emp_sex = request.form.get('new_emp_sex')
    new_emp_pos = request.form.get('new_emp_position')
    new_emp_dep = request.form.get('new_emp_department')
    emp_pass = request.form.get('emp_pass')
    confirm_emp_pass = request.form.get('confirm_emp_pass')

    if not new_emp_name or not new_emp_email or not new_emp_sex or not new_emp_pos or not new_emp_dep or not emp_pass or not confirm_emp_pass:
        return '<div class="alert alert-warning"><p> Please fill all fields !</p></div>'
    
    if new_emp_name.isdigit() or new_emp_name.strip() == "":
        return '<div class="alert alert-warning"><p>Enter a valid name !</p></div>'
    
    if new_emp_email.isdigit() or new_emp_email.strip() == "":
        return '<div class="alert alert-warning"><p>Enter a valid email !</p></div>'
    
    if new_emp_sex.isdigit() or new_emp_sex.strip() == "" or (new_emp_sex.upper() != "F" and new_emp_sex.upper() != "M"):
        return '<div class="alert alert-warning"><p>Enter F or M in the Sex field !</p></div>'

    if len(emp_pass)<6 or emp_pass.strip() == "":
        return '<div class="alert alert-warning"><p> Enter a 6 characters password at least </p></div>'
    
    if emp_pass != confirm_emp_pass:
        return '<div class="alert alert-warning"><p> confirm password does not match </p></div>'
    
    employee_by_email = Employee.query.filter(Employee.email == new_emp_email).all()
    employee_by_name = Employee.query.filter(Employee.name == new_emp_name).all()

    if employee_by_email or employee_by_name:
        return '<div class="alert alert-warning"><p> This employee is already registered </p></div>'
    
    emp = Employee(
        name = new_emp_name, #type: ignore
        email = new_emp_email,#type: ignore
        password = "", #type: ignore
        sex = new_emp_sex, #type: ignore
        position_id = new_emp_pos, #type: ignore
        department_id = new_emp_dep #type: ignore
    )
    emp.create_pass(emp_pass)
    db.session.add(emp)
    db.session.commit()

    return '<div class="alert alert-success"><p> Employee registration success </p></div>"'

#export datas
@dash_bp.route('/export_datas', methods=['POST'])
@login_required
@admin_required
def export():
    department_id = request.form.get('exp_dep_id')
    start_date = request.form.get('exp_start_date')
    end_date = request.form.get('exp_end_date')

    if not start_date or not end_date:
        return "<p>Start date and end date are required.</p>"
    else :
        
        starting = datetime.strptime(start_date, "%Y-%m-%d").date()
        ending = datetime.strptime(end_date, "%Y-%m-%d").date()

        dates = []
        current = starting
        while current <= ending:
            if current.weekday() != 6:
                dates.append(current)
            current += timedelta(days=1)

        employees = Employee.query.filter_by(department_id=department_id).all()
        department = Department.query.filter(Department.id==department_id).first()

        work_time = timedelta()
        status = None
        new_report_rows = []
        on_time = time(8, 30)
        
        for employee in employees:
            for date in dates:
                checkpoints_in = Checkpoints.query.filter(
                    Checkpoints.employee_id == employee.id,
                    Checkpoints.moment >= datetime.combine(date, datetime.min.time()),
                    Checkpoints.moment <= datetime.combine(date, datetime.max.time()),
                    Checkpoints.type_id == 1
                ).order_by(Checkpoints.moment).first()
                checkpoints_out = Checkpoints.query.filter(
                    Checkpoints.employee_id == employee.id,
                    Checkpoints.moment >= datetime.combine(date, datetime.min.time()),
                    Checkpoints.moment <= datetime.combine(date, datetime.max.time()),
                    Checkpoints.type_id == 2
                ).order_by(Checkpoints.moment).first()

                if checkpoints_in and checkpoints_out:
                    entry = checkpoints_in.moment.time()
                    out = checkpoints_out.moment.time()
                    work_time = datetime.combine(date, out) - datetime.combine(date, entry)
                    if entry > on_time:
                        status = "late"
                    else:
                        status = "on time"
                elif checkpoints_in and not checkpoints_out:
                    entry = checkpoints_in.moment.time()
                    out = "-:-"
                    work_time = None
                    status = "undefined"
                elif checkpoints_out and not checkpoints_in:
                    out = checkpoints_out.moment.time()
                    entry = "-:-"
                    work_time = None
                    status = "undefined"
                else:
                    entry = "-:-"
                    out = "-:-"
                    work_time = None
                    status = "absent"
                new_report_rows.append({
                    'name': employee.name,
                    'sex':employee.sex,
                    'position': employee.position.name,
                    'date': date,
                    'entry': entry,
                    'exit': out,
                    'work_time': work_time,
                    'status': status
                })

        cleaned_rows = [
            row for row in new_report_rows
            if row["status"] != "absent" and (row["entry"] != "-:-" or row["exit"] != "-:-")
        ]

        cleaned_rows.sort(key=lambda r: (r["name"], r["date"]))

        #data analysis
        df = pd.DataFrame(new_report_rows)

        df["entry"] = pd.to_datetime(df["entry"], format="%H:%M:%S", errors="coerce").dt.time
        df["exit"] = pd.to_datetime(df["exit"], format="%H:%M:%S", errors="coerce").dt.time

        df["date"] = pd.to_datetime(df["date"])
        periode = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

        nb_days = len(periode)
        nb_absent = (periode["status"] == "absent").sum()
        absence_percentage = (nb_absent / nb_days) * 100

        valid_entry = periode.dropna(subset=["entry"])
        df_entry_data = pd.to_datetime(valid_entry["entry"].astype(str), format="%H:%M:%S")
        average_entry = df_entry_data.mean().time() if not df_entry_data.empty else None

        valid_out = periode.dropna(subset=["exit"])
        df_exit_data = pd.to_datetime(valid_out["exit"].astype(str), format="%H:%M:%S")
        average_out = df_exit_data.mean().time() if not df_exit_data.empty else None

        regular_entry = df_entry_data.dt.time.mode().iloc[0] if not df_entry_data.empty else None
        regular_exit = df_exit_data.dt.time.mode().iloc[0] if not df_exit_data.empty else None

        resume = df.groupby("name").agg(
            nb_abs = ("status", lambda x: (x=="absent").sum()),
            work_day = ("work_time", lambda x: x.notna().sum()),
            total_work_time = ("work_time", "sum")
        )

        resume["mean_work_time"] = resume["total_work_time"] / resume["work_day"]

        mean_arrival_emp = valid_entry.groupby("name")["entry"].apply(
            lambda x: pd.to_datetime(x, format="%H:%M:%S", errors="coerce").mean().time() if not x.empty else None
        )
        mean_departure_emp = valid_out.groupby("name")["exit"].apply(
            lambda x: pd.to_datetime(x, format="%H:%M:%S", errors="coerce").mean().time() if not x.empty else None
        )

        resume["average_arrival"] = mean_arrival_emp
        resume["average_departure"] = mean_departure_emp

        resume_reset = resume.reset_index()
        resume_template = resume_reset.to_dict(orient="records")

        stats = {
            "absence_percentage": round(absence_percentage, 2),
            "average_entry": average_entry.strftime("%H:%M:%S") if average_entry else "N/A",
            "average_exit": average_out.strftime("%H:%M:%S") if average_out else "N/A",
            "frequent_arrival": regular_entry.strftime("%H:%M:%S") if regular_entry else "N/A",
            "frequent_departure": regular_exit.strftime("%H:%M:%S") if regular_exit else "N/A"
        }

    rendered = render_template('data_page.html', report_rows=cleaned_rows, stats=stats, resume=resume_template, department=department,
                           start_date=start_date, end_date=end_date)
    
    buffer = io.BytesIO()
    HTML(string=rendered, base_url=request.root_path).write_pdf(buffer)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='export_datas.pdf',
        mimetype='application/pdf'
    )

@dash_bp.route('/delete_employee/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return jsonify({'message': 'Employé supprimé avec succès'})


@dash_bp.route('/delete_admin/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_admin(id):
    admin = Admin.query.get_or_404(id)
    db.session.delete(admin)
    db.session.commit()
    return jsonify({'message': 'Admin supprimé avec succès'})

@dash_bp.route('/create_admin', methods=["POST"])
@login_required
@admin_required
def create_admin_account():
    new_ad_login = request.form.get('new_ad_login')
    ad_pass = request.form.get('new_ad_pass')
    confirm_ad_pass = request.form.get('confirm_ad_pass')

    if not new_ad_login or  not ad_pass or not confirm_ad_pass:
        return '<p> Please fill all fields </p>'
    
    if len(ad_pass)<6:
        return '<p> Enter a 6 characters password at least </p>'
    
    if ad_pass != confirm_ad_pass:
        return '<p> confirm password does not match </p>'
    
    admin_by_login = Admin.query.filter(Admin.login == new_ad_login).all()

    if admin_by_login:
        return '<p> This admin is already registered </p>'
    
    admin = Admin(
        login = new_ad_login, #type: ignore
        password_hashed = "", #type: ignore
    )
    admin.create_pass(ad_pass)
    db.session.add(admin)
    db.session.commit()

    return '<p> Admin registration success </p>'