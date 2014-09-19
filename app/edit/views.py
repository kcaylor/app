from flask.ext.login import login_required
from flask import request
from app.decorators import admin_required
from . import edit
from app.shared.models.notebook import Notebook


@edit.route('/nbk_name', methods=['POST'])
@login_required
# @csrf.exempt
def nbk_name():
    notebook = Notebook.objects(id=request.form["pk"]).first()
    notebook.name = request.form["value"]
    notebook.save()
    return str(notebook.name)


@edit.route('/nbk_location', methods=['POST'])
@login_required
def nbk_location():
    notebook = Notebook.objects(id=request.form["nbk_id"]).first()
    return str('okay')


@edit.route('/nbk_tags', methods=['POST'])
@login_required
def nbk_tags():
    notebook = Notebook.objects(id=request.form["nbk_id"]).first()
    notebook.tags = str(request.form["tags"]).split(',')
    notebook.save()
    return str(notebook.tags)


@edit.route('/nbk_privacy', methods=['POST'])
@login_required
def nbk_privacy():
    # notebook = Notebook.objects(id=request.form["nbk_id"]).first()
    # notebook.public = not request.form["public"]
    # notebook.save()
    return not request.form["public"]


@edit.route('/nbk_notes', methods=['POST'])
@login_required
# @csrf.exempt
def nbk_notes():
    notebook = Notebook.objects(id=request.form["pk"]).first()
    notebook.notes = request.form["value"]
    notebook.save()
    return str(notebook.name)


@edit.route('/all_tags', methods=['GET'])
@login_required
def all_tags():
    return Notebook.objects.item_frequencies('tags', normalize=True).keys()
