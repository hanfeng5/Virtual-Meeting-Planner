import  json, requests, datetime
# import time (PYCHARM BUG!)

# def pretty(obj):
#     return json.dumps(obj, sort_keys=True, indent=2)
#
# def safe_get(url):
#     try:
#         return urllib.request.urlopen(url)
#     except urllib.error.HTTPError as e:
#         print("The server couldn't fulfill the request." )
#         print("Error code: ", e.code)
#     except urllib.error.URLError as e:
#         print("We failed to reach a server")
#         print("Reason: ", e.reason)
#     return None

# import requests
#
# url = "https://maps.googleapis.com/maps/api/timezone/json?location=39.6034810%2C-119.6822510&timestamp=1331161200&key=AIzaSyAwq-zGDaets1tN5GO5n2EzRHJ5FKtCe44"
# #
# # payload={}
# # headers = {}
# #
# # response = requests.request("GET", url, headers=headers, data=payload)
# #
# # print(response.text)
#
# time = safe_get(url).read()
# time_result = json.loads(time)
# print(time_result)

# import requests
#
api_key = "30e3c89a0d0c4fd49e0bdb70333745ee"
# location = "Beijing, China"
# currentTime = requests.get("https://timezone.abstractapi.com/v1/current_time/?api_key=%s&location=%s"%(api_key,location))
# # print(response.status_code)
# print(currentTime.text)
#
# print("\n")

# base_location = "Seattle, WA"
# target_location = "Beijing, China"
# base_datetime = "2021-07-19 10:00:00"
# convertedTime = requests.get("https://timezone.abstractapi.com/v1/convert_time/?api_key=%s&base_location=%s&base_datetime=%s&target_location=%s"%(api_key,base_location,base_datetime,target_location))
# print(json.loads(convertedTime.content))

from flask import Flask, render_template,request
import logging
app = Flask(__name__)


def if_goodtime(dictionary, recommendation_type):
    # app.logger.info(dictionary)
    # app.logger.info(recommendation_type)
    # app.logger.info("inside goodtime")
    # time.sleep(1)   (PYCHARM BUG!)
    converted_time = dictionary["target_location"]["datetime"]
    # app.logger.info(converted_time)
    input_time = converted_time[11:]
    date = converted_time[:11]
    splitted_time = input_time.split(":")
    target_time = datetime.time(int(splitted_time[0]), int(splitted_time[1]), int(splitted_time[2]))
    if (recommendation_type == "workday schedule"):
        goodtime_start = datetime.time(8,00,00)
        goodtime_end = datetime.time(17,00,00)
        if (goodtime_start <= target_time and goodtime_end >= target_time):
            dictionary["goodtime"] = True
    else:
        longitude = dictionary["target_location"]["longitude"]
        latitude = dictionary["target_location"]["latitude"]
        url = "https://api.sunrise-sunset.org/json?lat=%s&lng=%s&date=%s"%(latitude,longitude,date)
        sun_data = requests.get(url).content
        sun_result = json.loads(sun_data)
        app.logger.info(sun_result)
        sunrise = sun_result["results"]["sunrise"]
        sunset = sun_result["results"]["sunset"]
        offset = int(dictionary["target_location"]["gmt_offset"])
        sunsetPM = False
        sunrisePM = False
        if "PM" in sunrise:
            sunrisePM = True
        if "PM" in sunset:
            sunsetPM = True
        sunrise = sunrise[:-2]
        sunrise_splitted = sunrise.split(":")
        if (sunrisePM):
            newhour = (int(sunrise_splitted[0]) + 12 + offset) % 24
        else:
            newhour = (int(sunrise_splitted[0]) + offset) % 24
        sunrise = str(newhour) + sunrise[sunrise.index(":"):]
        sunset = sunset[:-2]
        sunset_splitted = sunset.split(":")
        if (sunsetPM):
            newhour = (int(sunset_splitted[0]) + 12 + offset) % 24
        else:
            newhour = (int(sunset_splitted[0]) + offset) % 24
        sunset = str(newhour) + sunset[sunset.index(":"):]

        # app.logger.info(sunrise)
        # app.logger.info(sunset)
        # app.logger.info(offset)
        sunrise_splitted = sunrise.split(":")
        sunset_splitted = sunset.split(":")
        goodtime_start = datetime.time(int(sunrise_splitted[0]), int(sunrise_splitted[1]), int(sunrise_splitted[2]))
        goodtime_end = datetime.time(int(sunset_splitted[0]), int(sunset_splitted[1]), int(sunset_splitted[2]))
        if (goodtime_start <= target_time and goodtime_end >= target_time):
            dictionary["goodtime"] = True
    return dictionary



