# CS121 Project 3
# Created by Ye Yuan
# Contributors: Diyue Gu, Jian Li
# Team# : 53

from bs4 import BeautifulSoup
import json
from nltk.corpus import stopwords
import redis
import math


class IcsSearchEngine:

    def __init__(self):
        self.db = None
        self.local_title=None
        self.js_file = 'index.json'
        self.page_counter = 0
        self.local_word_counter = 0
        self.all_words = set()
        self.stop_words = set(stopwords.words('english'))
        self.all_words_fix=37497

        with open("./WEBPAGES_RAW/bookkeeping.json") as map_file:
            self.map_js = json.load(map_file)

        open(self.js_file, 'w').close()

    def parse_line(self, line, freq, unique):
        pure_line = ''.join(map(lambda x: " " + x.lower() if x.isupper() else x,
                                [i if (ord(i) < 128) and i.isalnum() else ' ' for i in line]))

        for token in pure_line.split():
            # all is a set.
            if len(token) < 2 or (token in self.stop_words):
                # print("stop words:",token)
                continue
            self.local_word_counter += 1
            if token not in unique:
                freq[token] = 1
                unique.add(token)
            else:
                freq[token] += 1
        return

    def weighted(self, filename):
        with open("./WEBPAGES_RAW/" + filename) as file:
            soup = BeautifulSoup(file, features="lxml")
        [x.extract() for x in soup(['script', 'style', 'link'])]
        text = soup.get_text()
        for i in soup.find_all(['b', 'strong', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'title']):
            tag_str = str(i)
            if tag_str[:2] == '<b' or str(i)[:7] == "<strong" or tag_str[:3] == "<h6":
                text += (" " + i.get_text() + " ")
            if tag_str[:3] == "<h1":
                text += (" " + i.get_text() + " ") * 6
            if tag_str[:3] == "<h2":
                text += (" " + i.get_text() + " ") * 5
            if tag_str[:3] == "<h3":
                text += (" " + i.get_text() + " ") * 4
            if tag_str[:3] == "<h4":
                text += (" " + i.get_text() + " ") * 3
            if tag_str[:3] == "<h5":
                text += (" " + i.get_text() + " ") * 2
            if tag_str[:6] == "<title":
                self.local_title = i.get_text().lower()
                text += (" " + i.get_text() + " ") * 3
        return text

    def calculate_tf(self, tf):
        return (1+math.log10(tf))

    def token_in_title(self, token):
        return 1 if token in self.local_title else 0

    def parse_file(self, filename):
        self.local_word_counter = 0
        freq = {}
        unique = set()
        lines = self.weighted(filename).splitlines()
        [self.parse_line(i, freq, unique) for i in lines]
        self.all_words.update(unique)
        for i in freq:
            # print(self.calculate_tf(freq[i]))
            temp = {filename + " " + str(self.token_in_title(i)): self.calculate_tf(freq[i])}
            self.db.zadd(i, temp)

    def connect_to_redis(self):
        try:
            self.db = redis.Redis(host='localhost', port=6379, db=0)
            # self.db.flushdb()
        except Exception as e:
            print(e)

    def build(self):
        for i in self.map_js:
            self.page_counter += 1
            # Avoid txt trap
            if i not in ("39/373", "35/269", "0/438"):
                self.parse_file(i)
            print(self.page_counter)
            # if self.page_counter > 100:
            #     break

        report = open("report.txt", 'w')
        report.write("The total documents in corpus:" + str(self.page_counter) + "\n")
        report.write("The number of unique words is :" + str(len(self.all_words)) + "\n")

        report.close()

    def run(self,raw):
        print("raw is :",raw)
        self.db.delete('p3_result')
        query = raw.split()
        result_dict={}
        if len(query) == 1:
            results = self.db.zrange(query[0], 0, 15, desc=True)
        else:
            keys={}
            for i in query:
                n_of_doc=self.db.zcard(i)
                idf=math.log10(self.all_words_fix/n_of_doc)
                keys[i]=idf
            self.db.zinterstore("p3_result",keys)
            results=self.db.zrange('p3_result', 0, 15, desc=True)

        for i in results:
            temp= i.decode("utf-8").split()
            result_dict[self.map_js[temp[0]]]=temp[1]


        return result_dict




def main():

    ins = IcsSearchEngine()
    ins.connect_to_redis()
    # ins.build()
    print(ins.run('computer science'))


if __name__ == "__main__":
    main()
