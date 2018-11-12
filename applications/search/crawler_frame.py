import logging
from datamodel.search.Yyuan13Jianl9Diyueg_datamodel import Yyuan13Jianl9DiyuegLink, OneYyuan13Jianl9DiyuegUnProcessedLink
from spacetime.client.IApplication import IApplication
from spacetime.client.declarations import Producer, GetterSetter, Getter
from lxml import html,etree
import re, os
from time import time
from uuid import uuid4

from urlparse import urlparse, parse_qs
from uuid import uuid4

from collections import defaultdict

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"


@Producer(Yyuan13Jianl9DiyuegLink)
@GetterSetter(OneYyuan13Jianl9DiyuegUnProcessedLink)
class CrawlerFrame(IApplication):

    app_id = "Yyuan13Jianl9Diyueg"

    def __init__(self, frame):
        self.app_id = "Yyuan13Jianl9Diyueg"
        self.frame = frame


    def initialize(self):
        self.count = 0
        links = self.frame.get_new(OneYyuan13Jianl9DiyuegUnProcessedLink)
        if len(links) > 0:
            print "Resuming from the previous state."
            self.download_links(links)
        else:
            l = Yyuan13Jianl9DiyuegLink("http://www.ics.uci.edu/")
            print l.full_url
            self.frame.add(l)

    def update(self):
        unprocessed_links = self.frame.get_new(OneYyuan13Jianl9DiyuegUnProcessedLink)
        if unprocessed_links:
            self.download_links(unprocessed_links)

    def download_links(self, unprocessed_links):
        for link in unprocessed_links:
            print "Got a link to download:", link.full_url
            downloaded = link.download()
            links = extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(Yyuan13Jianl9DiyuegLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
    
def extract_next_links(rawDataObj):
    outputLinks = []
    '''
    rawDataObj is an object of type UrlResponse declared at L20-30
    datamodel/search/server_datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded. 
    The frontier takes care of that.
    
    Suggested library: lxml
    '''
    # global most_out_count
    # global most_out_link
    # print rawDataObj.url.encode("utf-8"), rawDataObj.url
    try:

        # create an lxml HTML element object containing the page's entire HTML
        content_html = html.document_fromstring(rawDataObj.content)

        # modifying every link in the document to make it absolute e.g. /path.html -> http:xxx/path.html
        content_html.make_links_absolute("http://www.ics.uci.edu/")

        # The .iterlinks() method returns a generator of tuples that
        # yields the element, attribute, link, and position of every link on the page.
        # In this case, we are only interested in the link, which is at the index of 2 in every tuple.'
        for item in content_html.iterlinks():
            outputLinks.append(item[2])

        # count most out link url
        # if (len(outputLinks) > most_out_count) :
        #     most_out_count = len(outputLinks)
        #     most_out_link = rawDataObj.url

    except Exception as e:
        print e

        # print most_out_count
        # print most_out_link
    return outputLinks

def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be
    downloaded or not.
    Robot rules and duplication rules are checked separately.
    This is a great place to filter out crawler traps.
    '''

    # e.g. urlparse('http://www.cwi.nl:80/%7Eguido/Python.html')
    # ParseResult(scheme='http', netloc='www.cwi.nl:80', path='/%7Eguido/Python.html',
    # params='', query='', fragment='')
    parsed = urlparse(url)

    # global subdomain
    # subdomain = defaultdict(int)
    # subdomain[parsed.hostname]+=1
    # print subdomain

    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        paths = re.split("/", parsed.path)

        return ".ics.uci.edu" in parsed.hostname \
            and not re.search("\?calender", parsed.path.lower()) \
            and repeat_len(paths) \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())



    except TypeError:
        print ("TypeError for ", parsed)
        return False

def repeat_len(paths):

    # check len path of url
    # check looping url trap
    # valid_long = True if max([len(path) for path in paths]) < 100 else False
    # valid_repeat = all([paths.count(path) < 5 for path in paths])

    if (len(paths) > 15):
        return False
    for path in paths:
        if (len(path) > 100):
            return False
    return all([paths.count(path) < 5 for path in paths])