import http.client
import urllib
import json
from PrivateVariables import awsGatewayUrl, botToken

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
connection = http.client.HTTPSConnection('api.telegram.org')
options =['Enable AWS bot', 'Disable AWS bot', 'Get updates', 'Clean updates']

optionsChosen = [options[1],options[2]]

for option in optionsChosen:
    if option == 'Enable AWS bot':
        print("Enabling AWS bot")
        print('\n')
        allowed_updates = json.dumps(["message", "callback_query"])
        params = urllib.parse.urlencode({'url': awsGatewayUrl,
                                         'allowed_updates': allowed_updates})
        connection.request('POST', '/bot' + botToken + '/setWebhook', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        print(string)
        print('\n')

        # Test if everything is okay
        connection.request('GET', '/bot' + botToken + '/getWebhookInfo', headers=headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        print(string)
        print('\n')

    elif option == 'Disable AWS bot':
        print("Disabling AWS bot")
        print('\n')
        connection.request('POST', '/bot' + botToken + '/deleteWebhook', headers=headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        print(string)
        print('\n')

    elif option == 'Get updates':
        print("Getting updates")
        print('\n')
        file = open("results.json", "w")
        params = urllib.parse.urlencode({'offset': 0})
        connection.request('GET', '/bot' + botToken + '/getUpdates', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        file.write(string)

    elif option == 'Clean updates':
        print("Cleaning updates")
        print('\n')
        file = open("results.json", "w")
        params = urllib.parse.urlencode({'offset': 0})
        connection.request('GET', '/bot' + botToken + '/getUpdates', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        responsejson = json.loads(string)
        updates = responsejson["result"]
        if len(updates) > 0:
            offset = int(updates[len(updates) - 1]["update_id"]) + 1
        else:
            offset = 0
        params = urllib.parse.urlencode({'offset': offset})
        connection.request('GET', '/bot' + botToken + '/getUpdates', params, headers)
        response = connection.getresponse()
        string = response.read().decode('utf-8')
        file.write(string)

    else:
        print("error: option not recognized")
