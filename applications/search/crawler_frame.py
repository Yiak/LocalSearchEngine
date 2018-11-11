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
    print rawDataObj.url.encode("utf-8"), rawDataObj.url
    try:

        # create an lxml HTML element object containing the page's entire HTML
        content_html = html.document_fromstring(rawDataObj.content)

        # modifying every link in the document to make it absolute e.g. /sub.html -> http:xxx/sub.html
        content_html.make_links_absolute(base_href="http://www.ics.uci.edu/", resolve_base_href=True)

        # The .iterlinks() method returns a generator of tuples that
        # yields the element, attribute, link, and position of every link on the page.
        # In this case, we are only interested in the link, which is at the index of 2 in every tuple.'
        for item in content_html.make_links_absolute():
            outputLinks.append(item[2])

    # to do: infinite trap
    # to do: infinite loop site
    # to do: max out link

    except Exception as e:
        print e
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
    if parsed.scheme not in set(["http", "https"]):
        return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower()) \
            and not re.search("\?calender", parsed.path.lower())  # regex\?

    except TypeError:
        print ("TypeError for ", parsed)
        return False

