from flask import render_template, request, redirect, url_for, session, flash
from models.lesson_model import Lesson_Model
from models.lesson_component_model import Lesson_Component_Model

class Lesson_Controller:
    def __init__(self, lesson_model: Lesson_Model, lesson_component_model: Lesson_Component_Model):
        self.lesson_model = lesson_model
        self.lesson_component_model = lesson_component_model
    
    def get_current_user(self):
        """Get the current user from the session."""
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
    
    def view(self, lesson_id):
        """Show a specific lesson and its components."""
        current_user = self.get_current_user()
        session['user'] = current_user
        
        # Get the lesson
        lesson_result = self.lesson_model.get(id=lesson_id)
        if lesson_result['status'] != 'success':
            flash('Lesson not found', 'error')
            return redirect(url_for('units.view'))
        
        lesson = lesson_result['data']
        
        # Get all components for this lesson
        components_result = self.lesson_component_model.get_by_lesson(lesson_id)
        components = components_result['data'] if components_result['status'] == 'success' else []
        
        return render_template('lesson.html', lesson=lesson, components=components)
    
    def create(self):
        """Create a new lesson."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        unit_id = request.form.get('unit_id')
        lesson_name = request.form.get('lesson_name')
        
        if not unit_id or not lesson_name:
            flash('Unit ID and lesson name are required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.lesson_model.create({'name': lesson_name, 'unit_id': int(unit_id)})
        if result['status'] == 'success':
            flash('Lesson created successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('units.view'))
    
    def update(self):
        """Update a lesson."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        lesson_id = request.form.get('lesson_id')
        lesson_name = request.form.get('lesson_name')
        
        if not lesson_id or not lesson_name:
            flash('Lesson ID and name are required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.lesson_model.update({'id': int(lesson_id), 'name': lesson_name})
        if result['status'] == 'success':
            flash('Lesson updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', lesson_id=lesson_id))
    
    def delete(self):
        """Delete a lesson."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('units.view'))
        
        lesson_id = request.form.get('lesson_id')
        if not lesson_id:
            flash('Lesson ID is required', 'error')
            return redirect(url_for('units.view'))
        
        result = self.lesson_model.remove(id=int(lesson_id))
        if result['status'] == 'success':
            flash('Lesson deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('units.view'))
