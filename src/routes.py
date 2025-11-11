from flask import Blueprint, render_template,request
import manim


routes = Blueprint('routes', __name__)

@routes.route('/')
def index():
    return "Welcome to the Infographics Generator!"