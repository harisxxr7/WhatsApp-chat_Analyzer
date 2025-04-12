import os
import io
import base64
import numpy as np
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time

from nltk.sentiment import SentimentIntensityAnalyzer
from werkzeug.security import check_password_hash
from time import sleep
import pymysql
from collections import Counter
import random
import shutil
import re
import matplotlib.pyplot as plt

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/details'
db = SQLAlchemy(app)


class clientdetail(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(12), nullable=True)
    gender = db.Column(db.String(120), nullable=True)
    password = db.Column(db.String(50), nullable=True)
    age = db.Column(db.String(6), nullable=True)
    date = db.Column(db.DateTime, default=datetime.now)
    imageurl = db.Column(db.String(100), nullable=True)

    def check_password(self, password):
        return check_password_hash(self.password, password)

def searchword(text,word):
    # Split the text into lines
    searched_list = []
    filtered_substrings = []
    words = []
    chat_times = []
    for line in text:
        colon_indices = [m.start() for m in re.finditer(':', line)]
        if len(colon_indices) >= 2:
            line_text = line[colon_indices[1] + 1:]
            line_text = line_text.lower()
            print(line_text)
            if word in line_text:
                print(line_text)
                searched_list.append(line_text)
    return searched_list
def analyze_chat_sentiments(text):
    # Initialize the SentimentIntensityAnalydi
    sia = SentimentIntensityAnalyzer()
    negative_strings = []
    positive_strings = []
    positive_count = 0
    negative_count = 0
    chat_times = []
    for line in text:
        message = line.split(':', 2)[-1].strip()  # Extract message text after second colon
        sentiment_scores = sia.polarity_scores(message)
        compound_score = sentiment_scores['compound']

        # Increment positive or negative count based on compound score
        if compound_score >= 0.05:
            positive_strings.append(line)
            positive_count += 1
        elif compound_score <= -0.05:
            negative_strings.append(line)
            negative_count += 1

    # Return the overall positive and negative counts
    return positive_count, negative_count,negative_strings,positive_strings
def getcounts():
    # Initialize the sentiment analyzer

    # Read the chat from the text file
    with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
        text_dataa = file.readlines()

    text_data = '\n'.join(text_dataa)
    dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2}', text_data)
    last_date = dates[-1]
    month, date, year = last_date.split('/')

    # Print the extracted values
    print("Date:", date)
    print("Month:", month)
    print("Year:", year)
    monthcount = 0
    daycount = 0
    yearcount = 0
    for d in reversed(dates):
        m, dy, y = d.split('/')
        if (dy == date):
            daycount = daycount + 1
        else:
            break
    for d in reversed(dates):
        m, dy, y = d.split('/')
        if (m == month):
            monthcount = monthcount + 1
        else:
            break
    for d in reversed(dates):
        m, dy, y = d.split('/')
        if (y == year):
            yearcount = yearcount + 1
        else:
            break
    print(daycount)
    print(monthcount)
    print(yearcount)
    print(len(dates))
    return daycount, monthcount, yearcount, len(dates)
def split_string_on_comma(string):
    substrings = []
    while ',' in string:
        comma_index = string.index(',')
        substring = string[comma_index + 1:].strip()
        substrings.append(substring)
        string = string[comma_index + 1:]
    return ' '.join(substrings)

def calculate_message_counts(chat_times):
    # Create a Counter object to store the message counts by hour
    message_counts = Counter()

    for chat_time in chat_times:
        # Extract the hour from the chat time
        hour = chat_time.split(':')[0]
        # Increment the message count for the hour
        hour = split_string_on_comma(hour)
        message_counts[hour] += 1

    return message_counts

