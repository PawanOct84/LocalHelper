import time
import re
import os
from pywebio.platform.flask import webio_view
from pywebio import STATIC_PATH
from flask import Flask, send_from_directory
from pywebio.input import *
from pywebio.output import *
import argparse
from pywebio import start_server
import pickle
import numpy as np
from googletrans import constants

app = Flask(__name__)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="./google.json"
sampleText = r""" # Localization Helper
        *****Please follow the below format*****
        "login_userid_text" = "User ID";
        "login_pin_text" = "PIN";
        "login_login_button" = "Login";
        "login_signup_text" = "Sign up";
        """

def processText(languageCode,sourceText):
    iterator = re.finditer(r'"(.*?)"', sourceText)
    *_, last = iterator 
    textToTranste = last.group().replace('"','')
    translatedText = translate_text(languageCode,textToTranste)
    result = sourceText[0:last.start()+1] + translatedText + sourceText[last.end()-1: ]
    return result

def showHomePage():
    put_markdown(sampleText)
    info = input_group("Localization info",[
    radio("Select platform", options=['iOS', 'Android'],name='platform',required=True),
    select("Select language", options=constants.LANGUAGES.values(), name='language',required=True),
    textarea('Enter localization text', code={
    'mode': "python",
    'theme': 'darcula'
    }, name='source', rows=30, help_text="")
    ])

    platform = info['platform']
    language = info['language']
    languageCode = "ar"
    source = info['source'].splitlines() # List with stripped line-breaks
    languageCode = [k for k, v in constants.LANGUAGES.items() if v == language][0]
    translations = ""
    for line in source:
        try:
            result = processText(languageCode,line)
            if len(result) > 0:
                translations = translations + result
                translations = translations + "\n"
        except:
            print("An exception occurred")
        
    put_scrollable(put_scope('scrollable'), height=500, keep_bottom=True)
    put_text("You can copy this result.", scope='scrollable')
    put_text(translations, scope='scrollable')
   

def translate_text(target, text):
    import six
    from google.cloud import translate_v2 as translate
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    result = translate_client.translate(text, target_language=target)
    return result["translatedText"]
   

app.add_url_rule('/tool', 'webio_view', webio_view(showHomePage),
            methods=['GET', 'POST', 'OPTIONS'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=8080)
    args = parser.parse_args()
    start_server(showHomePage, port=args.port)