def get_time(current_location, date, target_location, start_time, end_time, recommendation_type):
    time_data = []
    start_hour = int(start_time[:2])
    start_minute = int(start_time[3:])
    second = "00"
    end_time_string = "%s %s:%s"%(date,end_time,second)
    end_hour = int(end_time[:2])
    end_minute = int(end_time[3:])
    start_time_string = "%s %s:%s:%s"%(date,f"{start_hour:02d}",f"{start_minute:02d}",second)
    result = requests.get("https://timezone.abstractapi.com/v1/convert_time/?api_key=%s&base_location=%s&base_datetime=%s&target_location=%s" % (api_key, current_location, start_time_string, target_location)).content
    resultdata = json.loads(result)
    time_data.append(if_goodtime(resultdata, recommendation_type))
    # app.logger.info(result)
    # while(end_time_string != start_time_string):
    while (end_hour != start_hour):
        start_hour += 1
        start_hour = start_hour % 24
        # app.logger.info(start_hour)
        start_time_string = "%s %s:%s:%s" % (date, f"{start_hour:02d}", f"{start_minute:02d}", second)
        result = requests.get("https://timezone.abstractapi.com/v1/convert_time/?api_key=%s&base_location=%s&base_datetime=%s&target_location=%s" %(api_key, current_location, start_time_string, target_location)).content
        resultdata = json.loads(result)
        time_data.append(if_goodtime(resultdata, recommendation_type))
        # app.logger.info(time_data)
    if (start_time_string != end_time_string):
        result = requests.get("https://timezone.abstractapi.com/v1/convert_time/?api_key=%s&base_location=%s&base_datetime=%s&target_location=%s" %(api_key, current_location, end_time_string, target_location)).content
        resultdata = json.loads(result)
        time_data.append((if_goodtime(resultdata, recommendation_type)))
    app.logger.info(time_data)
    # page_title = "Here is the time conversion result!\nCurrent Location:\"%s\"\nTarget Location:\"%s\""%(current_location,target_location)
    page_title = "Here is the time conversion result!"
    return render_template('getTime.html',
                    current_location = current_location,
                    target_location = target_location,
                    datetime = end_time_string,
                    page_title = page_title,
                    timeData = time_data,
                    missing = False)



@app.route("/")
def main_handler():
    app.logger.info("In MainHandler")
    current_location = request.args.get("current location",False)
    app.logger.info(current_location)
    target_location = request.args.get("target location",False)
    app.logger.info(target_location)
    date = request.args.get("date",False)
    app.logger.info(date)
    start_time = request.args.get("start time",False)
    app.logger.info(start_time)
    end_time = request.args.get("end time",False)
    app.logger.info(end_time)
    recommendation_type = request.args.get("recommendation_type", False)
    # if(current_location and target_location and datetime):
    # if current_location or start_time or end_time or target_location or date or recommendation_type:
    if current_location and start_time and end_time and target_location and date and recommendation_type:
        return get_time(current_location, date, target_location, start_time, end_time, recommendation_type)
    elif current_location or start_time or end_time or target_location or date or recommendation_type:
        return render_template('getTime.html', missing = True)
    else:
        return render_template('getTime.html', missing = False)



if __name__ == "__main__":
# Used when running locally only.
# When deploying to Google AppEngine, a webserver process will # serve your app.
    app.run(host="localhost", port=8000, debug=True)
#
# if current_location or datetime or target_location:
#     convertedtime = requests.get(
#         "https://timezone.abstractapi.com/v1/convert_time/?api_key=%s&base_location=%s&base_datetime=%s&target_location=%s" % (
#         api_key, current_location, datetime, target_location))
#     return render_template('getTime.html',
#                            current_location=current_location,
#                            target_location=target_location,
#                            datetime=datetime,
#                            convertedtime=json.loads(convertedtime.content),
#                            page_title="Converting from %s time to %s time" % (current_location, target_location))
# else:
#     return render_template('getTime.html')

