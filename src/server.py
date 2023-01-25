from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from spaces import Client
from pathlib import Path
import time, pdf, pandadoc, os, panda_template, docusign
import pypdftk
from wand.image import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfFileWriter, PdfFileReader

app = Flask(__name__)
CORS(app)

client = Client(
    region_name='sfo3',
    space_name='xcii-legacy-prod',
    public_key='DO002DY74UZ7NNGQQQNP',
    secret_key='j+GnFpWvnfMU9HGj8NdllcK1VoCFd3qE0Dy6Zh05mm8'
)

mappings = {
    '100-1': {
        'transform': '',
        'field': 'address1'
    },
    '100-2': {
        'transform': 'get_date',
        'field': 'offer_date'
    },
    '100-3': {
        'transform': 'get_month_fullstring',
        'field': 'offer_date'
    },
    '100-4': {
        'transform': 'get_year_last2digit',
        'field': 'offer_date'
    },
    '100-5': {
        'transform': '',
        'field': 'buyer_brokerage_name'
    },
    '100-6': {
        'transform': '',
        'field': 'buyer_broker_name'
    },
    '100-7': {
        'transform': '',
        'field': 'buyer1'
    },
    '100-8': {
        'transform': '',
        'field': 'buyer2'
    },
    '100-9': {
        'transform': 'get_date_mmddyyyy',
        'field': 'offer_date'
    },
    '100-10': {
        'transform': '',
        'field': 'sent_through'
    },
    '100-11': {
        'transform': 'get_hour',
        'field': 'sent_date'
    },
    '100-12': {
        'transform': 'get_am_pm',
        'field': 'sent_date'
    },
    '100-13': {
        'transform': 'get_date',
        'field': 'sent_date'
    },
    '100-14': {
        'transform': 'get_month_fullstring',
        'field': 'sent_date'
    },
    '100-15': {
        'transform': 'get_year_last2digit',
        'field': 'sent_date'
    },
    '100-16': {
        'transform': 'get_hour',
        'field': 'irrevocable_date'
    },
    '100-17': {
        'transform': 'get_am_pm',
        'field': 'irrevocable_date'
    },
    '100-18': {
        'transform': 'get_date',
        'field': 'irrevocable_date'
    },
    '100-19': {
        'transform': 'get_month_fullstring',
        'field': 'irrevocable_date'
    },
    '100-20': {
        'transform': 'get_year_last2digit',
        'field': 'irrevocable_date'
    },
    '100-21': {
        'transform': '',
        'field': 'seller1'
    },
    '100-22': {
        'transform': '',
        'field': 'seller2'
    },
    '100-23': {
        'transform': '',
        'field': 'listing_brokerage_name'
    },
    '100-24': {
        'transform': '',
        'field': 'listing_broker_name'
    }
}