def extract_links(text):
    # Find all URLs using regex
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls
def extract_words(lines):
    # Split the text into lines
    filtered_substrings = []
    words = []
    chat_times = []
    for line in lines:
        # Find the substring after the second occurrence of ':'
        colon_indices = [m.start() for m in re.finditer(':', line)]
        if len(colon_indices) >= 2:
            line_text = line[colon_indices[1]+1:]
            # Remove special characters and convert to lowercase
            line_text = re.sub(r'[^\w\s]', '', line_text.lower())
            # Split the text into words
            line_words = line_text.split()
            filtered_substrings.append(line_text)
            # Exclude specific words like 'media' and 'omitted'
            line_words = [word for word in line_words if word not in ['media', 'omitted']]
            words.extend(line_words)
            # Extract the chat time
            chat_time = line[:colon_indices[1]]
            chat_times.append(chat_time)
    return words, filtered_substrings, chat_times
#This function extract number of participents and number of texts by each participent
#It take chat as argument and return 2 arrays first with name of participents
#second an array with number of texts by each participents
def extract_name_from_text(lines):
    participents = []
    totaltextsperperson = []
    for line in lines:
        if line.count('/') >= 2 and ':' in line.partition('-')[0]:
            start_index = line.find('-') + 1
            end_index = line.find(':', line.find(':') + 1)

            if start_index == -1 or end_index == -1:
                print('none')
            extracted_text = line[start_index:end_index].strip()
            print(extracted_text)
            if extracted_text not in participents:
                if len(extracted_text) < 80:
                    if 'http' not in extracted_text and 'end-to-end encrypted' not in extracted_text and  'added' not in extracted_text and  'created' not in extracted_text and  'group' not in extracted_text:
                        participents.append(extracted_text)
    text_data = '\n'.join(lines)
    for participent in participents:
        count = text_data.lower().count(participent.lower())
        totaltextsperperson.append(count)
    return participents, totaltextsperperson

def chart(first_array,second_array):
    sorted_indices = sorted(range(len(second_array)), key=lambda k: second_array[k], reverse=True)
    top_10_indices = sorted_indices[:10]
    top_10_first_array = [first_array[i] for i in top_10_indices]
    top_10_second_array = [second_array[i] for i in top_10_indices]
    print(top_10_second_array)
    print(top_10_first_array)
    # Generating random colors
    colors = [random.choice(['#800000', 'green', 'blue', 'purple', 'orange', 'darkgreen']) for _ in range(10)]

    # Plotting the graph
    plt.bar(top_10_first_array, top_10_second_array, color=colors)
    plt.xticks(rotation='vertical')
    plt.subplots_adjust(bottom=0.27)
    plt.title('Top 10 peoples chat stats')

    # Saving the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    plt.close()
def encrypt_text(plain_text, key):
    encrypted_text = ""
    for char in plain_text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            shifted_char = chr((ord(char) - ascii_offset + key) % 26 + ascii_offset)
            encrypted_text += shifted_char
        else:
            encrypted_text += char
    return encrypted_text


