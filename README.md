# cc-project

<h2>Requirements</h2>
<li>python version 3.x</li>
<li>python packages (to install, run <code>pip3 install &lt;package-name&gt;</code>:
<ul>
<li>twilio</li>
<li>flask</li>
<li>apscheduler</li>
</ul>
</li>
<li>ngrok  - for responding to messages from Twilio, download from ngrok.io</li>

<h2>Twilio</h2>
The program uses Twilio to send and receive text messages.
In order for messaging to work, the following environment variables need to be set up:
TWILIO_ACCOUNT_SID - credential to log into Twilio account
TWILIO_AUTH_TOKEN - credential to log into Twilio account
TWILIO_PHONE_NUMBER - main Twilio phone number used to send messages
OWNER_PHONE_NUMBER - device user phone number (has to be registered at Twilio as verified phone number)

At the moment Twilio account is a trial account.

To be able to respond to text messages from Twilio phone number, the url mapped to you web server has to be configured in Twilio


<h2>Running the program</h2>
To run the program from Rasberry Pi, go to terminal<br/>
cd &lt;directory where the project is&gt;<br>
if you want Twilio number to receive messages, type:<br>
<code>./ngrok http 5000</code>

copy generated ngrok url and use it in Twilio webhook configuration TODO: add details<br><br>
in another terminal window or tab:<br>
<code>python3 app.py</code>