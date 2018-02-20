import http.client
import urllib
import json
import time
import random
from PrivateVariables import botToken, idFileAudio, idFileVoice

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
lastUpdate = 0
random_li = ['Hello bro.', 'Yo whats up.', 'Whats up man.']
# polls_li = {chat_id: {message_id:
#                   {reply_id: reply_id, username:username, value:value, n_votes: n_votes}}
#                   value = sum(Votes) / (3 * nVotes)
polls_li = {}
keyboard = {"inline_keyboard": [[{"text": "Very bad", "callback_data": "0"}], [{"text": "Not that good", "callback_data": "1"}], [{"text": "It's ok", "callback_data": "2"}], [{"text": "So nice!", "callback_data": "3"}]]}


def main():
    global lastUpdate
    connection = http.client.HTTPSConnection('api.telegram.org')

    # Clean all updates that took place when bot was disconnected
    offset = lastUpdate
    params = urllib.parse.urlencode({'offset': offset})
    connection.request('GET', '/bot' + botToken + '/getUpdates', params, headers)
    response = connection.getresponse()
    string = response.read().decode('utf-8')
    responsejson = json.loads(string)
    updates = responsejson["result"]
    if len(updates) > 0:
        lastUpdate = int(updates[len(updates)-1]["update_id"]) + 1

    # Main loop
    while True:

        # Request for updates
        offset = lastUpdate
        params = urllib.parse.urlencode({'offset': offset})
        connection.request('GET', '/bot' + botToken + '/getUpdates', params, headers)
        response = connection.getresponse()
        file = open("results.json", "w")

        # Response treating
        string = response.read().decode('utf-8')
        file.write(string)  # Current action, for possible bugs
        responsejson = json.loads(string)
        updates = responsejson["result"]

        # Handle updates one by one if we get any
        if len(updates) > 0:
            for update in updates:
                handleUpdate(update)
                print(' ')
        else:
            print(str(lastUpdate) + " --> No updates")
            print(' ')

        # Sleep 5 seconds, so we don't poll Telegram Server that often
        time.sleep(5)


def handleUpdate(update):
    global lastUpdate
    # add many update types as you want to handle. Here i handle only "message" and "callback_query"
    if 'message' in update:
        success = handleMessage(update)
    elif 'callback_query' in update:
        success = handleCallbackQuery(update)
    else:
        success = True
    # if we success, we set lastUpdate as current update + 1, so we discard current update on next HTTPrequest
    if success:
        lastUpdate = int(update["update_id"]) + 1


def handleMessage(update):
    global polls_li
    sender = update['message']['from']
    messageId = update['message']['message_id']
    chatId = update['message']['chat']['id']
    success = False

    # Handle only text messages
    if 'text' in update['message']:
        text = update['message']['text']
        print(str(update["update_id"]) + " TEXT detected --> " + text)

        if ('mappa italia' == text) | ('Mappa italia' == text) | ('Mappa Italia' == text) | ('mappa Italia' == text):
            success = sendPhoto(chatId, "AgADBAAD-KsxG15jyVPdctQFXg0YDFJHJhoABBE172LbwlnNTCYDAAEC")
        elif (('Make a poll about this' == text) | ('make a poll about this' == text)) & ('reply_to_message' in update['message']):
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
            success = sendPollSolution(chatId, update['message']['reply_to_message']['message_id'])
        else:
            success = True
    else:
        success = True
    return success


# polls_li = {chat_id: {message_id:
#                   {reply_id: reply_id, username:username, value:value, n_votes: n_votes}}
#                   value = sum(Votes) / (3 * nVotes)
def handleCallbackQuery(update):
    global polls_li
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
        if chatId in polls_li:
            if messageId in polls_li[chatId]:
                votesDone = polls_li[chatId][messageId]['votes']
                if voteFrom in votesDone:
                    print("VOTE CHANGED --> from = " + voteFrom + ", new vote = " + data)
                votesDone[voteFrom] = data
                polls_li[chatId][messageId] = {'reply_id': replyId, 'username': username, 'votes': votesDone}
                polls_li[chatId][messageId] = {'reply_id': replyId, 'username': username, 'votes': votesDone}

        else:
            newVote = {voteFrom: data}
            polls_li[chatId] = {messageId: {'reply_id': replyId, 'username': username, 'votes': newVote}}
    print(polls_li[chatId][messageId]['votes'])
    success = True
    return success


def sendMessage(chatId, text, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', text = ' + text)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'text': text, 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendMessage', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'text': text})
        connection.request('POST', '/bot' + botToken + '/sendMessage', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


def sendKeyboard(chatId, text, keyboard, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', text and keyboard = ' + text)
    print(keyboard)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'text': text, 'reply_markup': json.dumps(keyboard), 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendMessage', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'text': text, 'reply_markup': json.dumps(keyboard)})
        connection.request('POST', '/bot' + botToken + '/sendMessage', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


# polls_li = {chat_id: {message_id:
#                   {reply_id: reply_id, username:username, value:value, n_votes: n_votes}}
#                   value = sum(Votes) / (3 * nVotes)
def sendPollSolution(chatId, messagePollId):
    success = True
    if chatId in polls_li:
        if messagePollId in polls_li[chatId]:
            votes = polls_li[chatId][messagePollId]['votes']
            nVotes = 0
            totalValue = 0
            for vote in votes:
                nVotes = nVotes + 1
                totalValue = totalValue + int(votes[vote])
            result = int(totalValue * 100 / (nVotes * 3))
            if result < 25:
                success = sendMessage(chatId, "Result: " + str(result) + "%" + ".Very bad bro.", polls_li[chatId][messagePollId]['reply_id'], True)
            elif result < 50:
                success = sendMessage(chatId, "Result: " + str(result) + "%" + ". Mmh not the best choice.", polls_li[chatId][messagePollId]['reply_id'], True)
            elif result < 75:
                success = sendMessage(chatId, "Result: " + str(result) + "%" + ". Good, keep on that point.", polls_li[chatId][messagePollId]['reply_id'], True)
            else:
                success = sendMessage(chatId, "Result: " + str(result) + "%" + ". Nice! you are the best.", polls_li[chatId][messagePollId]['reply_id'], True)
        else:
            success = sendMessage(chatId, "Go team! vote the poll", polls_li[chatId][messagePollId]['reply_id'], True)

    return success


def sendVoice(chatId, voice, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', voice = ' + voice)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'voice': voice, 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendVoice', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'voice': voice})
        connection.request('POST', '/bot' + botToken + '/sendVoice', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


def sendVideo(chatId, video, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', video = ' + video)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'video': video, 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendVideo', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'video': video})
        connection.request('POST', '/bot' + botToken + '/sendVideo', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


def sendAudio(chatId, audio, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', audio = ' + audio)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'audio': audio, 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendAudio', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'audio': audio})
        connection.request('POST', '/bot' + botToken + '/sendAudio', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


def sendPhoto(chatId, photo, replyId = 0, replyMode = False):
    connection = http.client.HTTPSConnection('api.telegram.org')
    print('chatID = ' + str(chatId) +', photo = ' + photo)
    if replyMode:
        params = urllib.parse.urlencode({'chat_id': chatId, 'photo': photo, 'reply_to_message_id': replyId})
        connection.request('POST', '/bot' + botToken + '/sendPhoto', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    else:
        params = urllib.parse.urlencode({'chat_id': chatId, 'photo': photo})
        connection.request('POST', '/bot' + botToken + '/sendPhoto', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        if 'retry_after' in responsejson:
            return False
    return True


if __name__ == "__main__":
    main()
