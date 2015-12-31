#!/usr/bin/env python

import latexbot
import flask
from flask import Flask, request, make_response
from flask_restful import reqparse
import json
from flask.ext.api import status
import threading
import requests
import os

class ImageUpload:
    def __init__(self, args_dict):
        thread = threading.Thread(target=self.run)
        self.args = args_dict
        thread.start()

    def run(self):
        args = self.args
        name = args['user_id']
        text = args['text']
        command = args['command']
        path = latexbot.tmp_dir + "/" + name + "/" + name + ".png"
        if latexbot.create_image(text, name):
            image_data = latexbot.upload_image(path)
            image_url = str(image_data["link"])
            resp = {"response_type": "in_channel", "text": "I've LaTeXed it for you","attachments":[{"text": command + ' ' + text, "image_url": image_url}]}
        else:
            log_file = path[:-4] + ".log"
            if os.path.exists(log_file):
                error_text = ""
                with open(path[:-4] + ".log", "r") as f:
                    lines = f.readlines()
                for item in lines:
                    if item[0] == "!":
                        if lines.index(item) + 1 < len(lines):
                            error_text += item + lines[lines.index(item) + 1]
                        break
            else:
                error_text = "Sorry, something went wrong. Let @gwg know."
            resp = {"text": error_text}
            print error_text
        requests.post(args['response_url'], json=resp)
        latexbot.cleanup(name)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def parse_request():
    parser = reqparse.RequestParser()
    # request.get_data()
    # data = request.data
    arg_list = ['text','token','channel_id','response_url', 'user_id', 'command']
    for item in arg_list:
        parser.add_argument(item)
    args = parser.parse_args()
    if args['text'].find("write18") > -1:
        resp = {"text": "Illegal command. I can't run that for security reasons."}
        return flask.jsonify(resp)
    # name = args['user_id']
    # text = args['text']
    # latexbot.create_image(text, name)
    # path = latexbot.tmp_dir + "/" + name + "/" + name + ".png"
    # image_data = latexbot.upload_image(path)
    # image_url = str(image_data["link"])
    resp = {"response_type": "in_channel"}
    # return flask.jsonify(resp)
    thread = ImageUpload(args)
    return flask.jsonify(resp)

app.run(host='0.0.0.0', port=5500)
