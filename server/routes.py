from flask import jsonify, request, Response, send_file, abort
from . import app, db
from .amqp_connectivity import administrative_channel
from .models import Area, AreaState
from .tasks import create_database_task
from .task_utils import enqueue_with_retries
from shared import Database
from shared.amqp_queue_naming import get_client_queue_name

@app.route("/api/areas", methods=["GET"])
def areas():
    return jsonify([area.json_dict for area in Area.query.order_by(Area.name)])

@app.route("/api/areas", methods=["POST"])
def maybe_create_area():
    json_body = request.get_json()
    if json_body and isinstance(json_body, dict):
        name = json_body.get("name", None)
    if not json_body or not name:
        abort(400)
    area = Area.query.filter_by(name=name).first()
    if area:
        return jsonify(area.json_dict)
    else:
        area = Area(name=name)
        db.session.add(area)
        db.session.commit()
        resp = jsonify(area.json_dict)
        resp.status_code = 201
        enqueue_with_retries(create_database_task, area_name=name)
        return resp

@app.route("/api/areas/<area_name>")
def area_detail(area_name):
    area = Area.query.filter_by(name=area_name).first_or_404()
    return jsonify(area.json_dict)

@app.route("/api/areas/<area_name>/download")
def download_area_data(area_name):
    if "client_id" not in request.args:
        abort(400)
    area = Area.query.filter_by(name=area_name).first_or_404()
    if area.state in {AreaState.creating, AreaState.applying_changes}:
        # We can not guarantee data integrity in those cases. The database is incomplete, or the client could get partial changes from the queue or none at all.
        abort(400)
    else:
        with administrative_channel() as chan:
            queue_name = get_client_queue_name(request.args["client_id"], area)
            chan.queue_declare(queue_name, durable=True)
            chan.queue_bind(queue=queue_name, exchange=area_name)
        return send_file(Database.get_database_file(area_name))

@app.route("/api/ping")
def ping():
    return jsonify(dict(reply="pong"))