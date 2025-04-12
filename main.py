import re
from collections import Counter
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from time import sleep
import pymysql
from flask import Flask, render_template, request, redirect, url_for, jsonify, Response
#from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, time
import os
from werkzeug.security import check_password_hash
#import MySQLdb


#This function will take the text file & the word by which you want to search a chat and
#it will retrun the substring only containing the searchedwords
def searchword(text,word):
    # Split the text into lines
    lines = text.split('\n')
    searched_list = []
    filtered_substrings = []
    words = []
    chat_times = []
    for line in lines:
        colon_indices = [m.start() for m in re.finditer(':', line)]
        if len(colon_indices) >= 2:
            line_text = line[colon_indices[1] + 1:]
            print(line_text)
            if word in line_text:
                print(line_text)
                searched_list.append(line_text)
    return searched_list








#extract time , words and substrings from a chat
def extract_words(text):
    # Split the text into lines
    lines = text.split('\n')
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








#Function to analyze chat sentiments just provide the chat
def analyze_chat_sentiments(text):


    # Initialize the SentimentIntensityAnalydi
    sia = SentimentIntensityAnalyzer()

    # Count variables
    positive_count = 0
    negative_count = 0
    chat = text.split('\n')
    chat_times = []
    for line in chat:
        message = line.split(':', 2)[-1].strip()  # Extract message text after second colon
        sentiment_scores = sia.polarity_scores(message)
        compound_score = sentiment_scores['compound']

        # Increment positive or negative count based on compound score
        if compound_score >= 0.05:
            positive_count += 1
        elif compound_score <= -0.05:
            negative_count += 1

    # Return the overall positive and negative counts
    return positive_count, negative_count


def split_string_on_comma(string):
    substrings = []
    while ',' in string:
        comma_index = string.index(',')
        substring = string[comma_index + 1:].strip()
        substrings.append(substring)
        string = string[comma_index + 1:]
    return ' '.join(substrings)
def extract_links(text):
    # Find all URLs using regex
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return urls





# Read the chat from a text file
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









with open('Group chat.txt', 'r', encoding='utf-8') as file:
    chat_text = file.read()

# Extract words and filtered substrings from the chat
chat_words, filtered_substrings, chat_times = extract_words(chat_text)
links = extract_links(chat_text)
# Count the frequency of each word
word_counts = Counter(chat_words)

# Get the most common words
most_common_words = word_counts.most_common(10)
message_counts = calculate_message_counts(chat_times)
# Print the most common words
for word, count in most_common_words:
    print(f'{word}: {count}')


count=0
for link in links:
    count = count + 1
    print(f'link # {count} : {link}')
chat_words, filtered_substrings, chat_times = extract_words(chat_text)
message_counts = calculate_message_counts(chat_times)
peak_slots = message_counts.most_common(4)
print("\nPeak 4-Hour Slots:")
for slot, count in peak_slots:
    integer_number = int(slot)
    print(f'{integer_number}-{integer_number+1}: {count} messages')


positive_count, negative_count = analyze_chat_sentiments(chat_text)
print('Positive count:', positive_count)
print('Negative count:', negative_count)
# Print the filtered substrings
#print("Filtered Substrings:")
#for substring in filtered_substrings:
 #   print(substring)
searchword(chat_text,'cheers')
