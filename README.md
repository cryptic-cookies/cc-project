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
<li><b>ngrok</b>  - for responding to messages from Twilio, download from ngrok.io</li>

<h2>Twilio</h2>
The program uses Twilio to send and receive text messages.
In order for messaging to work, the following environment variables need to be set up in .bashrc file:
<ul>
  <li>TWILIO_ACCOUNT_SID - credential to log into Twilio account</li>
  <li>TWILIO_AUTH_TOKEN - credential to log into Twilio account</li>
<li>TWILIO_PHONE_NUMBER - main Twilio phone number used to send messages</li>
<li>OWNER_PHONE_NUMBER - device user phone number (has to be registered at Twilio as verified phone number)</li>
</ul>

<p>At the moment Twilio account is a trial account.</p>

<p>To be able to respond to text messages from Twilio phone number, the url mapped to your web server has to be configured in Twilio. </p>


<h2>Running the program</h2>
To run the program from Rasberry Pi, go to terminal<br/>
<code>cd &lt;directory where the project is&gt;</code><br>
if you want Twilio number to respond to messages, type:<br>
<code>./ngrok http 5000</code><br>
This will generate a temporary url that look like <code>http://XXXXXXX.ngrok.io</code><br>
Copy generated <b>ngrok</b> url<br>
in another terminal window or tab, run:<br>
<code>python3 app.py &lt;generated ngrok url&gt;/message</code><br>
This will update Twilio with the url that will respond to sms messages<br>
You can also run the program without setting the url:<br>
<code>python3 app.py</code><br>
In this case the existing url will be used. So if you stop the program and <b>ngrok</b> is still running, you don't have to set the url when you run the program again<br><br>
Use Ctrl-C to terminate the program.
