import boto3
import json
import random
import os
import http.client
import urllib

botToken = os.environ['BOT_TOKEN']
headers = {'Content-Type': 'application/json'}
tableName = os.environ['TABLE_NAME']
idFileAudio = os.environ['ID_AUDIO']
idFileVoice = os.environ['ID_VOICE']

random_li = ['Hello bro.', 'Yo whats up.', 'Whats up man.']
# polls_li = {chat_id: {message_id:
#                   {reply_id: reply_id, username:username, value:value, n_votes: n_votes}}
#                   value = sum(Votes) / (3 * nVotes)
polls_li = {}
keyboard = {"inline_keyboard": [[{"text": "Very bad", "callback_data": "0"}], [{"text": "Not that good", "callback_data": "1"}], [{"text": "It's ok", "callback_data": "2"}], [{"text": "So nice!", "callback_data": "3"}]]}


def lambda_handler(event, context):
    # get http request from Telegram Server
    data = json.loads(event["body"])

    # response treating, add many update types as you want to handle. Here i handle only "message" and "callback_query"
    if 'message' in data:
        response = handleMessage(data)
    elif 'callback_query' in data:
        response = handleCallbackQuery(data)
    else:
        # Default response if we don't have anything to say.
        # 'statusCode': '200' means that we read the UPDATE, so Telegram wont
        # send it again. MUST HAVE
        response = {
            'statusCode': '200',
            'headers': headers
        }
    return response


def handleMessage(update):
    global blackList_li
    global cdKeyboard
    global polls_li
    global talker
    global talkerCounter

    sender = update['message']['from']
    messageId = update['message']['message_id']
    chatId = update['message']['chat']['id']
    response = {
        'statusCode': '200',
        'headers': headers
    }
    if 'text' in update['message']:
        text = update['message']['text']
        print(str(update["update_id"]) + " TEXT detected --> " + sender['first_name'] + ": " + text)
        if ('mappa italia' == text) | ('Mappa italia' == text) | ('Mappa Italia' == text) | ('mappa Italia' == text):
            success = sendPhoto(chatId, "AgADBAAD-KsxG15jyVPdctQFXg0YDFJHJhoABBE172LbwlnNTCYDAAEC")
        elif ('Make a poll about this' == text) & ('reply_to_message' in update['message']):
            replieduser = update['message']['reply_to_message']['from']['first_name']
            success = sendKeyboard(chatId, 'What do you think about ' + replieduser + 'said?',
                                   keyboard, update['message']['reply_to_message']['message_id'], True)
        elif '👀' == text:
            success = sendAudio(chatId, idFileAudio)
        elif ('hello' in text) | ('Hello' in text):
            success = sendVoice(chatId, idFileVoice)
        elif ('random message' in text) | ('Random message' in text):
            answer = random.choice(random_li)
            success = sendMessage(chatId, answer)
        elif ('hello bot' in text) | ('Hello bot' in text):
            success = sendMessage(chatId, 'Did i hear my name?')
        elif ((text == 'Results?') | (text == 'results?')) & ('reply_to_message' in update['message']):
            response = sendPollSolution(chatId, update['message']['reply_to_message']['message_id'])
    return response


# {chat_id: {message_id:
#               {reply_id: reply_id, username:username, votes: {user:vote}}}
#                result = (sumatoria votos)/(3*nÂºvotos) = value/(n_votes*3)
def handleCallbackQuery(update):
    response = {
        'statusCode': '200',
        'headers': headers
    }
    chatId = update['callback_query']['message']['chat']['id']
    messageId = update['callback_query']['message']['message_id']
    replyId = update['callback_query']['message']['reply_to_message']['message_id']
    username = update['callback_query']['message']['reply_to_message']['from']['first_name']
    voteFrom = update['callback_query']['from']['first_name']
    data = update['callback_query']['data']
    print(str(update["update_id"]) + " VOTE detected --> chat_id = " + str(chatId) + ", message_id = " + str(messageId)
          + ", from = " + voteFrom + ", vote = " + str(data))
    if username == voteFrom:
        print("You can't vote here! " + username)
    else:
        insertVoteDynamo(chatId, messageId, replyId, username, voteFrom, data, '0')
    return response


def sendMessage(chatId, text, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', text = ' + text)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendMessage', 'chat_id': chatId, 'text': text, 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps({'method': 'sendMessage', 'chat_id': chatId, 'text': text}),
            'headers': headers
        }
    return response


