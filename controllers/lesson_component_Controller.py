from flask import render_template, request, redirect, url_for, session, flash
from models.lesson_component_model import lesson_component_Model

class lesson_component_Controller:
    def __init__(self, lesson_component_model: lesson_component_Model):
        self.lesson_component_model = lesson_component_model
    
    def get_current_user(self):
        """Get the current user from the session."""
        if 'user_email' in session:
            result = self.user_model.get(session['user_email'])
            if result['status'] == 'success':
                return result['data']
        return {'email': None, 'team': 'none', 'access': 1}  # Default guest user
    
    def view(self, lesson_component_id):
        """Show a specific lesson_component."""
        current_user = self.get_current_user()
        session['user'] = current_user
        
        # Get the lesson_component
        result = self.lesson_component_model.get(id=lesson_component_id)
        if result['status'] != 'success':
            flash('lesson_component not found', 'error')
            return redirect(url_for('units.view'))
        
        lesson_component = result['data']
        return render_template('lesson.html', active_lesson_component=lesson_component)
    
    def create(self):
        """Create a new lesson_component."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('lessons.view', lesson_id=request.form.get('lesson_id')))
        
        lesson_id = request.form.get('lesson_id')
        title = request.form.get('title')
        content = request.form.get('content')
        lesson_component_type = request.form.get('type')
        
        if not all([lesson_id, title, content, lesson_component_type]):
            flash('All fields are required', 'error')
            return redirect(url_for('lessons.view', lesson_id=lesson_id))
        
        result = self.lesson_component_model.create({
            'lesson_id': int(lesson_id),
            'title': title,
            'content': content,
            'type': lesson_component_type
        })
        
        if result['status'] == 'success':
            flash('lesson_component created successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', lesson_id=lesson_id))
    
    def update(self):
        """Update a lesson_component."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('lessons.view', lesson_id=request.form.get('lesson_id')))
        
        lesson_component_id = request.form.get('lesson_component_id')
        lesson_id = request.form.get('lesson_id')
        title = request.form.get('title')
        content = request.form.get('content')
        lesson_component_type = request.form.get('type')
        
        if not all([lesson_component_id, lesson_id, title, content, lesson_component_type]):
            flash('All fields are required', 'error')
            return redirect(url_for('lessons.view', lesson_id=lesson_id))
        
        result = self.lesson_component_model.update({
            'id': int(lesson_component_id),
            'lesson_id': int(lesson_id),
            'title': title,
            'content': content,
            'type': lesson_component_type
        })
        
        if result['status'] == 'success':
            flash('lesson_component updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', lesson_id=lesson_id))
    
    def delete(self):
        """Delete a lesson_component."""
        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('lessons.view', lesson_id=request.form.get('lesson_id')))
        
        lesson_component_id = request.form.get('lesson_component_id')
        lesson_id = request.form.get('lesson_id')
        
        if not lesson_component_id or not lesson_id:
            flash('lesson_component ID is required', 'error')
            return redirect(url_for('lessons.view', lesson_id=lesson_id))
        
        result = self.lesson_component_model.remove(id=int(lesson_component_id))
        if result['status'] == 'success':
            flash('lesson_component deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', lesson_id=lesson_id))
