import os
import subprocess
import shutil
from slacker import Slacker
from imgurpython import ImgurClient
import websocket
from defaults import auth_token, client_id, client_secret
import requests
from requests.auth import HTTPBasicAuth
from configobj import ConfigObj
from time import sleep

conf = ConfigObj("latexit.conf")

slack = Slacker(conf["Slack"]["auth_token"])
count = 1

while count < 5:
    try:
        client = ImgurClient(conf["Imgur"]["client_id"], conf["Imgur"]["client_secret"])
        break
    except:
        count += 1
        sleep(5)

if count == 5:
    print("Couldn't connect to Imgur")


tmp_dir = "/tmp/latexbot"

if not os.path.isdir(tmp_dir):
    if os.path.exists(tmp_dir):
        try:
            os.remove(tmp_dir)
        except:
            print("Cannot create temp dir" + tmp_dir)
            exit(1)
    else:
        os.mkdir(tmp_dir)

def gen_tex_text(text):
    path = os.path.dirname(__file__) + "/"
    with open(path + "contents.txt", "r") as f:
        contents = f.read()
    contents += text
    contents += "$\n\\end{document}\n"
    return contents

def gen_tex_file(text, name):
    f_name = name + ".tex"
    try:
        os.mkdir(tmp_dir + "/" + name)
    except:
        pass
    with open(tmp_dir + "/" + name + "/" + f_name, "w") as f:
        f.write(text)

def generate_png(name):
    f_name = name + ".tex"
    directory = tmp_dir + "/" + name + "/"
    command = "arara "
    if subprocess.call("cd " + directory + " && " + command + f_name, shell=True):
        return False
    else:
        return True

def cleanup(name):
    shutil.rmtree(tmp_dir + "/" + name)

def create_image(text, name):
    gen_tex_file(gen_tex_text(text), name)
    return generate_png(name)

def upload_image(path):
    return client.upload_from_path(path)

def gen_attachment_json(url):
    return [{"text": "LaTeX", "image_url": url}]

def post_message(channel, path):
    image_data = upload_image(path)
    image_url = str(image_data["link"])
    att = gen_attachment_json(image_url)
    slack.chat.post_message(text="I've LaTeXed that for you", channel=channel, attachments=att)

def is_latex(message):
    if message[:7] == "latexit":
        return True
    else:
        return False

def on_message(ws, message):
    message = eval(message)
    if message["type"] == "message":
        text = message["text"]
        if is_latex(text):
            name = message["ts"]
            tex_text = text[7:]
            if tex_text.find("\write18") > -1:
                return False
            create_image(tex_text, name)
            dir_path = tmp_dir + "/" + name
            post_message(message["channel"], dir_path + "/" + name + ".png")
            cleanup(name)


if __name__ == "__main__":
    rtm_link = slack.rtm.start().body["url"]
    ws = websocket.WebSocketApp(rtm_link, on_message=on_message)
    ws.run_forever()
