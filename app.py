from flask import Flask, render_template
from lemmatizator_stem import lemmatize_all, lemmatize_all_eng
from Preprocess import preprocess_all
from flask import jsonify
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from Make_graph_from_TM import make_graph_big, translate_to_eng
import shutil
import pickle
import ast
from googletrans import Translator
translator = Translator()
import nltk

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def index():
  return render_template('index.html')

# Handle the GET request for node information
@app.route('/node-info/<node_name>', methods=['GET'])
def get_node_info(node_name):
    # Retrieve information based on the node_id (replace with your logic)
    output = 'blah blah blah'
    with open('data/x_train_rus', 'rb') as file:
      text = pickle.load(file)
    output = '<br>'.join(['Line ' + str(i)+': ' + l for i,l in enumerate(text) if node_name in l.split()])
    node_info = 'Node: <b>{node_id}</b><br>Output:<br>{output}'.format(node_id=node_name, output=output) # get_node_information(node_id)
    return node_info

	
# @app.route('/uploader', methods = ['GET', 'POST'])
# def upload_file():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(secure_filename(f.filename))
#       return 'File uploaded successfully'

# @app.route('/uploader2', methods = ['GET', 'POST'])
# def upload_file2():
#    if request.method == 'POST':
#       f = request.files['file']
#       f.save(secure_filename(f.filename))
#       return 'File uploaded successfully'


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        filename = secure_filename(file.filename)
        file.save(filename)
        return 'File uploaded successfully.'


@app.route('/my-link/')
def my_link():
  with open('data/text.txt') as f:
    first_line = f.readline()
  result = translator.translate(first_line, dest='en')
  lang = result.src
  if lang == 'ru':
    lemmatize_all('data/text.txt')
  elif lang == 'en':
    lemmatize_all_eng('data/text.txt')

  return 'Your file is lemmatized, now you can click preprocess.'

@app.route('/my-preprocess/')
def my_preprocess():
    print('I got clicked!')
    # Assuming preprocess_all returns a pandas DataFrame or similar
    data = preprocess_all('data/text.txt', 'data/additional_stopwords.txt').to_dict(orient='records')
    return render_template('preprocess_table.html', data=data)

@app.route("/graph/", methods = ['POST', 'GET'])
def data():
    if request.method == 'POST':
        method = request.form['Method']
        k = request.form['Topics number']
        clear_nodes, clear_links = make_graph_big(method, k)
        shutil.move("graph.json", "static/data/graph.json")
        with open(r'data/clear_nodes', 'w') as fp:
          for item in clear_nodes: fp.write("%s\n" % item)
          print('Done for clear_nodes')
        with open(r'data/clear_links', 'w') as fp:
          for item in clear_links: fp.write("%s\n" % item)
          print('Done for clear_links')
        return render_template('make_graph.html')

@app.route('/my-translate/')
def my_translate():
  clear_nodes = []
  clear_links = []
  with open(r'data/clear_nodes', 'r') as fp:
      for line in fp:
          x = line[:-1]
          clear_nodes.append(ast.literal_eval(x))
  with open(r'data/clear_links', 'r') as fp:
      for line in fp:
          x = line[:-1]
          clear_links.append(ast.literal_eval(x))  
  translate_to_eng(clear_nodes, clear_links)
  shutil.move("graph.json", "static/data/graph.json")
  return render_template('make_graph.html')

if __name__ == '__main__':
  app.run(debug=True)