def sendKeyboard(chatId, text, keyboard, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', text and keyboard = ' + text)
    print(keyboard)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendMessage', 'chat_id': chatId, 'text': text, 'reply_markup': json.dumps(keyboard),
                 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendMessage', 'chat_id': chatId, 'text': text, 'reply_markup': json.dumps(keyboard)}),
            'headers': headers
        }
    return response


# polls_li = {chat_id: {message_id:
#                   {reply_id: reply_id, username:username, value:value, n_votes: n_votes}}
#                   value = sum(Votes) / (3 * nVotes)
def sendPollSolution(chatId, messagePollId):
    poll = readDynamo(chatId, messagePollId)
    if poll != None:
        votes = poll['votes']["M"]
        nVotes = 0
        totalValue = 0
        for vote in votes:
            nVotes = nVotes + 1
            totalValue = totalValue + int(votes[vote]['S'])
        result = int(totalValue * 100 / (nVotes * 3))
        if result < 25:
            response = sendMessage(chatId, "Result: " + str(result) + "%" + ".Very bad bro.", polls_li[chatId][messagePollId]['reply_id'], True)
        elif result < 50:
            response = sendMessage(chatId, "Result: " + str(result) + "%" + ". Mmh not the best choice.", polls_li[chatId][messagePollId]['reply_id'], True)
        elif result < 75:
            response = sendMessage(chatId, "Result: " + str(result) + "%" + ". Good, keep on that point.", polls_li[chatId][messagePollId]['reply_id'], True)
        else:
            response = sendMessage(chatId, "Result: " + str(result) + "%" + ". Nice! you are the best.", polls_li[chatId][messagePollId]['reply_id'], True)
    else:
        response = sendMessage(chatId, "Go team! vote the poll", polls_li[chatId][messagePollId]['reply_id'], True)
    return response


def sendVoice(chatId, voice, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', voice = ' + voice)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendVoice', 'chat_id': chatId, 'voice': voice, 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps({'method': 'sendVoice', 'chat_id': chatId, 'voice': voice}),
            'headers': headers
        }
    return response


def sendVideo(chatId, video, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', video = ' + video)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendVideo', 'chat_id': chatId, 'video': video, 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps({'method': 'sendVideo', 'chat_id': chatId, 'video': video}),
            'headers': headers
        }
    return response


def sendAudio(chatId, audio, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', audio = ' + audio)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendAudio', 'chat_id': chatId, 'audio': audio, 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps({'method': 'sendAudio', 'chat_id': chatId, 'audio': audio}),
            'headers': headers
        }
    return response


def sendPhoto(chatId, photo, replyId=0, replyMode=False):
    print('chatID = ' + str(chatId) + ', photo = ' + photo)
    if replyMode:
        response = {
            'statusCode': '200',
            'body': json.dumps(
                {'method': 'sendPhoto', 'chat_id': chatId, 'photo': photo, 'reply_to_message_id': replyId}),
            'headers': headers
        }
    else:
        response = {
            'statusCode': '200',
            'body': json.dumps({'method': 'sendPhoto', 'chat_id': chatId, 'photo': photo}),
            'headers': headers
        }
    return response


def insertVoteDynamo(chatId, messageId, replyId, username, voteFrom, data, type):
    dynamo = boto3.client('dynamodb')
    chatIdmessageId = str(chatId) + str(messageId)
    poll = dynamo.get_item(TableName=tableName, Key={'ChatIDmessageID': {'S': chatIdmessageId}})
    print(poll)
    if 'Item' in poll:
        print("Adding new vote")
        if voteFrom in poll["Item"]['votes']["M"]:
            print("Changing vote --> From " + voteFrom + " vote " + data)
        poll["Item"]['votes']["M"][voteFrom] = {'S': data}
        item = poll["Item"]
        dynamo.put_item(TableName=tableName, Item=item)
    else:
        print("Creating new poll")
        item = {
            'ChatIDmessageID': {'S': chatIdmessageId},
            'chat_id': {'S': str(chatId)},
            'reply_id': {'S': str(replyId)},
            'username': {'S': username},
            'votes': {'M':
                          {voteFrom: {'S': data}}
                      },
            'type': {'S': type}
        }
        dynamo.put_item(Item=item, TableName=tableName)


def readDynamo(chatId, messageId):
    dynamo = boto3.client('dynamodb')
    chatIdmessageId = str(chatId) + str(messageId)
    poll = dynamo.get_item(TableName=tableName, Key={'ChatIDmessageID': {'S': chatIdmessageId}})
    if 'Item' in poll:
        return poll["Item"]
    return None
