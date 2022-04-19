import requests
import random
import json
import os
from dotenv import load_dotenv

load_dotenv()

gist_id = os.getenv("GIST_ID")
gist_filename = os.getenv("GIST_FILE")
questions_file = "./questions.txt"
used_file = "./used_questions.txt"
slack_url = os.getenv("SLACK_URL")
slack_channel = os.getenv("SLACK_CHANNEL")


def get_questions_from_gist(gist, filename):
    r = requests.get("https://api.github.com/gists/" + gist)
    rdata = r.json()
    rawurl = rdata["files"][str(filename)]["raw_url"]

    qraw = requests.get(rawurl).text
    questions = qraw.strip().split("\n")
    return questions


def get_questions(path):
    q_file = open(path, 'r')
    questions = q_file.read().strip().split("\n")
    return questions


def get_used_questions(path):
    used_file = open(path, 'r')
    used = used_file.read().strip().split("\n")
    return used


def new_question(used_list, question_list):
    question = random.choice(question_list)
    if question in used_list:
        return None
    else:
        return question


def update_questions_file(path, questions):
    with open(path, 'a') as qf:
        for q in questions:
            qf.write(f'{q}\n')


def save_used_question(path, question):
    with open(path, 'a') as uf:
        uf.write(f'{question}\n')


def compare_lists(list1, list2):
    list3 = [x for x in list1 if x not in list2]
    print('Remaining questions: ' + str(len(list3)))
    return len(list3)


def post_to_slack(question, channel, url):
    p = {
        "channel": str(channel),
        "username": "QOTD",
        "icon_emoji": ":interrobang:",
        "attachments": [
            {
                "fallback": "Here's the question of the day, respond in channel:",
                "pretext": "Here's the question of the day, respond in channel:",
                "color": "#00FF00",
                "fields": [
                    {
                        "title": "Question",
                        "value": str(question),
                        "short": False
                    }
                ]
            }
        ]
    }
    payload = json.dumps(p)

    s = requests.post(url, data=payload)
    print(s.status_code)
    print(s.reason)
    print(s.headers)
    print(s.content)

    return s.status_code


questions = get_questions(questions_file)
used_questions = get_used_questions(used_file)

questions.sort()
# print(str(questions) + "\n\n\n\n")
used_questions.sort()
# print(str(used_questions) + "\n\n\n\n")

if questions == used_questions or compare_lists(questions, used_questions) == 0:
    print("all questions in current question list have been used, checking gist")

    gist_questions = get_questions_from_gist(gist_id, gist_filename)
    print(gist_questions)

    gist_questions.sort()
    if gist_questions == questions:
        exit(2)
    else:
        update_questions_file(questions_file, gist_questions)
        questions = gist_questions

question = new_question(used_questions, questions)
while question is None:
    question = new_question(used_questions, questions)

print(question)
post_to_slack(question, slack_channel, slack_url)

save_used_question(used_file, question)
