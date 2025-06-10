from flask import render_template, request, redirect, url_for, session, flash
from models.lesson_model import LessonModel
from models.lesson_component_model import LessonComponentModel
from models.user_model import UserModel
from models.unit_model import UnitModel
from controllers.base_controller import BaseController


class SessionController(BaseController):
    def __init__(self, user_model: UserModel):
        self.user_model = user_model
        

    def index(self):
        return render_template('index.html')
