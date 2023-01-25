from time import sleep

import pandadoc_client
from pandadoc_client.model.document_create_request_content_library_items import \
    DocumentCreateRequestContentLibraryItems
from pandadoc_client.model.document_create_request_content_placeholders import \
    DocumentCreateRequestContentPlaceholders
from pandadoc_client.model.document_create_request_images import DocumentCreateRequestImages
from pandadoc_client.model.document_create_by_template_request_tokens import \
    DocumentCreateByTemplateRequestTokens
from pandadoc_client.model.document_create_request_recipients import DocumentCreateRequestRecipients
from pandadoc_client.model.document_create_request import DocumentCreateRequest
from pandadoc_client.model.document_send_request import DocumentSendRequest
from pandadoc_client import ApiClient, Configuration
from pandadoc_client.api import documents_api
from pandadoc_client.model.pricing_table_request import PricingTableRequest
from pandadoc_client.model.pricing_table_request_row_options import PricingTableRequestRowOptions
from pandadoc_client.model.pricing_table_request_rows import PricingTableRequestRows
from pandadoc_client.model.pricing_table_request_sections import (
    PricingTableRequestSections,
)


# place your api key here
API_KEY = 'b85951a80284ccd36cc3a657147e7af9d6a6fb6f'
#
# you should have a several onboarding CLIs in your workspace
# just place an ID of any
CONTENT_LIBRARY_ITEM_ID = 'YOUR_CONTENT_LIBRARY_ITEM_ID'

MAX_CHECK_RETRIES = 5


def create_doc_from_sample_template(api_instance, template_uuid, data):

    document_create_request = DocumentCreateRequest(
        name='API Sample Document from PandaDoc Template',
        template_uuid=template_uuid,
        # specify a folder uuid if you want to document to be created
        # in specific folder otherwise it will be created in root directory
        #
        # folder_uuid='QMDSzwabfFzTgjW4kUijqQ',
        recipients=[
            DocumentCreateRequestRecipients(
                email='r.afghanz@gmail.com',
                first_name='Josh',
                last_name='Ron',
                role="Role 1",
                signing_order=2,
            ),
            DocumentCreateRequestRecipients(
                email='iraj.amini@outlook.com',
                first_name='Iraj',
                last_name='Ron',
                role="Role 2",
                signing_order=1,
            ),
        ],
        #tokens=[DocumentCreateByTemplateRequestTokens(name='Favorite.Pet', value='Panda')],
        fields=data,
        metadata={},
        tags=['created_via_api', 'test_document'],
        # images=[
        #     DocumentCreateRequestImages(
        #         urls=[
        #             'https://s3.amazonaws.com/pd-static-content/public-docs/pandadoc-panda-bear.png',
        #         ],
        #         name='Image 1',
        #     ),
        # ],
        #pricing_tables=pricing_tables,
        # content_placeholders=[
        #     DocumentCreateRequestContentPlaceholders(
        #         block_id='Content Placeholder 1',
        #         content_library_items=[
        #             DocumentCreateRequestContentLibraryItems(
        #                 id=CONTENT_LIBRARY_ITEM_ID,
        #                 pricing_tables=pricing_tables,
        #             ),
        #         ],
        #     ),
        # ],
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


def send(template_uuid, data):
    cfg = Configuration(api_key={'apiKey': f'API-Key {API_KEY}'})
    # Enter a context with an instance of the API client
    with ApiClient(cfg) as client:
        try:
            api_instance = documents_api.DocumentsApi(client)
            document = create_doc_from_sample_template(api_instance, template_uuid, data)
            print(f'Document was successfully uploaded:\n{document}')
            ensure_document_created(api_instance, document)
            send_document(api_instance, document)
            print(f'Document was successfully created and sent to the recipients!')
        except pandadoc_client.ApiException as e:
            print(f'{e.status} {e.reason} {e.body}')
