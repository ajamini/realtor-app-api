from time import sleep

import pandadoc_client
from pandadoc_client.model.document_create_request_recipients import DocumentCreateRequestRecipients
from pandadoc_client import ApiClient, Configuration
from pandadoc_client.api import documents_api
from pandadoc_client.model.document_send_request import DocumentSendRequest
from pandadoc_client.model.document_create_request import DocumentCreateRequest


# place your api key here
API_KEY = ''
MAX_CHECK_RETRIES = 5


def create_document_from_sample_template_pdf_url(api_instance, file_url, signers):

    recipients = []
    for signer in signers:
        recipients.append(DocumentCreateRequestRecipients(
            email=signer['email'],
            first_name=signer['firstname'],
            last_name=signer['lastname'],
            role=signer['role']
        ))

    # [
    #     DocumentCreateRequestRecipients(
    #         email='r.afghanz@gmail.com',
    #         first_name='rafghan',
    #         last_name='gmail',
    #         role='user'
    #     ),
    #     DocumentCreateRequestRecipients(
    #         email='iraj.amini@outlook.com',
    #         first_name='rafghan',
    #         last_name='gmail',
    #         role='user2'
    #     ),
    # ],

    document_create_request = DocumentCreateRequest(
        name='Sample Document from PDF with Field Tags',
        url=file_url,
        recipients=recipients,
        fields={},
        metadata={},
        parse_form_fields=True,
    )

    return api_instance.create_document(document_create_request=document_create_request)


def ensure_document_created(api_instance, document):
    # Document creation is non-blocking (asynchronous) operation.
    #
    # With a successful request, you receive a response with the created
    # document's ID and status document.uploaded.
    # After processing completes on our servers, usually a few seconds,
    # the document moves to the document.draft status.
    # Please wait for the webhook call or check this document's
    # status before proceeding.
    #
    # The change of status from document.uploaded to another status signifies
    # the document is ready for further processing.
    # Attempting to use a newly created document before PandaDoc servers
    # process it will result in a '404 document not found' response.

    retries = 0
    while retries < MAX_CHECK_RETRIES:
        sleep(2)
        retries += 1

        doc_status = api_instance.status_document(document['id'])
        if doc_status.status == 'document.draft':
            return

    raise RuntimeError('Document was not sent')


def send_document(api_instance, document):
    api_instance.send_document(
        document['id'],
        document_send_request=DocumentSendRequest(
            silent=False, subject='This doc was send via python SDK'
        ),
    )


def  send(file_url, signers):
    cfg = Configuration(api_key={'apiKey': f'API-Key {API_KEY}'})
    # Enter a context with an instance of the API client
    with ApiClient(cfg) as client:
        try:
            api_instance = documents_api.DocumentsApi(client)
            document = create_document_from_sample_template_pdf_url(api_instance, file_url, signers)
            print(f'Document was successfully uploaded:\n{document}')
            ensure_document_created(api_instance, document)
            send_document(api_instance, document)
            print(f'Document was successfully created and sent to the recipients!')
        except pandadoc_client.ApiException as e:
            print(f'{e.status} {e.reason} {e.body}')
