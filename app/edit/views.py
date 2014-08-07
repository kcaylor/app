from flask.ext.login import login_required
from app import csrf
from flask import request
from . import edit
from ..models.notebook import Notebook


@edit.route('/nbk_name', methods=['POST'])
@login_required
@csrf.exempt
def nbk_name():
    notebook = Notebook.objects(id=request.form["pk"]).first()
    notebook.name = request.form["value"]
    notebook.save()
    return str(notebook.name)


@edit.route('/nbk_notes', methods=['POST'])
@login_required
@csrf.exempt
def nbk_notes():
    notebook = Notebook.objects(id=request.form["pk"]).first()
    notebook.notes = request.form["value"]
    notebook.save()
    return str(notebook.name)
