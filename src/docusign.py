import base64
from os import path

from docusign_esign import EnvelopesApi, RecipientViewRequest, Document, Signer, EnvelopeDefinition, SignHere, Tabs, \
    Recipients, CarbonCopy, ApiClient, DateSigned

ACCESS_TOKEN = 'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQoAAAABAAYABwCA0Wx2T7vaSAgAgF3zvU-72kgCAFNNSMe1fd9MlfT5LOhN9X0VAAEAAAAYAAIAAAAFAAAAHQAAAA0AJAAAADM5ZDYwNTUwLWU2NjgtNDJlNy04MGQwLWY5ZTY1ZDA4MDgwNyIAJAAAADM5ZDYwNTUwLWU2NjgtNDJlNy04MGQwLWY5ZTY1ZDA4MDgwNzcAworit8ywEECTwO4xmJdscDAAAP5EFU-72kg.Vo6D1oOPOzb14MBSeNg6YpiC7ND3Rfo4vI7P42zjOUVTHtFJr1DwNLT3ELIHd9kPBI9daCX7A2GXWn5uy7Oz0yjidfPph8WNg6arR-zKtGH9UrM7L7ieHiGYz599dLjn3eXi9syRfRc22dT2ToqgYSSqa6SnL3CelpjwikxHFNgLL9Fo33zCI5tK1QWk64-Yulj2bv9oHj4eKedQGdrLHtJD7bHmjnhONt3WbwhNkn4Y8j_X1MAjhoxfqKNdQh0JIFFqs7B351vHf0EpU0s58FSheuFXgF2EfOfEi5iI1vBPxxm61bU5RnpDbaEZc6yjmj1RMEd1gREwKCPrRWOT-A'
BASE_PATH = ''
ACCOUNT_ID = 'c112c377-646a-4607-8b03-11f6d01b5959'
DOCS_PATH = ''
KEYPAIR_ID = '1eacd802-9ea7-44d2-80c7-b39d75e34b07'

def send(doc_pdf_path):

    api_client = ApiClient()
    api_client.set_base_path(DS_JWT["authorization_server"])
    api_client.set_oauth_host_name(DS_JWT["authorization_server"])
    private_key = get_private_key(DS_JWT["private_key_file"]).encode("ascii").decode("utf-8")
    jwt_values = get_token(private_key, api_client)

    """
    1. Create the envelope request object
    2. Send the envelope
    """

    # 1. Create the envelope request object
    envelope_definition = make_envelope(doc_pdf_path)
    api_client = create_api_client(base_path=jwt_values["base_path"], access_token=jwt_values["access_token"])
    # 2. call Envelopes::create API method
    # Exceptions will be caught by the calling function
    envelopes_api = EnvelopesApi(api_client)
    results = envelopes_api.create_envelope(account_id=jwt_values["api_account_id"], envelope_definition=envelope_definition)

    envelope_id = results.envelope_id

    return {"envelope_id": envelope_id}


SCOPES = [
    "signature", "impersonation"
]

DS_JWT = {
    "ds_client_id": "39d60550-e668-42e7-80d0-f9e65d080807",
    "ds_impersonated_user_id": "c7484d53-7db5-4cdf-95f4-f92ce84df57d",  # The id of the user.
    "private_key_file": "./docusign.private.key", # Create a new file in your repo source folder named private.key then copy and paste your RSA private key there and save it.
    "authorization_server": "account-d.docusign.com"
}


def get_consent_url():
    url_scopes = "+".join(SCOPES)

    # Construct consent URL
    redirect_uri = "http://localhost:5000/"
    consent_url = f"https://{DS_JWT['authorization_server']}/oauth/auth?response_type=code&" \
                  f"scope={url_scopes}&client_id={DS_JWT['ds_client_id']}&redirect_uri={redirect_uri}"

    return consent_url


def get_token(private_key, api_client):
    # Call request_jwt_user_token method
    token_response = get_jwt_token(private_key, SCOPES, DS_JWT["authorization_server"], DS_JWT["ds_client_id"],
                                   DS_JWT["ds_impersonated_user_id"])
    access_token = token_response.access_token

    # Save API account ID
    user_info = api_client.get_user_info(access_token)
    accounts = user_info.get_accounts()
    api_account_id = accounts[0].account_id
    base_path = accounts[0].base_uri + "/restapi"

    return {"access_token": access_token, "api_account_id": api_account_id, "base_path": base_path}

