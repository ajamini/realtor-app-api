import os.path
from io import BytesIO

import PyPDF2
import pdfrw, time
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, BooleanObject, IndirectObject, NumberObject, createStringObject
from pdfrw import PageMerge, PdfReader as PDFWReader, PdfWriter as PDFRWriter
from fpdf import FPDF

ANNOT_PARENT = '/Parent'
ANNOT_KEY = '/Annots'
ANNOT_FIELD_KEY = '/T'
ANNOT_VAL_KEY = '/V'
ANNOT_RECT_KEY = '/Rect'
ANNOT_FLATTEN = '/Ff'
SUBTYPE_KEY = '/Subtype'
WIDGET_SUBTYPE_KEY = '/Widget'

class FieldFlag(int):
      """TABLE 8.70 Field flags common to all field types"""

      READ_ONLY = 1
      REQUIRED = 2
      NO_EXPORT = 4

def new_content():
      fpdf = FPDF()
      fpdf.add_page()
      fpdf.set_font("helvetica", size=36)
      fpdf.text(50, 50, "Hello!")
      reader = PDFWReader(fdata=bytes(fpdf.output()))
      return reader.pages[0]

def add_signature(pdf, output):
      input_stream = open(pdf, "rb")
      reader = PDFWReader(input_stream, strict=False);
      writer = PDFRWriter()
      print(len(writer.pagearray))
      PageMerge(reader.getPage(0)).add(new_content(), prepend=False).render()
      writer.write(output)
      print(os.path.curdir)
      print(output)
      #
      #
      # input_stream = open(pdf, "rb")
      # pdf_reader = PyPDF2.PdfFileReader(input_stream, strict=False)
      # pdf_writer = PyPDF2.PdfFileWriter()
      #
      # for i in range(0, len(pdf_reader.pages)):
      #       text = pdf_reader.pages[i].extractText()
      #       if text.find('INITIALS OF BUYER(S):'):
      #
      #       print(text)




def replace_fields(pdf, outfile, form_number):

      input_stream = open(pdf, "rb")
      pdf_reader = PyPDF2.PdfFileReader(input_stream, strict=False)
      pdf_writer = PyPDF2.PdfFileWriter()

      for i in range(0, len(pdf_reader.pages)):

            pdf_writer.addPage(pdf_reader.getPage(i))
            page = pdf_writer.getPage(i)

            for j in range(0, len(page['/Annots'])):
                  writer_annot = page['/Annots'][j].getObject()
                  field_name = writer_annot.get('/T').__str__()
                  new_field_name = field_name.replace("810", form_number)
                  print(f'replacing {field_name} with {new_field_name}')
                  writer_annot.update({
                        NameObject("/T"): createStringObject(new_field_name)
                  })

      pdf_writer.write(outfile)

      return True

def empty():
      writer = PyPDF2.PdfFileWriter()
      set_need_appearances_writer(writer)
      if "/AcroForm" in writer._root_object:
            # Acro form is form field, set needs appearances to fix printing issues
            writer._root_object["/AcroForm"].update(
                  {NameObject("/NeedAppearances"): BooleanObject(True)})

      return writer

def append(writer, new_file):
      input_stream = open(new_file, "rb")
      reader = PyPDF2.PdfFileReader(input_stream, strict=False)

      for i in range(0, len(reader.pages)):
            writer.addPage(reader.getPage(i))

def save(writer, outfile):
      writer.write(outfile)


