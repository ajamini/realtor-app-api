from flask import Flask, request
from flask_cors import CORS
from spaces import Client
from dotenv import load_dotenv
import time, pdf, os

load_dotenv()

app = Flask(__name__)
CORS(app)

client = Client(
    region_name=os.environ.get('space_region'),
    space_name=os.environ.get('space_name'),
    public_key=os.environ.get('space_public_key'),
    secret_key=os.environ.get('space_secret_key')
)

@app.route("/")
def home():
    return "OK"

@app.route("/generate", methods=['POST'])
def generate():
    # body => {name:100, uuid: asdfafd, fields: {}}
    body = request.get_json()
    form_number = body.name;
    form_uuid = body.uuid;
    form_fields = body.fields;

    base_url = os.environ.get('space_base_url'),


    current_time = int(time.time()*1000)
    template = f"form/{form_number}.pdf"
    filename = f"{form_number}_{current_time}"
    temp_path = f"temp/{filename}.pdf"
    upload_path = f"secure/docs/{form_uuid}"

    pdf.pdf(template, temp_path, form_fields)

    # source = Image(filename=pdf_output, resolution=300)
    # source.save(filename=pdf_flatten)

    client.upload_file(temp_path, destination=upload_path, rename=filename)

    return {
        'filename': filename,
        'path': f"{upload_path}/{filename}",
        'url': f"{base_url}/{upload_path}/{filename}"
    }