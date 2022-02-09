import secretstest
from pushbullet import PushBullet
import smtplib
from email.message import EmailMessage
from datetime import datetime, date

def send_email(subject, body):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        # Create a message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = secretstest.user
        msg['To'] = secretstest.user
        msg.set_content(body)
        smtp.login(secretstest.user, secretstest.password)
        smtp.send_message(msg)

# Push Bullet
pb = PushBullet(secretstest.accesstoken)
now = datetime.now()
hour = now.strftime("%H:%M:%S")

##########
def ntc(entry_price, price_now, pnl, hour):  # notification - trade close
    pb.push_note("Trade Info",
                 f"{hour}\n"
                 "position closed\n"
                 f"entry price: {entry_price}\n"
                 f"price now: {price_now}\n"
                 f"pnl: {pnl}"
                 )
    send_email(
        "Trade Info", "Position closed\ncheck out results in Pushbullet app")
def nto(entry_price, side, hour): # notification - trade open
    pb.push_note("Trade Info",
                 f"{hour}\n"
                 "postition opened\n"
                 f"entry price: {entry_price}\n"
                 f"side: {side}"
                 )
    send_email(
        "Trade Info", "Position Opened\nMore details in Pushbullet app")
def ns(type, hour): # notification - session
    pb.push_note("ByBit Bot",
                 f"Session {type} at {hour}"
                 )
    if type == "Closed":
        send_email(
            "ByBit Bot", "Application closed\nMore details in Pushbullet app")
def nlc(hour): # notification - lost connection
    pb.push_note("ByBit Bot",
                 f"{hour}\n"
                 f"Play sie zesrał"
                 )
    send_email(
        "ByBit Bot", "Lost Connection\nMore details in Pushbullet app")
def nrc(hour): # notifcation - reconnecting
    pb.push_note("ByBit Bot",
                 f"{hour}\n"
                 "Reconnected"
                 )
def nupd(msg, hour): # notification - update
    pb.push_note("Bybit Bot",
                 f"{hour}\n"
                 f"{msg}"
                 )
def ncon(msg, hour, side, entry): # notification - trade continuation
    pb.push_note("Trade Info",
                 f"{hour}\n"
                 f"{msg}\n"
                 f"side: {side}\n"
                 f"entry price: {entry}"
                 )
def nres(hour):
    pb.push_note("Bot Info", f"{hour}\nRestarted")
##########
