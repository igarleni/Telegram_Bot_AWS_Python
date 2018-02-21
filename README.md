# Telegram_Bot_AWS_Python
###### *A simple Template*

This little proyect is about managing your Telegram bot using your pc
and AWS Lambda service. We will use **3 scripts:**
 - 2 **Bot handlers:** *__lambda_function.py__* and *__PCHandler.py__*. The first one
runs on AWS Lambda service, and the second one runs on your PC. Both do
 exaclty the same thing, responding to Telegram Server chat updates, but in a 
 different way. The big difference is where they are executed and how they communicate
 with Telegram Server.
 
 - 1 **Switcher:** *__Switcher.py__*. It is used to change who will handle the bot (*lambda_function.py* or *PCHandler.py*)
This last script is also useful for debugging.

 - 1 **PrivateVariables:** *__PrivateVariables.py__*. Here you will have to save your own
 private variables (ie: botToken).
### 1. lambda_function.py

So I guess that you have your Lambda function with an APIGateway configured. This
lambda function is divided by 3 sections. The first 2 are mandatory, the last one
is optional if you want to comunicate with a DynamoBD.

- **REQUEST HANDLERS.** First, the section that reads the events that triggers him (in this
 case, Telegram HTTP requests). We just get them, convert
it to JSON and send the JSON request file to the right Handler function. In my case,
I only accept 2 types of updates: 'message' and 'callback_query'. Both have their
own functions and generates the HTTP response depending on what they get. **You should
modify this functions** depending on what you want to answer or what you want to do
with the updates. I just give you some examples inside this handlers. Be careful with
'callback_query' example, because it use DynamoDB. If you don't want to use DynamoDB, you
can simply save data on your script as a global variable. Keep in mind that if you do this,
the info of this variable will be deleted each time you update your script and click 'save'.

- **ANSWER GENERATORS.** This two Handler functions use other little functions to generate HTTP responses.
They are *sendMessage, sendKeyboard, sendPollSolution, sendVoice, sendVideo, sendAudio* and
*sendPhoto*. All of them generates an HTTPresponse that Handlers will return to AWS
Lambda manager, so then he can return it to Telegram Server. *It is mandatory* to send an
 'statusCode': '200', so Telegram Server knows that everything went OK, also when you don't
 want to answer anything to that update. **You don't need to modify this functions** if
  you want. 

- **DYNAMO COMUNICATION.** The third section is used to save on DynamoDB the polls votes. You should first
create a table on DynamoDB and give to your bot access permission to that table on AWS IAM (Roles).

NOTE: lambda_function.py doesn't use PrivateVariables.py. He uses Lambda AWS enviroment variables. It read them in this way:

    botToken = os.environ['BOT_TOKEN']
    
### 2. PCHandler.py

This is the same script of lambda_function.py, but runs on your own PC, not in a server.
I really made this script first, so it is like the lambda_function.py father. If you are
curious of how you can handle your bot on your PC without servers, you can take a look
to this script. This scripts doesn't need an exhaustive analysis because if you understood
how the lambda function works, you will easily understand this version.

This scripts have the same 2 sections named before: **REQUEST HANDLERS** and **ANSWER GENERATORS,**
it doens't have a DynamoBD comunication because of obvious reasons. The big difference 
between this script and the other one is the way he communicates with the server. I think you
 know it (otherwise you won't be reading this Repo), but i will explain it. Instead of
receiving HTTPrequests, he polls Telegram server, asking if there is any update that he 
have to handle. The process of choosing a response is nearly the same. It only changes
how you response to this updates. In this case, **you make an HTTPrequest** to get the updates and
 then **you make another HTTPrequest** to send a message/photo/video/etc. 
 In lambda_function.py you gave the response on the HTTPresponse.

### 3. Switcher.py

This little script is not required, but I found it **useful for debbugging and catching
file_id's**, so I share it with you.

It have 4 options:*'Enable AWS bot', 'Disable AWS bot', 'Get updates', 'Clean updates'.* 
You can perform multiple options at the same time, but be careful with the order. For example,
'Get updates' won't work correcly if you dont 'Disable AWS bot' first. You have to add on
*optionsChosen* a list with the options you want to be executed. 

- **'Enable AWS bot':** As his name says, this options is to enable AWS handler. It will
set the Webhook of your APIGateway. Remember to add your *awsGatewayUrl* on PrivateVariables.py.

- **'Disable AWS bot':** This is the opposite of first option. He just 
disable the Webhook, enabling /getUpdates queries, so we can debug using this
script.

- **'Get updates':** In this option, we read the incoming updates and
save them on a JSON file, called "results.json". Note that it
overrides the file, so be careful with information loosing.

- **'Clean updates':** Use this option if you want to tell Telegram
Server that you have handled all pending updates, so he won't send
them again.

An example of typical use is this:

    optionsChosen = [options[1],options[2]]

I use this to disable the Telegram AWS handler, and then read 
incoming updates. I use to open a conversation with my bot and send
him **audios/voices/videos** that I want to get his **ID_FILE**. They will
appear on results.json.

### 4. PrivateVariables.py (hidden)
 
The mandatory private variables you should have here are:

- **_"botToken"_** = your bot token
- **_"awsGatewayUrl"_** = your AWSGateway URL

There are some private variables that I use on this Repo, but
they are not mandatory. You can "hard code" them on your script.

- **_"idFileAudio"_** = your bot token
- **_"idFileVoice"_** = your AWSGateway URL

Then, on your AWS enviroment variables you should include this variables:

- **_"BOT_TOKEN"_** = your bot token
- **_"TABLE_NAME"_** = DynamoDB Table Name (this only is on AWS enviroment variables)

**Important!:** you dont have to quote (" ") your enviroment variables, they will be
autoQuoted by AWS Lambda Service.
 
 
 Thank you and I hope you found this Repo useful :)