from flask import render_template, request, redirect, url_for, session, flash
from models.lesson_model import LessonModel
from models.lesson_component_model import LessonComponentModel
from models.user_model import UserModel
from models.unit_model import UnitModel

class LessonController:
    def __init__(self, lesson_model: LessonModel, lesson_component_model: LessonComponentModel, user_model: UserModel, unit_model: UnitModel):
        self.lesson_model = lesson_model
        self.lesson_component_model = lesson_component_model
        self.user_model = user_model
        self.unit_model = unit_model
    
    def get_current_user(self):
        """Get the current user from the session."""
        if 'user' in session and session['user'].get('email'):
            return session['user']
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                session['user'] = result['data']
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
    
    def view(self, unit_id, lesson_id):
        """Show a specific lesson and its lesson_components."""
        current_user = self.get_current_user()
        session['user'] = current_user
        
        # Get the lesson
        lesson_result = self.lesson_model.get(id=lesson_id)
        unit_result = self.unit_model.get(id=unit_id)
        if lesson_result['status'] == 'error':
            flash(f'Lesson not found {lesson_result}', 'error')
            return redirect(url_for('units.view'))
        if lesson_result['status'] == 'error':
            flash(f'Unit not found {unit_result}', 'error')
            return redirect(url_for('units.view'))        
        
        lesson = lesson_result['data']
        unit = unit_result["data"]
        
        # Get all lesson components for this lesson
        lesson_components_result = self.lesson_component_model.get_by_lesson_id(lesson_id)
        lesson_components = lesson_components_result['data'] if lesson_components_result['status'] == 'success' else []
        
        return render_template('lesson.html',  # Changed from 'lessons.view' to 'lesson.html'
                         lesson=lesson, 
                         lesson_id=lesson_id, 
                         unit_id=unit_id, 
                         unit=unit, 
                         lesson_components=lesson_components, 
                         user=current_user)
    
    def create(self):
        """Create a new lesson."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect('/units')
        
        unit_id = request.form.get('unit_id')
        name = request.form.get('lesson_name')
        type = request.form.get('lesson_type')   
        img = None 
        img = request.form.get('lesson_img')    
        if not all([unit_id, name, type]):
            # flash('All fields except img are required', 'error')
            flash(f"name: {name}, type: {type}, img: {img}, unit_id:{unit_id}")
            return redirect('/units')
        
        result = self.lesson_model.create({
            'unit_id': int(unit_id),
            'name': name,
            'img': img,
            'type': type,
        })
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
        unit_id = request.form.get('unit_id')
        lesson_name = request.form.get('lesson_name')
        
        if not lesson_id or not lesson_name:
            flash('Lesson ID and name are required', 'error')
            return redirect(url_for('units.view'))
        
        lesson = self.lesson_model.update({'id': int(lesson_id), 'name': lesson_name})
        unit = self.unit_model.get(id=int(unit_id))['data']
        
        if lesson['status'] == 'success':
            flash('Lesson updated successfully', 'success')
            return redirect(url_for('lesson.view', unit_id=unit_id, lesson_id=lesson_id, unit=unit, lesson=lesson['data']))
        else:
            flash(lesson['data'], 'error')
            return redirect(url_for('lesson.view', unit_id=unit_id, unit=unit, lesson=lesson["data"],lesson_id=lesson_id))
    
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
