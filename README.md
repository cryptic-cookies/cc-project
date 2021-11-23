# cc-project

<h2>Requirements</h2>
<li>python version 3.x</li>
<li>python packages (to install, run <code>pip3 install &lt;package-name&gt;</code>:
<ul>
<li>twilio</li>
<li>flask</li>
<li>pygame</li>
</ul>
</li>
<li>ngrok  - for responding to messages from Twilio, download from ngrok.io</li>

<h2>Twilio</h2>
The program uses Twilio to send and receive text messages.
In order for messaging to work, the following environment variables need to be set up in .bashrc file:
TWILIO_ACCOUNT_SID - credential to log into Twilio account
TWILIO_AUTH_TOKEN - credential to log into Twilio account
TWILIO_PHONE_NUMBER - main Twilio phone number used to send messages
OWNER_PHONE_NUMBER - device user phone number (has to be registered at Twilio as verified phone number)

At the moment Twilio account is a trial account.

To be able to respond to text messages from Twilio phone number, the url mapped to your web server has to be configured in Twilio. 


<h2>Running the program</h2>
To run the program from Rasberry Pi, go to terminal<br/>
cd &lt;directory where the project is&gt;<br>
if you want Twilio number to receive messages, type:<br>
<code>./ngrok http 5000</code>
This will generate a temporary url that look like <code>http://XXXXXXX.ngrok.io
copy generated ngrok url<br><br>
in another terminal window or tab, run:<br>
<code>python3 app.py &lt;generated ngrok url&gt;/message</code>
this will update Twilio with the url that will repond to sms messages<br>
you can also run the program without setting the url:
<code>python3 app.py</code>
  In this case the existing url will be used. So if you stop the program and <b>ngrok</b> is still running, you don't have to set the url when you run the program again<br><br>
  Use Ctrl-C to terminate the program.
