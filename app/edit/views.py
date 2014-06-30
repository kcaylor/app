import json
from flask.ext.login import login_required
from flask import request
from . import edit
from ..models import Pod


@edit.route('/nbk_name', methods=['POST'])
@login_required
def nbk_name():
    # pod = Pod.objects(id=request.form["pk"])
    # pod.nbk_name = request.form["value"]
    # result = {}
    # pod.save()
    # return json.dumps(result)
    return request.form["pk"]
