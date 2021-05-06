import json
import requests
import telegram_send
import datetime
import time

# Get Data From COWIN Public API
def get_data_from_cowin(pincode):

    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=" + \
        str(pincode)+"&date="+datetime.date.today().strftime("%d-%m-%Y")
    print(url)
    response = requests.get(url)
    data = json.loads(response.text)
    return data

# Checks for Avaliable slot with given requirements 
def check_requirements(data, required_age):
    final_list = []
    for center in data['centers']:
        available_sessions = []
        for session in center['sessions']:
            if(session['available_capacity'] > 0 and session['min_age_limit'] <= required_age):
                available_sessions.append(session)

        if(len(available_sessions) != 0):
            center['sessions'] = available_sessions
            final_list.append(center)
    return final_list

# generates the message which will sent
def generate_notification_string(details_of_appointment):

    message = "Covid-19 Vaccination Slot Available 🎉\n\nPlease register as soon as possible 📝\n\nDetails of centers-\n"
    count = 1
    print(type(details_of_appointment))
    for center in details_of_appointment:
        message = message+"%s)\n" % count
        count = count+1
        message = message+"    Name - "+center['name']+"\n"
        message = message+"    Address - "+center['address']+"\n"
        message = message+"    Pincode - "+str(center['pincode'])+"\n"
        message = message+"    Fees Type - "+center['fee_type']+"\n"
        #message=message+"    Map - \"https://maps.google.com/?q="+str(center['lat'])+","+str(center['long'])+"\n"
        message = message+"    Sessions 🏥 \n"
        session_count = 97
        for session in center['sessions']:
            message = message+"      "+chr(session_count)+")\n"
            session_count = session_count+1
            message = message+"           Date - "+session['date']+"\n"
            message = message+"           Available Capacity - " + \
                str(session['available_capacity'])+" \n"
            message = message+"           Minimum Age limit- " + \
                str(session['min_age_limit'])+"\n"
            message = message+"           Vaccine- "+session['vaccine']+"\n\n"

    print(message)

    return message

# Sends message to telegram bot
def send_notification(message):
    telegram_send.send(messages=[message])
    print("notification success")


# TO-DO - Change pincode and require age according to your need

pincode = 273002
required_age = 45
refresh_time= 60 # in seconds


data = get_data_from_cowin(pincode)
final = check_requirements(data, required_age)

while(not final):
    time.sleep(refresh_time)
    print("called again")
    data = get_data_from_cowin(pincode)
    final = check_requirements(data, required_age)

message = generate_notification_string(final)
send_notification(message)