class Tranformers:
    def get_year_last2digit(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%y')

    def get_month_fullstring(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%B')

    def get_date(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%d')

    def get_am_pm(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%p')

    def get_hour(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%I')

    def get_date_mmddyyyy(self, value):
        obj = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        return obj.strftime('%m/%d/%Y')



@app.route("/")
def home():
    return "OK"

@app.route("/send", methods=['POST'])
def send():
    body = request.get_json()
    url = body['file_url']
    signers = [
        {
            'email': body['signer_email'],
            'firstname': body['signer_name'].split(' ')[0],
            'lastname': body['signer_name'].split(' ')[1],
            'role': 'user'
        },
        {
            'email': body['signer2_email'],
            'firstname': body['signer2_name'].split(' ')[0],
            'lastname': body['signer2_name'].split(' ')[1],
            'role': 'user2'
        },
    ]

    pandadoc.send(url, signers)

    return {"success": True}

@app.route("/signature")
@cross_origin()
def signature():
    file = request.args['file']
    # output = 'signature_add.pdf'
    #
    # pdf.add_signature(file, output)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(10, 100, "{s:user1:__}")
    can.drawString(100, 100, "{d:user1:__}")
    can.drawString(10, 200, "{s:user2:__}")
    can.drawString(100, 200, "{d:user2:__}")
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(file, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    pdf_output = "destination.pdf"
    outputStream = open(pdf_output, "wb")
    output.write(outputStream)
    outputStream.close()

    client.upload_file(pdf_output, destination='output/', rename='destination', extra_args={'ACL': 'public-read'})

    signers = [
        {
            'email': 'af_developer@yahoo.ca',
            'firstname': 'iraj',
            'lastname': 'amini',
            'role': 'user1'
        },
        {
            'email': 'r.afghanz@gmail.com',
            'firstname': 'rafghan',
            'lastname': 'amini',
            'role': 'user2'
        },
    ]

    pandadoc.send(f'https://xcii-legacy-prod.sfo3.digitaloceanspaces.com/output/{pdf_output}', signers)

    return {"url": True}


@app.route("/signature/docusign")
@cross_origin()
def signatureDocu():
    file = request.args['file']
    # output = 'signature_add.pdf'
    #
    # pdf.add_signature(file, output)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.drawString(10, 100, "\s1\\")
    can.drawString(100, 100, "\d1\\")
    can.drawString(10, 200, "\s2\\")
    can.drawString(100, 200, "\d2\\")
    can.save()

    #move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(file, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    pdf_output = "destination.pdf"
    outputStream = open(pdf_output, "wb")
    output.write(outputStream)
    outputStream.close()


    signers = [
        {
            'email': 'af_developer@yahoo.ca',
            'firstname': 'iraj',
            'lastname': 'amini',
            'role': 'user1'
        },
        {
            'email': 'r.afghanz@gmail.com',
            'firstname': 'rafghan',
            'lastname': 'amini',
            'role': 'user2'
        },
    ]

    docusign.send(pdf_output)

    return {"url": True}

@app.route("/doc/generate/<form_number>", methods=['POST'])
def generate(form_number):
    body = request.get_json()
    current_time = int(time.time()*1000)
    transformer = Tranformers()

    # mapping_new = {}
    # for i in range(1,100):
    #     field_name = '100-' + i.__str__()
    #     mapping_new[field_name] = {
    #         'transform': '',
    #         'field': field_name
    #     }
    #
    #     body[field_name] = field_name
    #
    # for i in [30,31,32,33,34,35,36,37,38,13,12,11]:
    #     field_name = '100-' + i.__str__()
    #     body[field_name] = "/Yes"

    # data = {}
    # for f in mapping:
    #     field = mapping_new[f]['field']
    #     transform = mapping_new[f]['transform']
    #     value = ''
    #
    #     if field in body:
    #         if transform:
    #             value = getattr(transformer, transform)(body[field])
    #         else:
    #             value = body[field]
    #
    #     data[f] = value
    #
    print(body)

    pdf_template = f"form/FORM_{form_number}.pdf"
    pdf_filename = f"form_{form_number}_{current_time}"
    pdf_output = f"{pdf_filename}.pdf"
    pdf_flatten = f"flatten-{pdf_output}"

    #client.download_file(file_name=pdf_template, destination='')
    pdf.pdf(pdf_template, pdf_output, body)

    # source = Image(filename=pdf_output, resolution=300)
    # source.save(filename=pdf_flatten)

    client.upload_file(pdf_output, destination='output/', rename=pdf_filename, extra_args={'ACL': 'public-read'})

    return {"file_url": f'https://xcii-legacy-prod.sfo3.digitaloceanspaces.com/output/{pdf_output}'}


@app.route("/rename_fields/<form_number>")
@cross_origin()
def renamed(form_number):
    input = f'form/FORM_{form_number}.pdf'
    output = f'form/FORM_{form_number}_renamed.pdf'

    pdf.replace_fields(input, output, form_number)

    return {"url": output}



@app.route("/merge", methods=['POST'])
@cross_origin()
def merge():
    body = request.get_json()
    filenames = body['files']

    empty = pdf.empty()
    for file in filenames:
        client.download_file(file_name=file, destination='./')
        pdf.append(empty, file)

    current_time = int(time.time()*1000)
    filename = f"merged-{current_time}"
    outfile = f"{filename}.pdf"
    pdf.save(empty, outfile)

    client.upload_file(outfile, destination='output/', rename=filename, extra_args={'ACL': 'public-read'})
    return {"url": f'https://xcii-legacy-prod.sfo3.digitaloceanspaces.com/output/{outfile}'}


@app.route("/gensend/<form_number>", methods=['POST'])
@cross_origin()
def generate_send(form_number):
    body = request.get_json()
    current_time = int(time.time()*1000)
    transformer = Tranformers()

    data = {}
    for f in mappings:
        field = mappings[f]['field']
        transform = mappings[f]['transform']
        value = ''

        if field in body:
            if transform:
                value = getattr(transformer, transform)(body[field])
            else:
                value = body[field]

        data[f] = value


    pdf_template = f"form/form-{form_number}.pdf"
    pdf_filename = f"form_{form_number}_{current_time}"
    pdf_output = f"{pdf_filename}.pdf"
    pdf_flatten = f"flatten-{pdf_output}"

    client.download_file(file_name=pdf_template, destination='')
    pdf.pdf(pdf_template, pdf_output, body)

    source = Image(filename=pdf_output, resolution=300)
    source.save(filename=pdf_flatten)

    client.upload_file(pdf_output, destination='output/', rename=pdf_filename, extra_args={'ACL': 'public-read'})
    #
    # pandadoc.send(f'https://xcii-legacy-prod.sfo3.digitaloceanspaces.com/output/{pdf_output}')

    #docusign.send(pdf_flatten)

    return {"success": True}


@app.route("/redirect_url")
def redirect_url():
    return {"url": docusign.get_consent_url()}