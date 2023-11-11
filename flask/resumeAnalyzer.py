import os
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from pdfminer.high_level import extract_text
import io, random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
import pafy #youtube related supposedly

uploads_folder = 'uploads'
for filename in os.listdir(uploads_folder):
    if filename.endswith('.pdf'):
        file_path = os.path.join(uploads_folder, filename)
        data = ResumeParser(file_path).get_extracted_data
