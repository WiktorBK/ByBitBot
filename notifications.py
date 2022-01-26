import secrets
from pushbullet import PushBullet
from datetime import datetime
from twilio.rest import Client
import smtplib
from email.message import EmailMessage



def get_excel_file():
    with open(r'C:\Users\admin\Desktop\Trades\TradeHistory.xlsx', 'rb') as f:
        file_data = f.read()
        file_name = "TradeHistory.xlsx"
    return file_data, file_name

# Email
def send_email(subject, body, addattachment):

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        # Create a message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = secrets.user
        msg['To'] = secrets.user
        msg.set_content(body)

        # add attachment if necessary
        if addattachment == True:
            msg.add_attachment(get_excel_file()[0], maintype='application', subtype='octet-stream', filename = get_excel_file()[1])


        smtp.login(secrets.user, secrets.password)
        smtp.send_message(msg)


#Twilio
tw_client = Client(secrets.account_sid, secrets.auth_token)
def twilio_send_message():
    msg = tw_client.messages.create(
        body="twilio message",
        from_= secrets.twilio_number,
        to= secrets.phone_number
    )


# Push Bullet
pb = PushBullet(secrets.accesstoken)
now = datetime.now()
hour = now.strftime("%H:%M:%S")

# notification - trade close
def ntc(entry_price, price_now, hour):
    pb.push_note("Trade Info", 
    f"{hour}\n"
    "position closed\n"
    f"entry price: {entry_price}\n"
    f"price now: {price_now}"
    )

    send_email("Trade Info", "Position closed\ncheck out results in excel", addattachment = True)
# notification - trade open
def nto(entry_price, side, hour):
    pb.push_note("Trade Info", 
    f"{hour}\n"
    "postition opened\n"
    f"entry price: {entry_price}\n"
    f"side: {side}"
    )
    send_email("Trade Info", "Position Opened\nMore details in Pushbullet app", addattachment = False)
# notification - session
def ns(type, hour):
    pb.push_note("ByBit Bot",
    f"Session {type} at {hour}"
    )
    if type == "Closed":
        send_email("ByBit Bot", "Application closed\nMore details in Pushbullet app", addattachment = False)
#notification - lost connection
def nlc(hour):
    pb.push_note("ByBit Bot",
    f"{hour}\n"
    f"Play sie zesrał"
    )
    send_email("ByBit Bot", "Lost Connection\nMore details in Pushbullet app", addattachment = False)
# notifcation - reconnecting
def nrc(hour):
    pb.push_note("ByBit Bot",
    f"{hour}\n"
    "Reconnected"
    )

