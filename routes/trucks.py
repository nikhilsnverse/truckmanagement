from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.decorators import login_required, manager_required
from models.truck import Truck
from models.document import Document
from database import db
from datetime import datetime
from utils.helpers import save_file

trucks_bp = Blueprint('trucks', __name__, template_folder='../templates')


@trucks_bp.route('/')
@manager_required
def list_trucks():
    status_filter = request.args.get('status', '')
    query = Truck.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    trucks = query.order_by(Truck.created_at.desc()).all()
    return render_template('trucks/list.html', trucks=trucks, status_filter=status_filter)


@trucks_bp.route('/add', methods=['GET', 'POST'])
@manager_required
def add_truck():
    if request.method == 'POST':
        truck_number = request.form.get('truck_number', '').strip()
        model = request.form.get('model', '').strip()
        insurance_expiry = request.form.get('insurance_expiry', '').strip()
        fitness_expiry = request.form.get('fitness_expiry', '').strip()
        status = request.form.get('status', 'Active')

        if not truck_number or not model or not insurance_expiry or not fitness_expiry:
            flash('Please fill in all required fields.', 'danger')
            return render_template('trucks/form.html', truck=None)

        existing = Truck.query.filter_by(truck_number=truck_number).first()
        if existing:
            flash('Truck number already exists.', 'danger')
            return render_template('trucks/form.html', truck=None)

        truck = Truck(
            truck_number=truck_number,
            model=model,
            insurance_expiry=datetime.strptime(insurance_expiry, '%Y-%m-%d').date(),
            fitness_expiry=datetime.strptime(fitness_expiry, '%Y-%m-%d').date(),
            status=status,
            owner_id=session.get('user_id')
        )
        db.session.add(truck)
        db.session.commit()

        flash('Truck added successfully!', 'success')
        return redirect(url_for('trucks.list_trucks'))

    return render_template('trucks/form.html', truck=None)


@trucks_bp.route('/edit/<int:truck_id>', methods=['GET', 'POST'])
@manager_required
def edit_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    if request.method == 'POST':
        truck.truck_number = request.form.get('truck_number', '').strip()
        truck.model = request.form.get('model', '').strip()
        insurance_expiry = request.form.get('insurance_expiry', '').strip()
        fitness_expiry = request.form.get('fitness_expiry', '').strip()
        truck.status = request.form.get('status', 'Active')

        if insurance_expiry:
            truck.insurance_expiry = datetime.strptime(insurance_expiry, '%Y-%m-%d').date()
        if fitness_expiry:
            truck.fitness_expiry = datetime.strptime(fitness_expiry, '%Y-%m-%d').date()

        db.session.commit()
        flash('Truck updated successfully!', 'success')
        return redirect(url_for('trucks.list_trucks'))

    return render_template('trucks/form.html', truck=truck)


@trucks_bp.route('/delete/<int:truck_id>', methods=['POST'])
@manager_required
def delete_truck(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    db.session.delete(truck)
    db.session.commit()
    flash('Truck deleted successfully!', 'success')
    return redirect(url_for('trucks.list_trucks'))


@trucks_bp.route('/upload-document/<int:truck_id>', methods=['POST'])
@manager_required
def upload_document(truck_id):
    truck = Truck.query.get_or_404(truck_id)
    doc_type = request.form.get('doc_type', 'Other')
    file = request.files.get('file')

    if file and file.filename:
        filename = save_file(file)
        if filename:
            doc = Document(truck_id=truck.id, type=doc_type, file_path=filename)
            db.session.add(doc)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')
        else:
            flash('Invalid file type. Allowed: png, jpg, jpeg, gif, pdf', 'danger')
    else:
        flash('No file selected.', 'danger')

    return redirect(url_for('trucks.list_trucks'))
