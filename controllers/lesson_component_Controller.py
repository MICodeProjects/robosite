from flask import render_template, request, redirect, url_for, session, flash
from models.lesson_component_model import LessonComponentModel
from models.user_model import UserModel
from models.unit_model import UnitModel
from models.lesson_model import LessonModel
from controllers.base_controller import BaseController


class LessonComponentController(BaseController):    
    def __init__(self, lesson_component_model: LessonComponentModel, user_model: UserModel, lesson_model: LessonModel, unit_model: UnitModel):
        self.lesson_component_model = lesson_component_model
        self.user_model = user_model
        self.unit_model = unit_model
        self.lesson_model = lesson_model


    
    def view(self, unit_id, lesson_id, lesson_component_id):
        """Show a specific lesson component."""
        current_user = self.get_current_user()
        
        # Get the lesson component, lesson and unit
        result = self.lesson_component_model.get(id=lesson_component_id)
        lesson = self.lesson_model.get(id=lesson_id)
        unit= self.unit_model.get(id=unit_id)
        
        if result['status'] != 'success':
            flash('Lesson component not found', 'error')
            return redirect(url_for('lesson.view', lesson=lesson["data"], unit=unit["data"], unit_id=unit_id, lesson_id=lesson_id))
        
        lesson_component = result['data']
        lesson = lesson['data']
        unit = unit['data']

        lesson_components_result = self.lesson_component_model.get_by_lesson_id(lesson_id)
        lesson_components = lesson_components_result['data'] if lesson_components_result['status'] == 'success' else []
        
        
        return render_template('lesson.html',  # No change needed here since this is template name
                         current_lesson_component=lesson_component,
                         lesson=lesson,
                         unit_id=unit_id,
                         lesson_id=lesson_id,
                         unit=unit,
                         lesson_components=lesson_components,
                         user=current_user)
    
    def create(self):
        """Create a new lesson component."""

        
        unit_id = request.form.get('unit_id')
        lesson_id = request.form.get('lesson_id')
        name = request.form.get('lesson_component_name')
        content = request.form.get('lesson_component_content')
        lesson_component_type = request.form.get('lesson_component_type')

        lesson = self.lesson_model.get(id=lesson_id)['data']
        unit = self.unit_model.get(id=unit_id)['data']

        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('lesson.view', unit=unit, lesson=lesson,
                              unit_id=unit_id, 
                              lesson_id=lesson_id))

        if not all([lesson_id, name, content, lesson_component_type]):
            flash('All fields are required', 'error')
            return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                              unit_id=unit_id, lesson_id=lesson_id))
        
        result = self.lesson_component_model.create({
            'lesson_id': int(lesson_id),
            'name': name,
            'content': content,
            'type': lesson_component_type
        })
        
        if result['status'] == 'success':
            flash('lesson component created successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                          unit_id=unit_id, lesson_id=lesson_id))

    def update(self):
        """Update a lesson component."""
        lesson_component_id = request.form.get('lesson_component_id')
        lesson_id = request.form.get('lesson_id')
        name = request.form.get('lesson_component_name')
        content = request.form.get('lesson_component_content')
        type = request.form.get('lesson_component_type')        
        unit_id=request.form.get('unit_id')

        lesson = self.lesson_model.get(id=lesson_id)['data']
        unit = self.unit_model.get(id=unit_id)['data']

        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')
            return redirect(url_for('lesson.view', unit=unit, lesson=lesson, unit_id=request.form.get('unit_id'), lesson_id=request.form.get('lesson_id')))
        

        
        if not all([lesson_component_id, lesson_id]):
            flash(f'All fields are required les com id les id type content name{lesson_component_id, lesson_id, type, content, name}', 'error')
            return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                              unit_id=unit_id, lesson_id=lesson_id))
        
        result = self.lesson_component_model.update({
            'id': int(lesson_component_id),
            'lesson_id': int(lesson_id),
            'name': name if name is not None else self.lesson_component_model.get(id=lesson_component_id)["data"]["name"],
            'content': content if content is not None else self.lesson_component_model.get(id=lesson_component_id)["data"]["content"],
            'type': type if type is not None else self.lesson_component_model.get(id=lesson_component_id)["data"]["type"]
        })
        
        if result['status'] == 'success':
            flash('lesson component updated successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                          unit_id=unit_id, lesson_id=lesson_id))

    def delete(self):
        """Delete a lesson component."""
        unit_id = request.form.get('unit_id')
        lesson_id = request.form.get('lesson_id')
        lesson_component_id = request.form.get('lesson_component_id')
        
        lesson = self.lesson_model.get(id=lesson_id)['data']
        unit = self.unit_model.get(id=unit_id)['data']
        user = self.get_current_user()


        if self.get_current_user()['access'] < 3:
            flash('Unauthorized access', 'error')

            return redirect(url_for('lesson.view', user=user, lesson=lesson, unit=unit, unit_id=unit_id, lesson_id=lesson_id))
        

        
        if not all([unit_id, lesson_id, lesson_component_id]):
            flash('All IDs are required', 'error')
            return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                              unit_id=unit_id, lesson_id=lesson_id))
        
        result = self.lesson_component_model.remove(id=int(lesson_component_id))
        if result['status'] == 'success':
            flash('lesson component deleted successfully', 'success')
        else:
            flash(result['data'], 'error')
        
        return redirect(url_for('lessons.view', unit=unit, lesson=lesson,
                          unit_id=unit_id, lesson_id=lesson_id))
