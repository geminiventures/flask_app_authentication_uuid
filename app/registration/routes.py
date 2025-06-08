

from app.registration import bp
from app.registration.logic.registration import registration


@bp.route("/registration", methods=["GET", "POST"])
def register():
    return registration()