def pdf(template, outfile, data_dict):
      # template = 'templates/template.pdf'
      # outfile = "templates/test.pdf"

      input_stream = open(template, "rb")
      pdf_reader = PyPDF2.PdfFileReader(input_stream, strict=False)
      if "/AcroForm" in pdf_reader.trailer["/Root"]:
            pdf_reader.trailer["/Root"]["/AcroForm"].update(
                  {NameObject("/NeedAppearances"): BooleanObject(True)})

      pdf_writer = PyPDF2.PdfFileWriter()
      set_need_appearances_writer(pdf_writer)
      if "/AcroForm" in pdf_writer._root_object:
            # Acro form is form field, set needs appearances to fix printing issues
            pdf_writer._root_object["/AcroForm"].update(
                  {NameObject("/NeedAppearances"): BooleanObject(True)})

      # data_dict = {
      #       '100-1': 'John\n',
      #       '100-2': 'Smith\n',
      #       '100-3': 'mail@mail.com\n'
      #
      # }

      for i in range(0, len(pdf_reader.pages)):
            pdf_writer.addPage(pdf_reader.getPage(i))
            page = pdf_writer.getPage(i)
            # print(i)
            # print(page)
            pdf_writer.updatePageFormFieldValues(page, data_dict)
            if (ANNOT_KEY in page):
                  for j in range(0, len(page[ANNOT_KEY])):
                        writer_annot = page[ANNOT_KEY][j].getObject()
                        for field in data_dict:
                              # -----------------------------------------------------BOOYAH!
                              if writer_annot.get(ANNOT_FIELD_KEY) == field:
                                    writer_annot.update({
                                          NameObject(ANNOT_FLATTEN): NumberObject(1)
                                    })
                        # -----------------------------------------------------
      #output_stream = BytesIO()
      pdf_writer.write(outfile)

      # response = HttpResponse(output_stream.getvalue(), content_type='application/pdf')
      # response['Content-Disposition'] = 'inline; filename="completed.pdf"'
      # input_stream.close()

      return True


def set_need_appearances_writer(writer):
      try:
            catalog = writer._root_object
            # get the AcroForm tree and add "/NeedAppearances attribute
            if "/AcroForm" not in catalog:
                  writer._root_object.update({
                        NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

            need_appearances = NameObject("/NeedAppearances")
            writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)


      except Exception as e:
            print('set_need_appearances_writer() catch : ', repr(e))

      return writer

def fill_new(input_pdf_path, output_pdf_path, data_dict):
      reader = PdfReader(input_pdf_path)
      writer = PdfWriter()

      page = reader.pages[0]
      #fields = reader.get_fields()

      writer.add_page(page)

      writer.update_page_form_field_values(
            writer.pages[0], data_dict, flags=FieldFlag(FieldFlag.READ_ONLY)
      )

      # write "output" to PyPDF2-output.pdf
      with open(output_pdf_path, "wb") as output_stream:
            writer.write(output_stream)

def fill_old(input_pdf_path, output_pdf_path, data_dict):
      template_pdf = pdfrw.PdfReader(input_pdf_path)
      for page in template_pdf.pages:
            annotations = page[ANNOT_KEY]
            for annotation in annotations:
                  if annotation[SUBTYPE_KEY] == WIDGET_SUBTYPE_KEY:
                        if annotation[ANNOT_FIELD_KEY]:
                              key = annotation[ANNOT_FIELD_KEY][1:-1]
                              if key in data_dict.keys():
                                    if type(data_dict[key]) == bool:
                                          if data_dict[key] == True:
                                                annotation.update(pdfrw.PdfDict(AS=pdfrw.PdfName('X')))
                                    else:
                                          annotation.update(pdfrw.PdfDict(V='{}'.format(data_dict[key]), Ff=1))
                                          annotation.update(pdfrw.PdfDict(AP='', Ff=1))
                        elif annotation[ANNOT_PARENT][ANNOT_FIELD_KEY]:
                              key = annotation[ANNOT_PARENT][ANNOT_FIELD_KEY][1:-1]
                              if key in data_dict.keys():
                                    if type(data_dict[key]) == bool:
                                          if data_dict[key] == True:
                                                annotation[ANNOT_PARENT].update(pdfrw.PdfDict(AS=pdfrw.PdfName('X')))
                                    else:
                                          annotation[ANNOT_PARENT].update(pdfrw.PdfDict(V='{}'.format(data_dict[key]), Ff=1))
                                          annotation[ANNOT_PARENT].update(pdfrw.PdfDict(AP='', Ff=1))
      template_pdf.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
      pdfrw.PdfWriter().write(output_pdf_path, template_pdf)

if __name__ == '__main__':
      pdf('form/FORM_801.pdf', 'test.pdf', {})