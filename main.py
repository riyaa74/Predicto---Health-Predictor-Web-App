from flask import Flask, render_template, request, redirect, url_for, session , flash, redirect
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import numpy as np
import sys
import os
import glob
import json
from datetime import datetime


# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image
# Flask utils
from flask import Flask, redirect, url_for, request, render_template
from werkzeug.utils import secure_filename
from gevent.pywsgi import WSGIServer


app = Flask(__name__)

app.secret_key = 'Yolo@6969'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rajada123@'
app.config['MYSQL_DB'] = 'final_project'

mysql = MySQL(app)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))

        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['username']

            return redirect(url_for('home'))
    
        else:
            msg = 'Incorrect username/password'

    return render_template('index.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)

    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''

    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'age' in request.form and 'gender' in request.form and 'height' in request.form and 'weight' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        gender = request.form['gender']
        height = request.form['height']
        weight = request.form['weight']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email or not age or not gender or not height or not weight:
            msg = 'Please fill out the form completely!'
        elif int(age)<0 or int(height)<0 or int(weight)<0:
            msg="Please enter correct input"
        else:
            cursor.execute('INSERT INTO accounts VALUES (%s, %s, %s, %s, %s, %s, %s)', (username, password, email, age, gender, height, weight))
            mysql.connection.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form completely!'
    
    return render_template('register.html', msg=msg)

def addPredHistory(disease_bool, disease_name):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    date_today = datetime.today().strftime('%d-%m-%Y')
    if disease_bool == 1:
        cursor.execute('INSERT INTO prediction_history (username, disease_name, prediction, prediction_date) VALUES (%s, %s, %s, %s)', (str(session['username']), disease_name, 'Positive', date_today))
        mysql.connection.commit()
    else:
        cursor.execute('INSERT INTO prediction_history (username, disease_name, prediction, prediction_date) VALUES (%s, %s, %s, %s)', (str(session['username']), disease_name, 'Negative', date_today))
        mysql.connection.commit()

def predict(values, dic):
    if len(values) == 8:
        print("entered if")
        model = pickle.load(open('models/diabetes.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Diabetes')
        return temp
    elif len(values) == 26:
        model = pickle.load(open('models/breast_cancer.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Breast Cancer')
        return temp
    elif len(values) == 13:
        model = pickle.load(open('models/heart.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Liver Disease')
        return temp
    elif len(values) == 18:
        model = pickle.load(open('models/kidney.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Kidney Disease')
        return temp
    elif len(values) == 10:
        model = pickle.load(open('models/liver.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Liver Disease')
        return temp
    elif len(values) == 15:
        model = pickle.load(open('models/lung_cancer.pkl','rb'))
        values = np.asarray(values)
        temp = model.predict(values.reshape(1, -1))[0]
        addPredHistory(temp, 'Lung Cancer')
        return temp
    elif len(values) == 404:
        model = pickle.load(open('models/AllDiseases.pkl','rb'))
        values = np.asarray(values)
        p = model.predict(values.reshape(1, -1))[0]
        addPredHistory(1, p.title())
        return p


@app.route('/home', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        username = session['username']
        name = request.form['name']
        email = request.form['email']
        date = request.form['date']
        department = request.form['department']
        phone = request.form['phone']
        message = request.form['message']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO appointment (username, full_name, email, appointment_date, department, phone_number, additional_message) VALUES (%s, %s, %s, %s, %s, %s, %s)',
         (username, name, email, date, department, phone, message))
        mysql.connection.commit()

        return redirect(url_for('home'))


    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (session['username'],))
        account = cursor.fetchone()
        cursor.execute('SELECT * FROM prediction_history WHERE username = %s', (session['username'],))
        prediction_history = cursor.fetchall()
        return render_template('profile.html', account=account, prediction_history=prediction_history)
    return redirect(url_for('login'))
    
@app.route('/news-detail')
def news_detail():
    if 'loggedin' in session:
        return render_template('news-detail.html')
    return redirect(url_for('login'))

        
@app.route('/diabetes-prediction', methods=['GET', 'POST'])
def diabetes_prediction():
    if 'loggedin' in session:
        return render_template('DiabetesPrediction.html')
    return redirect(url_for('login'))  


@app.route('/maleria-prediction', methods=['GET', 'POST'])
def maleria_prediction():
    if 'loggedin' in session:
        return render_template('MaleriaPrediction.html')
    return redirect(url_for('login'))

@app.route('/breast-cancer-prediction', methods=['GET', 'POST'])
def breast_cancer_prediction():
    if 'loggedin' in session:
        return render_template('BreastCancerPrediction.html')
    return redirect(url_for('login'))

@app.route('/heart-disease-prediction', methods=['GET', 'POST'])
def heart_disease_prediction():
    if 'loggedin' in session:
        return render_template('HeartDiseasePrediction.html')
    return redirect(url_for('login'))

@app.route('/kidney-disease-prediction', methods=['GET', 'POST'])
def kidney_disease_prediction():
    if 'loggedin' in session:
        return render_template('KidneyDiseasePrediction.html')
    return redirect(url_for('login'))

@app.route('/liver-disease-prediction', methods=['GET', 'POST'])
def liver_disease_prediction():
    if 'loggedin' in session:
        return render_template('LiverDiseasePrediction.html')
    return redirect(url_for('login'))

@app.route('/lung-cancer-prediction', methods=['GET', 'POST'])
def lung_cancer_prediction():
    if 'loggedin' in session:
        return render_template('LungCancerPrediction.html')
    return redirect(url_for('login'))

@app.route('/pneumonia-prediction', methods=['GET', 'POST'])
def pneumonia_prediction():
    if 'loggedin' in session:
        return render_template('PnemoniaPrediction.html')
    return redirect(url_for('login'))

@app.route('/AllDiseasePrediction', methods=['GET', 'POST'])
def AllDiseasePrediction():
    if 'loggedin' in session:
        symptom_list = ['shortness of breath', 'dizziness', 'asthenia', 'fall', 'syncope', 'vertigo', 'sweat', 'sweating increased', 'palpitation', 'nausea', 'angina pectoris', 'pressure chest', 'polyuria', 'polydypsia', 'pain chest', 'orthopnea', 'rale', 'unresponsiveness', 'mental status changes', 'vomiting', 'labored breathing', 'feeling suicidal', 'suicidal', 'hallucinations auditory', 'feeling hopeless', 'weepiness', 'sleeplessness', 'motor retardation', 'irritable mood', 'blackout', 'mood depressed', 'hallucinations visual', 'worry', 'agitation', 'tremor', 'intoxication', 'verbal auditory hallucinations', 'energy increased', 'difficulty', 'nightmare', 'unable to concentrate', 'homelessness', 'hypokinesia', 'dyspnea on exertion', 'chest tightness', 'cough', 'fever', 'decreased translucency', 'productive cough', 'pleuritic pain', 'yellow sputum', 'breath sounds decreased', 'chill', 'rhonchus', 'green sputum', 'non-productive cough', 'wheezing', 'haemoptysis', 'distress respiratory', 'tachypnea', 'malaise', 'night sweat', 'jugular venous distention', 'dyspnea', 'dysarthria', 'speech slurred', 'facial paresis', 'hemiplegia', 'seizure', 'numbness', 'symptom aggravating factors', 'st segment elevation', 'st segment depression', 't wave inverted', 'presence of q wave', 'chest discomfort', 'bradycardia', 'pain', 'nonsmoker', 'erythema', 'hepatosplenomegaly', 'pruritus', 'diarrhea', 'abscess bacterial', 'swelling', 'apyrexial', 'dysuria', 'hematuria', 'renal angle tenderness', 'lethargy', 'hyponatremia', 'hemodynamically stable', 'difficulty passing urine', 'consciousness clear', 'guaiac positive', 'monoclonal', 'ecchymosis', 'tumor cell invasion', 'haemorrhage', 'pallor', 'fatigue', 'heme positive', 'pain back', 'orthostasis', 'arthralgia', 'transaminitis', 'sputum purulent', 'hypoxemia', 'hypercapnia', 'patient non compliance', 'unconscious state', 'bedridden', 'abdominal tenderness', 'unsteady gait', 'hyperkalemia', 'urgency of\xa0micturition', 'ascites', 'hypotension', 'enuresis', 'asterixis', 'muscle twitch', 'sleepy', 'headache', 'lightheadedness', 'food intolerance', 'numbness of hand', 'general discomfort', 'drowsiness', 'stiffness', 'prostatism', 'weight gain', 'tired', 'mass of body structure', 'has religious belief', 'nervousness', 'formication', 'hot flush', 'lesion', 'cushingoid facies', 'cushingoid\xa0habitus', 'emphysematous change', 'decreased body weight', 'hoarseness', 'thicken', 'spontaneous rupture of membranes', 'muscle hypotonia', 'hypotonic', 'redness', 'hypesthesia', 'hyperacusis', 'scratch marks', 'sore to touch', 'burning sensation', 'satiety early', 'throbbing sensation quality', 'sensory discomfort', 'constipation', 'pain abdominal', 'heartburn', 'breech presentation', 'cyanosis', 'pain in lower limb', 'cardiomegaly', 'clonus', 'unwell', 'anorexia', 'history of - blackout', 'anosmia', 'metastatic lesion', 'hemianopsia homonymous', 'hematocrit decreased', 'neck stiffness', 'cicatrisation', 'hypometabolism', 'aura', 'myoclonus', 'gurgle', 'wheelchair bound', 'left\xa0atrial\xa0hypertrophy', 'oliguria', 'catatonia', 'unhappy', 'paresthesia', 'gravida 0', 'lung nodule', 'distended abdomen', 'ache', 'macerated skin', 'heavy feeling', 'rest pain', 'sinus rhythm', 'withdraw', 'behavior hyperactive', 'terrify', 'photopsia', 'giddy mood', 'disturbed family', 'hypersomnia', 'hyperhidrosis disorder', 'mydriasis', 'extrapyramidal sign', 'loose associations', 'exhaustion', 'snore', 'r wave feature', 'overweight', 'systolic murmur', 'asymptomatic', 'splenomegaly', 'bleeding of vagina', 'macule', 'photophobia', 'painful swallowing', 'cachexia', 'hypocalcemia result', 'hypothermia, natural', 'atypia', 'general unsteadiness', 'throat sore', 'snuffle', 'hacking cough', 'stridor', 'paresis', 'aphagia', 'focal seizures', 'abnormal sensation', 'stupor', 'fremitus', "Stahli's line", 'stinging sensation', 'paralyse', 'hirsutism', 'sniffle', 'bradykinesia', 'out of breath', 'urge incontinence', 'vision blurred', 'room spinning', 'rambling speech', 'clumsiness', 'decreased stool caliber', 'hematochezia', 'egophony', 'scar tissue', 'neologism', 'decompensation', 'stool color yellow', 'rigor - temperature-associated observation', 'paraparesis', 'moody', 'fear of falling', 'spasm', 'hyperventilation', 'excruciating pain', 'gag', 'posturing', 'pulse absent', 'dysesthesia', 'polymyalgia', 'passed stones', 'qt interval prolonged', 'ataxia', "Heberden's node", 'hepatomegaly', 'sciatica', 'frothy sputum', 'mass in breast', 'retropulsion', 'estrogen use', 'hypersomnolence', 'underweight', 'dullness', 'red blotches', 'colic abdominal', 'hypokalemia', 'hunger', 'prostate tender', 'pain foot', 'urinary hesitation', 'disequilibrium', 'flushing', 'indifferent mood', 'urinoma', 'hypoalbuminemia', 'pustule', 'slowing of urinary stream', 'extreme exhaustion', 'no status change', 'breakthrough pain', 'pansystolic murmur', 'systolic ejection murmur', 'stuffy nose', 'barking cough', 'rapid shallow breathing', 'noisy respiration', 'nasal discharge present', 'frail', 'cystic lesion', 'projectile vomiting', 'heavy legs', 'titubation', 'dysdiadochokinesia', 'achalasia', 'side pain', 'monocytosis', 'posterior\xa0rhinorrhea', 'incoherent', 'lameness', 'claudication', 'clammy skin', 'mediastinal shift', 'nausea and vomiting', 'awakening early', 'tenesmus', 'fecaluria', 'pneumatouria', 'todd paralysis', 'alcoholic withdrawal symptoms', 'myalgia', 'dyspareunia', 'poor dentition', 'floppy', 'inappropriate affect', 'poor feeding', 'moan', 'welt', 'tinnitus', 'hydropneumothorax', 'superimposition', 'feeling strange', 'uncoordination', 'absences finding', 'tonic seizures', 'debilitation', 'impaired cognition', 'drool', 'pin-point pupils', 'tremor resting', 'groggy', 'adverse reaction', 'adverse effect', 'abdominal bloating', 'fatigability', 'para 2', 'abortion', 'intermenstrual heavy bleeding', 'previous pregnancies 2', 'primigravida', 'abnormally hard consistency', 'proteinemia', 'pain neck', 'dizzy spells', 'shooting pain', 'hyperemesis', 'milky', 'regurgitates after swallowing', 'lip smacking', 'phonophobia', 'rolling of eyes', 'ambidexterity', 'pulsus\xa0paradoxus', 'gravida 10', 'bruit', 'breath-holding spell', 'scleral\xa0icterus', 'retch', 'blanch', 'elation', 'verbally abusive behavior', 'transsexual', 'behavior showing increased motor activity', 'coordination abnormal', 'choke', 'bowel sounds decreased', 'no known drug allergies', 'low back pain', 'charleyhorse', 'sedentary', 'feels hot/feverish', 'flare', 'pericardial friction rub', 'hoard', 'panic', 'cardiovascular finding', 'cardiovascular event', 'soft tissue swelling', 'rhd positive', 'para 1', 'nasal flaring', 'sneeze', 'hypertonicity', "Murphy's sign", 'flatulence', 'gasping for breath', 'feces in rectum', 'prodrome', 'hypoproteinemia', 'alcohol binge episode', 'abdomen acute', 'air fluid level', 'catching breath', 'large-for-dates fetus', 'immobile', 'homicidal thoughts']
        symptom_list = [symptom.title() for symptom in symptom_list]
        return render_template('AllDiseasePrediction.html', symptom_list=symptom_list)
    return redirect(url_for('login'))

@app.route("/predict", methods = ['POST', 'GET'])
def predictPage():
    try:
        if request.method == 'POST':
            print("Inside if")
            to_predict_dict = request.form.to_dict()
            print(to_predict_dict)
            to_predict_list = list(map(float, list(to_predict_dict.values())))
            print(to_predict_list)
            pred = predict(to_predict_list, to_predict_dict)
    except Exception as e:
        message = "Please enter valid Data"
        return render_template("home.html", message = message)

    return render_template('predict.html', pred = pred)

@app.route("/malariapredict", methods = ['POST', 'GET'])
def malariapredictPage():
    if request.method == 'POST':
        print("hi")
        try:
            if 'image' in request.files:
                img = Image.open(request.files['image'])
                img = img.resize((36,36))
                img = np.asarray(img)
                img = img.reshape((1,36,36,3))
                img = img.astype(np.float64)
                model = load_model("models/malaria.h5")
                pred = np.argmax(model.predict(img)[0])
                addPredHistory(pred, 'Malaria')
        except:
            message = "Please upload an Image"
            return render_template('home.html', message = message)
    return render_template('predict.html', pred = pred)

@app.route("/pneumoniapredict", methods = ['POST', 'GET'])
def pneumoniapredictPage():
    if request.method == 'POST':
        try:
            if 'image' in request.files:
                img = Image.open(request.files['image']).convert('L')
                img = img.resize((36,36))
                img = np.asarray(img)
                img = img.reshape((1,36,36,1))
                img = img / 255.0
                model = load_model("models/pneumonia.h5")
                pred = np.argmax(model.predict(img)[0])
                addPredHistory(pred, 'Pneumonia')
        except:
            message = "Please upload an Image"
            return render_template('pneumonia.html', message = message)
    return render_template('predict.html', pred = pred)

@app.route("/disease-predictor", methods=['POST', 'GET'])
def diseasePredictor():
    if request.method == 'POST':
        symptoms = request.form.to_dict()
        selected_symptoms_list = json.loads(symptoms['symptoms'])
        symptom_list = ['shortness of breath', 'dizziness', 'asthenia', 'fall', 'syncope', 'vertigo', 'sweat', 'sweating increased', 'palpitation', 'nausea', 'angina pectoris', 'pressure chest', 'polyuria', 'polydypsia', 'pain chest', 'orthopnea', 'rale', 'unresponsiveness', 'mental status changes', 'vomiting', 'labored breathing', 'feeling suicidal', 'suicidal', 'hallucinations auditory', 'feeling hopeless', 'weepiness', 'sleeplessness', 'motor retardation', 'irritable mood', 'blackout', 'mood depressed', 'hallucinations visual', 'worry', 'agitation', 'tremor', 'intoxication', 'verbal auditory hallucinations', 'energy increased', 'difficulty', 'nightmare', 'unable to concentrate', 'homelessness', 'hypokinesia', 'dyspnea on exertion', 'chest tightness', 'cough', 'fever', 'decreased translucency', 'productive cough', 'pleuritic pain', 'yellow sputum', 'breath sounds decreased', 'chill', 'rhonchus', 'green sputum', 'non-productive cough', 'wheezing', 'haemoptysis', 'distress respiratory', 'tachypnea', 'malaise', 'night sweat', 'jugular venous distention', 'dyspnea', 'dysarthria', 'speech slurred', 'facial paresis', 'hemiplegia', 'seizure', 'numbness', 'symptom aggravating factors', 'st segment elevation', 'st segment depression', 't wave inverted', 'presence of q wave', 'chest discomfort', 'bradycardia', 'pain', 'nonsmoker', 'erythema', 'hepatosplenomegaly', 'pruritus', 'diarrhea', 'abscess bacterial', 'swelling', 'apyrexial', 'dysuria', 'hematuria', 'renal angle tenderness', 'lethargy', 'hyponatremia', 'hemodynamically stable', 'difficulty passing urine', 'consciousness clear', 'guaiac positive', 'monoclonal', 'ecchymosis', 'tumor cell invasion', 'haemorrhage', 'pallor', 'fatigue', 'heme positive', 'pain back', 'orthostasis', 'arthralgia', 'transaminitis', 'sputum purulent', 'hypoxemia', 'hypercapnia', 'patient non compliance', 'unconscious state', 'bedridden', 'abdominal tenderness', 'unsteady gait', 'hyperkalemia', 'urgency of\xa0micturition', 'ascites', 'hypotension', 'enuresis', 'asterixis', 'muscle twitch', 'sleepy', 'headache', 'lightheadedness', 'food intolerance', 'numbness of hand', 'general discomfort', 'drowsiness', 'stiffness', 'prostatism', 'weight gain', 'tired', 'mass of body structure', 'has religious belief', 'nervousness', 'formication', 'hot flush', 'lesion', 'cushingoid facies', 'cushingoid\xa0habitus', 'emphysematous change', 'decreased body weight', 'hoarseness', 'thicken', 'spontaneous rupture of membranes', 'muscle hypotonia', 'hypotonic', 'redness', 'hypesthesia', 'hyperacusis', 'scratch marks', 'sore to touch', 'burning sensation', 'satiety early', 'throbbing sensation quality', 'sensory discomfort', 'constipation', 'pain abdominal', 'heartburn', 'breech presentation', 'cyanosis', 'pain in lower limb', 'cardiomegaly', 'clonus', 'unwell', 'anorexia', 'history of - blackout', 'anosmia', 'metastatic lesion', 'hemianopsia homonymous', 'hematocrit decreased', 'neck stiffness', 'cicatrisation', 'hypometabolism', 'aura', 'myoclonus', 'gurgle', 'wheelchair bound', 'left\xa0atrial\xa0hypertrophy', 'oliguria', 'catatonia', 'unhappy', 'paresthesia', 'gravida 0', 'lung nodule', 'distended abdomen', 'ache', 'macerated skin', 'heavy feeling', 'rest pain', 'sinus rhythm', 'withdraw', 'behavior hyperactive', 'terrify', 'photopsia', 'giddy mood', 'disturbed family', 'hypersomnia', 'hyperhidrosis disorder', 'mydriasis', 'extrapyramidal sign', 'loose associations', 'exhaustion', 'snore', 'r wave feature', 'overweight', 'systolic murmur', 'asymptomatic', 'splenomegaly', 'bleeding of vagina', 'macule', 'photophobia', 'painful swallowing', 'cachexia', 'hypocalcemia result', 'hypothermia, natural', 'atypia', 'general unsteadiness', 'throat sore', 'snuffle', 'hacking cough', 'stridor', 'paresis', 'aphagia', 'focal seizures', 'abnormal sensation', 'stupor', 'fremitus', "Stahli's line", 'stinging sensation', 'paralyse', 'hirsutism', 'sniffle', 'bradykinesia', 'out of breath', 'urge incontinence', 'vision blurred', 'room spinning', 'rambling speech', 'clumsiness', 'decreased stool caliber', 'hematochezia', 'egophony', 'scar tissue', 'neologism', 'decompensation', 'stool color yellow', 'rigor - temperature-associated observation', 'paraparesis', 'moody', 'fear of falling', 'spasm', 'hyperventilation', 'excruciating pain', 'gag', 'posturing', 'pulse absent', 'dysesthesia', 'polymyalgia', 'passed stones', 'qt interval prolonged', 'ataxia', "Heberden's node", 'hepatomegaly', 'sciatica', 'frothy sputum', 'mass in breast', 'retropulsion', 'estrogen use', 'hypersomnolence', 'underweight', 'dullness', 'red blotches', 'colic abdominal', 'hypokalemia', 'hunger', 'prostate tender', 'pain foot', 'urinary hesitation', 'disequilibrium', 'flushing', 'indifferent mood', 'urinoma', 'hypoalbuminemia', 'pustule', 'slowing of urinary stream', 'extreme exhaustion', 'no status change', 'breakthrough pain', 'pansystolic murmur', 'systolic ejection murmur', 'stuffy nose', 'barking cough', 'rapid shallow breathing', 'noisy respiration', 'nasal discharge present', 'frail', 'cystic lesion', 'projectile vomiting', 'heavy legs', 'titubation', 'dysdiadochokinesia', 'achalasia', 'side pain', 'monocytosis', 'posterior\xa0rhinorrhea', 'incoherent', 'lameness', 'claudication', 'clammy skin', 'mediastinal shift', 'nausea and vomiting', 'awakening early', 'tenesmus', 'fecaluria', 'pneumatouria', 'todd paralysis', 'alcoholic withdrawal symptoms', 'myalgia', 'dyspareunia', 'poor dentition', 'floppy', 'inappropriate affect', 'poor feeding', 'moan', 'welt', 'tinnitus', 'hydropneumothorax', 'superimposition', 'feeling strange', 'uncoordination', 'absences finding', 'tonic seizures', 'debilitation', 'impaired cognition', 'drool', 'pin-point pupils', 'tremor resting', 'groggy', 'adverse reaction', 'adverse effect', 'abdominal bloating', 'fatigability', 'para 2', 'abortion', 'intermenstrual heavy bleeding', 'previous pregnancies 2', 'primigravida', 'abnormally hard consistency', 'proteinemia', 'pain neck', 'dizzy spells', 'shooting pain', 'hyperemesis', 'milky', 'regurgitates after swallowing', 'lip smacking', 'phonophobia', 'rolling of eyes', 'ambidexterity', 'pulsus\xa0paradoxus', 'gravida 10', 'bruit', 'breath-holding spell', 'scleral\xa0icterus', 'retch', 'blanch', 'elation', 'verbally abusive behavior', 'transsexual', 'behavior showing increased motor activity', 'coordination abnormal', 'choke', 'bowel sounds decreased', 'no known drug allergies', 'low back pain', 'charleyhorse', 'sedentary', 'feels hot/feverish', 'flare', 'pericardial friction rub', 'hoard', 'panic', 'cardiovascular finding', 'cardiovascular event', 'soft tissue swelling', 'rhd positive', 'para 1', 'nasal flaring', 'sneeze', 'hypertonicity', "Murphy's sign", 'flatulence', 'gasping for breath', 'feces in rectum', 'prodrome', 'hypoproteinemia', 'alcohol binge episode', 'abdomen acute', 'air fluid level', 'catching breath', 'large-for-dates fetus', 'immobile', 'homicidal thoughts']
        final_sympton_dict = {}
        for idx in symptom_list:
            final_sympton_dict[idx] = 0
        for idx in selected_symptoms_list:
            final_sympton_dict[idx.lower()] = 1
        final_symptoms_list = list(final_sympton_dict.values())
        pred = predict(final_symptoms_list, {})
        return render_template('predict.html', pred = pred)