def get_jwt_token(private_key, scopes, auth_server, client_id, impersonated_user_id):
    """Get the jwt token"""
    api_client = ApiClient()
    api_client.set_base_path(auth_server)
    response = api_client.request_jwt_user_token(
        client_id=client_id,
        user_id=impersonated_user_id,
        oauth_host_name=auth_server,
        private_key_bytes=private_key,
        expires_in=4000,
        scopes=scopes
    )
    return response

def get_private_key(private_key_path):
    """
    Check that the private key present in the file and if it is, get it from the file.
    In the opposite way get it from config variable.
    """
    private_key_file = path.abspath(private_key_path)

    if path.isfile(private_key_file):
        with open(private_key_file) as private_key_file:
            private_key = private_key_file.read()
    else:
        private_key = private_key_path

    return private_key

def create_api_client(base_path, access_token):
    """Create api client and construct API headers"""
    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header(header_name="Authorization", header_value=f"Bearer {access_token}")

    return api_client

def make_envelope(doc_pdf_path):
    """
    Creates envelope
    Document 1: An HTML document.
    Document 2: A Word .docx document.
    Document 3: A PDF document.
    DocuSign will convert all of the documents to the PDF format.
    The recipients" field tags are placed using <b>anchor</b> strings.
    """

    # document 1 (html) has sign here anchor tag **signature_1**
    # document 2 (docx) has sign here anchor tag /sn1/
    # document 3 (pdf)  has sign here anchor tag /sn1/
    #
    # The envelope has two recipients.
    # recipient 1 - signer
    # recipient 2 - cc
    # The envelope will be sent first to the signer.
    # After it is signed, a copy is sent to the cc person.

    # create the envelope definition
    env = EnvelopeDefinition(
        email_subject="Please sign this document set"
    )

    with open(path.join(DOCS_PATH, doc_pdf_path), "rb") as file:
        doc3_pdf_bytes = file.read()
    doc3_b64 = base64.b64encode(doc3_pdf_bytes).decode("ascii")

    document3 = Document(  # create the DocuSign document object
        document_base64=doc3_b64,
        name="Lorem Ipsum",  # can be different from actual file name
        file_extension="pdf",  # many different document types are accepted
        document_id="3"  # a label used to reference the doc
    )
    # The order in the docs array determines the order in the envelope
    env.documents = [document3]

    # Create the signer recipient model
    signer1 = Signer(
        email='r.afghanz@gmail.com',
        name='rafghanz',
        recipient_id="1",
        routing_order="1"
    )
    signer2 = Signer(
        email='af_developer@yahoo.ca',
        name='afdeveloper',
        recipient_id="2",
        routing_order="1"
    )
    # routingOrder (lower means earlier) determines the order of deliveries
    # to the recipients. Parallel routing order is supported by using the
    # same integer as the order for two or more recipients.

    # create a cc recipient to receive a copy of the documents
    # cc1 = CarbonCopy(
    #     email=args["cc_email"],
    #     name=args["cc_name"],
    #     recipient_id="2",
    #     routing_order="2"
    # )

    # Create signHere fields (also known as tabs) on the documents,
    # We"re using anchor (autoPlace) positioning
    #
    # The DocuSign platform searches throughout your envelope"s
    # documents for matching anchor strings. So the
    # signHere2 tab will be used in both document 2 and 3 since they
    # use the same anchor string for their "signer 1" tabs.
    sign_here1 = SignHere(
        anchor_string="\s1\\",
        anchor_units="pixels",
        anchor_y_offset="",
        anchor_x_offset=""
    )

    date_signed = DateSigned(
        anchor_string="\d1\\",
        anchor_units='pixels',
        anchor_y_offset="0",
        anchor_x_offset="0"
    )

    sign_here2 = SignHere(
        anchor_string="\s2\\",
        anchor_units="pixels",
        anchor_y_offset="0",
        anchor_x_offset="0"
    )

    date_signed2 = DateSigned(
        anchor_string="\d2\\",
        anchor_units='pixels',
        anchor_y_offset="0",
        anchor_x_offset="0"
    )

    # Add the tabs model (including the sign_here tabs) to the signer
    # The Tabs object wants arrays of the different field/tab types
    signer1.tabs = Tabs(sign_here_tabs=[sign_here1], date_signed_tabs=[date_signed])
    signer2.tabs = Tabs(sign_here_tabs=[sign_here2], date_signed_tabs=[date_signed2])

    # Add the recipients to the envelope object
    recipients = Recipients(signers=[signer1, signer2])#, carbon_copies=[cc1])
    env.recipients = recipients

    # Request that the envelope be sent by setting |status| to "sent".
    # To request that the envelope be created as a draft, set to "created"
    env.status = 'sent'

    return env