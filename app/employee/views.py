from flask import render_template
from app.employee import employee_bp

@employee_bp.route('/')
def employee_dashboard():
    # Employee dashboard logic goes here
    return {"HI":"BRO"}
#Add all employee logic