def extract_chat(chat_file, sender_name):
    sender_messages = []
    with open(chat_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        line = line.strip()
        if line:
            name_match = re.search(r'-\s(.+?):', line)
            if name_match:
                current_sender = name_match.group(1)
                if current_sender == sender_name:
                    message = line.split(':', 1)[1].strip()
                    sender_messages.append(message)

    return sender_messages

def download_string_to_file(content, filename):
    with open(filename, 'w',encoding='utf-8') as file:
        file.write(content)
    print(f"String downloaded and saved to {filename}.")
def delete_folder_contents(folder_path):
    # Verify that the folder exists
    if os.path.exists(folder_path):
        # Iterate over the contents of the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            # Check if the path is a file or directory
            if os.path.isfile(file_path):
                # Remove the file
                os.remove(file_path)
            else:
                # Remove the directory and its contents recursively
                shutil.rmtree(file_path)

        print("All data in the folder has been deleted.")
    else:
        print("The folder does not exist.")
def decrypt_text(encrypted_text, key):
    decrypted_text = ""
    for char in encrypted_text:
        if char.isalpha():
            ascii_offset = ord('A') if char.isupper() else ord('a')
            shifted_char = chr((ord(char) - ascii_offset - key) % 26 + ascii_offset)
            decrypted_text += shifted_char
        else:
            decrypted_text += char
    return decrypted_text


@app.route("/")
def home():
    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def getsignupdetails():
    if request.method == 'POST':
        '''Add entry to the database'''

        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        age = request.form.get('age')
        password = request.form.get('password')
        password = encrypt_text(password,3)
        entry = clientdetail(name=name, age=age, gender=gender, date=datetime.now(), email=email, imageurl='',
                             password=password)
        db.session.add(entry)
        db.session.commit()
    return render_template('signUp.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        message = ''
        email = request.form['email']
        password = request.form['password']

        user = clientdetail.query.filter_by(email=email).first()
        if user is None:
            message = 'Incorrect username or password'
            # Redirect to a success page or perform other actions here
            return render_template('login.html', message=message)
        user.password = decrypt_text(user.password, 3)
        user.password = user.password
        if user.password == password:
            return render_template('UploadChat.html', message=message)
        else:
            message = 'Incorrect username or password'
            # Redirect to a success page or perform other actions here
            return render_template('login.html', message=message)

graphic1 = None;
graphic = None;
@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    global graphic1;
    global graphic;
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            folder_path = r'D:\fyp rar file final\WhatsAppData (1)\WhatsAppData\textfile\file1.txt'
            delete_folder_contents(r'D:\fyp rar file final\WhatsAppData (1)\WhatsAppData\textfile\\textfile')
            uploaded_file.save(folder_path)
        message = 'Logged in successfully'
        day, mtd, ytd, total = getcounts()
        with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
            text_dataa = file.readlines()
        participents, totaltextsperperson = extract_name_from_text(text_dataa)
        chat_words, filtered_substrings, chat_times = extract_words(text_dataa)
        message_counts = calculate_message_counts(chat_times)
        peak_slots = message_counts.most_common(4)
        first_arraytimes = [str(int(item[0])) + '-' + str(int(item[0]) + 1) for item in peak_slots]
        second_arraycounts = [item[1] for item in peak_slots]
        word_counts = Counter(chat_words)
        commonwords = []
        # Get the most common words
        most_common_words = word_counts.most_common(10)
        # Print the most common words
        for word, count in most_common_words:
            print(f'{word}: {count}')
            commonwords.append(word + ' : ' + str(count))
        print(commonwords[0])

        num_bars = len(participents)  # or len(y)
        colors = [random.choice(['#800000', 'green', 'blue', 'purple', 'orange', 'darkgreen']) for _ in range(num_bars)]
        sorted_indices = sorted(range(len(totaltextsperperson)), key=lambda k: totaltextsperperson[k], reverse=True)
        top_10_indices = sorted_indices[:10]
        top_10_first_array = [participents[i] for i in top_10_indices]
        top_10_second_array = [totaltextsperperson[i] for i in top_10_indices]
        plt.bar(top_10_first_array, top_10_second_array, color=colors)
        plt.xticks(rotation='vertical')
        plt.subplots_adjust(bottom=0.29)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        graphic = base64.b64encode(image_png)
        graphic = graphic.decode('utf-8')
        plt.bar(first_arraytimes, second_arraycounts, color=colors)
        plt.xticks(rotation='vertical')
        plt.subplots_adjust(bottom=0.20)
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        plt.close()
        graphic1 = base64.b64encode(image_png)
        graphic1 = graphic1.decode('utf-8')
        return render_template('HomePage.html', mtd=mtd, day=day, ytd=ytd, total=total, totalparicipents=len(participents),
                               graphics=graphic,graphic1=graphic1,
                               word0=commonwords[0], word1=commonwords[1], word2=commonwords[2], word3=commonwords[3],
                               word4=commonwords[4], word5=commonwords[5],
                               word6=commonwords[6], word7=commonwords[7], word8=commonwords[8], word9=commonwords[9])
    else:
        day, mtd, ytd, total = getcounts()
        with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
            text_dataa = file.readlines()
        participents, totaltextsperperson = extract_name_from_text(text_dataa)
        chat_words, filtered_substrings, chat_times = extract_words(text_dataa)
        word_counts = Counter(chat_words)
        commonwords = []
        # Get the most common words
        most_common_words = word_counts.most_common(10)
        # Print the most common words
        for word, count in most_common_words:
            print(f'{word}: {count}')
            commonwords.append(word + ' : ' + str(count))
        print(commonwords[0])
        message_counts = calculate_message_counts(chat_times)
        peak_slots = message_counts.most_common(4)
        first_arraytimes = [str(int(item[0])) + '-' + str(int(item[0]) + 1) for item in peak_slots]
        second_arraycounts = [item[1] for item in peak_slots]
        num_bars = len(participents)  # or len(y)
        colors = [random.choice(['#800000', 'green', 'blue', 'purple', 'orange', 'darkgreen']) for _ in range(num_bars)]
        sorted_indices = sorted(range(len(totaltextsperperson)), key=lambda k: totaltextsperperson[k], reverse=True)
        top_10_indices = sorted_indices[:10]
        top_10_first_array = [participents[i] for i in top_10_indices]
        top_10_second_array = [totaltextsperperson[i] for i in top_10_indices]


        return render_template('HomePage.html', mtd=mtd, day=day, ytd=ytd, total=total,
                               totalparicipents=len(participents), graphics=graphic,graphic1=graphic1,
                               word0=commonwords[0], word1=commonwords[1], word2=commonwords[2], word3=commonwords[3],
                               word4=commonwords[4], word5=commonwords[5],
                               word6=commonwords[6], word7=commonwords[7], word8=commonwords[8], word9=commonwords[9])


@app.route("/person-analysis" ,methods=['GET', 'POST'])
def person_analysis():
    if request.method == 'POST':
        with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
            text_dataa = file.readlines()
        participents, totaltextsperperson = extract_name_from_text(text_dataa)
        print(participents)
        name = request.form.get('dropdown')
        chat = extract_chat('textfile/file1.txt', name)
        total = len(chat)
        overalltotal = len(text_dataa)
        percent = total/overalltotal*100
        positive_count, negative_count, negative_string, positive_string = analyze_chat_sentiments(chat)
        return render_template('PersonAnalysis.html', dropdown_options=participents, show_content=True,string_list=negative_string, total=total,positive_count=positive_count,percent=percent,positive_string=positive_string)
    with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
        text_dataa = file.readlines()
    participents, totaltextsperperson = extract_name_from_text(text_dataa)

    print(participents)
    return render_template('PersonAnalysis.html', dropdown_options=participents,show_content=False)

@app.route("/Chat-Comparsion",  methods=['GET', 'POST'])
def Chat_Comparsion():
    if request.method == 'POST':
        downloadstring = ''
        uploaded_file = request.files['file']
        uploaded_file1 = request.files['file1']
        if uploaded_file.filename != '' and uploaded_file1.filename != '':
            folder_path = r'D:\\fyp rar file final\\WhatsAppData (1)\\WhatsAppData\\compare\\file.txt'
            folder_path1 = r'D:\\fyp rar file final\\WhatsAppData (1)\\WhatsAppData\\compare\\file1.txt'
            delete_folder_contents(r'D:\\fyp rar file final\\WhatsAppData (1)\\WhatsAppData\\compare')
            uploaded_file.save(folder_path)
            uploaded_file1.save(folder_path1)
            with open('compare/file.txt', 'r', encoding='utf-8') as file:
                text_data = file.readlines()
            with open('compare/file1.txt', 'r', encoding='utf-8') as file:
                text_data1 = file.readlines()
            participents, totaltextsperperson = extract_name_from_text(text_data)
            participents1, totaltextsperperson1 = extract_name_from_text(text_data1)

            texts1 = len(text_data1)
            texts = len(text_data)
            print('negative strings')
            positive_count, negative_count,negative_string,positive_string = analyze_chat_sentiments(text_data)
            positive_count1, negative_count1, negative_string1,positive_string1 = analyze_chat_sentiments(text_data1)
            print(negative_string1)
            print(negative_string)
            chat_words, filtered_substrings, chat_times = extract_words(text_data)
            message_counts = calculate_message_counts(chat_times)
            peak_slots = message_counts.most_common(4)
            first_array = [str(int(item[0]) ) + '-' + str(int(item[0]) + 1) for item in peak_slots]
            second_array = [item[1] for item in peak_slots]
            chat_words, filtered_substrings, chat_times = extract_words(text_data1)
            message_counts = calculate_message_counts(chat_times)
            peak_slots1 = message_counts.most_common(4)
            first_array1 = [str(int(item[0])) + '-' + str(int(item[0]) + 1) for item in peak_slots1]
            second_array1 = [item[1] for item in peak_slots1]
            print(first_array, second_array, first_array1, second_array1)
            print(peak_slots)
            print(participents)
            print(participents1)
            p = participents
            p1 = participents1
            set1 = set(p)
            set2 = set(p1)
            mutual_elements = set1.intersection(set2)
            mutual_elements_list = list(mutual_elements)
            print(mutual_elements_list)
            downloadstring += 'Person 1 data \n'
            downloadstring += "Participents : " + " ".join(participents) + '\n'
            peak_slots = [str(item) for item in peak_slots]
            downloadstring += "Peak hours  : " + " ".join(peak_slots) + '\n'
            downloadstring += 'Total count : ' + str(texts) + '\n'
            downloadstring += 'Negative count : ' + str(negative_count) + '\n'
            downloadstring += 'Positive count : ' + str(positive_count) + '\n'

            downloadstring += 'Person 2 data \n'
            downloadstring += "Participents : " + " ".join(participents1) + '\n'
            peak_slots1 = [str(item) for item in peak_slots1]
            downloadstring += "Peak hours : " + " ".join(peak_slots1) + '\n'
            downloadstring += 'Total count : ' + str(texts1) + '\n'
            downloadstring += 'Negative count : ' + str(negative_count1) + '\n'
            downloadstring += 'Positive count : ' + str(positive_count1) + '\n'
            downloadstring += 'Mutual Contacts : ' + " ".join(mutual_elements_list) + '\n'
            download_string_to_file(downloadstring, 'DetailedReport')


        return render_template('ChatComparsion.html',participents=len(participents),participents1=len(participents1),count=texts,count1=texts1,negative=negative_count,negative1=negative_count1,positive=positive_count,positive1=positive_count1,
                                   participentsname1=participents1,negative_string=negative_string,negative_string1=negative_string1,
                                   participentsname=participents,show_content=True,mutual_elements=mutual_elements_list)
    return render_template('ChatComparsion.html',show_content=False)

@app.route("/sentiment-analysis",methods=['GET', 'POST'])
def sentiment_analysis():
    with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
        text_dataa = file.readlines()
    if request.method == 'POST':
        keyword = request.form['keyword']
        keyword = keyword.lower()
        string_list = searchword(text_dataa,keyword)
        total = len(string_list)
        overalltotal = len(text_dataa)
        percent = total / overalltotal * 100
        positive_count, negative_count, negative_string, positive_string = analyze_chat_sentiments(string_list)
        return render_template('SentimentAnalysis.html',string_list=string_list,show_content=True,total=total,percent=percent)
    return render_template('SentimentAnalysis.html')

@app.route("/links",methods=['GET', 'POST'])
def links():
    with open('textfile/file1.txt', 'r', encoding='utf-8') as file:
                chat_text = file.read()
    links = extract_links(chat_text)
    print(links)
    return render_template('links.html', string_list=links)
app.run(debug=True)
