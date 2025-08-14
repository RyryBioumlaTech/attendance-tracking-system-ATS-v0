from flask import render_template, jsonify, request
from app.qr_code import qr_code_bp
from app.signature import generate_signature, compare_signature
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app.models import Employee, Checkpoints, Type, db
from io import BytesIO
import base64, secrets
import qrcode
import json

used_nonces = set()

def generate_qr_base64():
    # Generate the current timestamp and create a signature
    moment = datetime.now().isoformat()
    nonce = secrets.token_hex(16)
    signature_input = json.dumps({"moment":moment, "nonce":nonce}, separators=(',',':'), sort_keys=True)
    signature = generate_signature(signature_input)
    data = {
        "moment" : moment,
        "nonce" : nonce,
        "signature" : signature
    }

    json_data = json.dumps(data, sort_keys=True)

    # Create a QR code with the signature
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(json_data)
    qr.make(fit=True)

    # Create an image from the QR code and convert it to base64
    img = qr.make_image(fill_color="black", back_color="white")
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    # Encode the image to base64
    return base64.b64encode(img_io.getvalue()).decode('utf-8')

#SAVE QR DATA
def saveCheckpoints(moment_recieved, employee_id):

    today = date.today()

    today_min = datetime.combine(today, datetime.min.time())
    today_max = datetime.combine(today, datetime.max.time())

    type_in = Type.query.filter_by(value="IN").first()
    type_out = Type.query.filter_by(value="OUT").first()

    checkpoint_in = Checkpoints.query.join(Type).filter(
        Checkpoints.employee_id==employee_id, # type: ignore
        Checkpoints.moment<=today_max,
        Checkpoints.moment>=today_min,
        Type.value=="IN" 
    ).all()

    checkpoint_out = Checkpoints.query.join(Type).filter(
        Checkpoints.employee_id==employee_id, # type: ignore
        Checkpoints.moment<=today_max,
        Checkpoints.moment>=today_min,
        Type.value=="OUT" 
    ).all()

    if(checkpoint_in):
        if(checkpoint_out):
            check_id = checkpoint_out[-1]
            check_id.moment =  moment_recieved
            db.session.commit()
        else:
            new_checkpoint = Checkpoints(moment=moment_recieved, employee_id=employee_id, type_id=type_out.id) # type: ignore
            db.session.add(new_checkpoint)
            db.session.commit()
    else:
        new_checkpoint = Checkpoints(moment=moment_recieved, employee_id=employee_id, type_id=type_in.id) # type: ignore
        db.session.add(new_checkpoint)
        db.session.commit()

@qr_code_bp.route('/qr_code')
def show():
    img_base64 = generate_qr_base64()
    return render_template('qr_code.html', qr_code=img_base64)

@qr_code_bp.route('/qr_update')
def updateQr():
    img_base64 = generate_qr_base64()
    return jsonify({'qr': img_base64})

@qr_code_bp.route('/scan', methods=["POST"])
@login_required
def validate():

    from app import socketio
    
    data_recieved = request.get_json()
    moment_recieved = data_recieved.get("moment")
    nonce_recieved = data_recieved.get("nonce")
    recieved = data_recieved.get("signature")

    employee_id = current_user.id
    employee_name = current_user.name

    # create the expected signature to compare to the reicieved one
    expected_input = json.dumps({"moment":moment_recieved, "nonce":nonce_recieved}, separators=(',',':'), sort_keys=True)
    expected = generate_signature(expected_input)

    timestamp_recieved = datetime.fromisoformat(moment_recieved)
    current_timestamp = datetime.now()

    print('la signature est bonne ? ', compare_signature(recieved, expected), ' et le temps est valide ? ', current_timestamp - timestamp_recieved < timedelta(minutes=1), ' est deja enregistré ? ', nonce_recieved in used_nonces)

    if (compare_signature(recieved, expected) and current_timestamp - timestamp_recieved < timedelta(minutes=1)):

        used_nonces.add(nonce_recieved)

        saveCheckpoints(moment_recieved, employee_id)

        socketio.emit("qr_validated", {"name": employee_name})

        return jsonify({"valid":True})
    else:
        return jsonify({"valid":False})
    
