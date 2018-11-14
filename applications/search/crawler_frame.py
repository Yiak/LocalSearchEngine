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
        self.subdomain_dict=defaultdict(int)
        self.most_out_link_count=0
        self.most_out_link_url=''
        self.valid_url_count=0
        self.invalid_url_count=0



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
            links = self.extract_next_links(downloaded)
            for l in links:
                if is_valid(l):
                    self.frame.add(Yyuan13Jianl9DiyuegLink(l))

    def shutdown(self):
        print (
            "Time time spent this session: ",
            time() - self.starttime, " seconds.")
    
    def extract_next_links(self,rawDataObj):
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
        try:

            # create an lxml HTML element object containing the page's entire HTML
            content_html = html.document_fromstring(rawDataObj.content)

            # modifying every link in the document to make it absolute e.g. /path.html -> http:xxx/path.html
            content_html.make_links_absolute(rawDataObj.final_url.encode("utf-8") if rawDataObj.is_redirected else rawDataObj.url.encode("utf-8"))

            # The .iterlinks() method returns a generator of tuples that
            # yields the element, attribute, link, and position of every link on the page.
            # In this case, we are only interested in the link, which is at the index of 2 in every tuple.'
            for item in content_html.iterlinks():
                outputLinks.append(item[2].encode("utf-8"))

            if is_valid(rawDataObj.url):  
                

                self.valid_url_count += 1 
                

                if "https" in rawDataObj.url: 
                    self.subdomain_dict[rawDataObj.url[8: rawDataObj.url.index("ics.uci.edu")-1]] += 1
                else:
                    self.subdomain_dict[rawDataObj.url[7: rawDataObj.url.index("ics.uci.edu")-1]] += 1
            
                # count most out link url
                if len(outputLinks) > self.most_out_link_count:
                    self.most_out_link_url = rawDataObj.url 
                    self.most_out_link_count = len(outputLinks)
            else:
                self.invalid_url_count+=1
                
            # print ("!!in extract, the valid_count is " , self.valid_url_count)
            # print ("!!in extract, the invalid_count is " , self.invalid_url_count)
            # print("the most_out_link_url is:",self.most_out_link_url)
            # print("the most_out_link_count is:",self.most_out_link_count)

            if self.valid_url_count>3000:
                raise EnvironmentError

        except EnvironmentError as e:
            print "Exceed 3000 valid urls, now generate analytics file."
            
            analytics = open("analytics.txt","w") 
            analytics.write("Analytics:\n")
            
            analytics.write("Valid url count:"+str(self.valid_url_count)+"\n")
            # analytics.write("Invalid url count:"+str(self.invalid_url_count)+"\n")
            analytics.write("The page with the most outlinks: {} has {} outlinks".format(self.most_out_link_url, self.most_out_link_count) +'\n') 
            analytics.write("\nSubdomain pages count:\n")
            for i in self.subdomain_dict.items():
                analytics.write("Subdomain {} has {} pages\n".format(i[0], i[1])) 
            analytics.close() 

            print "Finished Analytics file, now program shutdown. "
            
            raise SystemExit
            # print most_out_count
            # print most_out_link

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
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        return False

    if "ics.uci.edu" not in url:
        return False

    if len(parsed.query) > 45:    
        return False
    if "wics" in url:
        return False
    if "mailto:" in url:
        return False
    if str(url).count("/") > 8:      
        return False
    if not url.startswith("http"):  
        return False
    if url == None:      
        return False
 
    #According to the info showed in amazon.ics.uci.edu, subdomain calendar should be avoided.
    if "calendar" in url:             
            return False
    try:
        return ".ics.uci.edu" in parsed.hostname \
            and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4"\
            + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
            + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
            + "|thmx|mso|arff|rtf|jar|csv"\
            + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        return False

