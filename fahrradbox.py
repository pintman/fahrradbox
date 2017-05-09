from html.parser import HTMLParser
import urllib.request
import configparser

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
        self.status = 0 if "frei" in boxinfo_string else 1
        #print("num:", box_num, "dat:", dat, "stat:", status)


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
            

def main():
    config = configparser.ConfigParser()
    config.read("fahrradbox.ini")

    parser = FBoxParser()
    with urllib.request.urlopen(config["url"]["url"]) as response:
        html = str(response.read(), encoding="utf8")
        parser.feed(html)

    topic_stat = config["topics"]["status"]
    topic_date = config["topics"]["date"]
    topic_raw = config["topics"]["raw"]

    for bi in parser.boxinfos:
        print(topic_stat.format(nr=bi.num), bi.status)
        print(topic_date.format(nr=bi.num), bi.date)
        print(topic_raw.format(nr=bi.num), bi.raw)

if __name__ == "__main__":
    main()
