from html.parser import HTMLParser
import urllib.request
import configparser
import time
import paho.mqtt.client as mqtt

class Boxinfo:
    def __init__(self, boxinfo_string):
        """Convert string into object.

        Strings are of the following form.

        Box 1: in Nutzung  seit dem 21.01.2017, 10:38:31              
        Box 2: frei  seit dem 09.05.2017, 13:05:09
        """
        self.raw = boxinfo_string

        # Box 1: frei
        self.num = boxinfo_string.split(":")[0].split(" ")[1]
        # seit dem 09.05.2017, 13:05:09 .
        self.date = boxinfo_string.split("seit dem ")[1]
        # 'in Nutzung' oder 'frei'
        self.belegt = 0 if "frei" in boxinfo_string else 1


class FBoxParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_tag = None
        self.boxinfos = []
            
    def handle_starttag(self, tag, attrs):
        self.in_tag = tag

    def handle_endtag(self,tag):
        self.in_tag = None

    def handle_data(self, data):
        if self.in_tag == "li":
            #print(" data:", data, ".")
            bi = Boxinfo(data)
            self.boxinfos.append(bi)

    def error(self, message):
        pass


class MqttPublisher:
    def __init__(self, topics, host, port=1883):
        """Create a publisher.
        topics is a dictionary that contains topic templates: status, date, and raw.
        """
        assert len(topics) == 3
        self.topics = topics
        self.client = mqtt.Client()
        print("connecting to", host, port)
        self.client.connect(host=host, port=port)

    def publish(self, boxinfo):
        assert "belegt" in self.topics
        assert "date" in self.topics
        assert "raw" in self.topics

        self.client.publish(self.topics["belegt"].format(nr=boxinfo.num),
                            boxinfo.belegt, retain=True)
        self.client.publish(self.topics["date"].format(nr=boxinfo.num),
                            boxinfo.date, retain=True)
        self.client.publish(self.topics["raw"].format(nr=boxinfo.num),
                            boxinfo.raw, retain=True)


def main():
    # read config file
    print("reading config")
    config = configparser.ConfigParser()
    config.read("fahrradbox.ini")

    sleeptime = config.getint("base", "wait_time")
    publisher = MqttPublisher(config["topics"], config["mqtt"]["host"])

    while True:
        # parse website
        parser = FBoxParser()
        with urllib.request.urlopen(config["base"]["url"]) as response:
            html = str(response.read(), encoding="utf8")
            parser.feed(html)

        for bi in parser.boxinfos:
            publisher.publish(bi)

        time.sleep(sleeptime)

if __name__ == "__main__":
    main()
