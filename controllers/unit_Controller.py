from flask import render_template, request, redirect, url_for, session, flash
from models.unit_model import UnitModel
from models.user_model import UserModel
from models.lesson_model import LessonModel
from controllers.base_controller import BaseController


class UnitController(BaseController):
    def __init__(self, unit_model: UnitModel, lesson_model: LessonModel, user_model: UserModel):
        self.unit_model = unit_model
        self.lesson_model = lesson_model
        self.user_model = user_model

   
    
    def view(self):
        """Show all units and their lessons."""
        current_user = self.get_current_user()
        session['user'] = current_user
        
        # Get all units
        units_result = self.unit_model.get_all()
        units = units_result['data'] if units_result['status'] == 'success' else []
        
        # For each unit, get its lessons
        for unit in units:
            lessons_result = self.lesson_model.get_by_unit_id(unit['id'])
            unit['lessons'] = lessons_result['data'] if lessons_result['status'] == 'success' else []
        
        return render_template('units.html', units=units, user=current_user)
    
    def create(self):
        """Create a new unit."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        unit_name = request.form.get('unit_name')
        if not unit_name:
            flash('Unit name is required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.unit_model.create(unit_name)
        if result['status'] == 'success':
            flash('Unit created successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('units.view'))
    
    def update(self):
        """Update a unit."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        unit_id = request.form.get('unit_id')
        unit_name = request.form.get('unit_name')
        
        if not unit_id or not unit_name:
            flash('Unit ID and name are required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.unit_model.update({'id': int(unit_id), 'name': unit_name})
        if result['status'] == 'success':
            flash('Unit updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('units.view'))
    
    def delete(self):
        """Delete a unit."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        unit_id = request.form.get('unit_id')
        if not unit_id:
            flash('Unit ID is required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.unit_model.remove(id=int(unit_id))
        if result['status'] == 'success':
            flash('Unit deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('units.view'))
