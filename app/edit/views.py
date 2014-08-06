import json
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
    # result = {}
    notebook.save()
    # return notebook.name
    # return json.dumps({'message': 'hello'})
    return str(notebook.name)
