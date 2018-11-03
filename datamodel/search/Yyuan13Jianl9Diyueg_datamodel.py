'''
Created on Oct 20, 2016
@author: Rohan Achar
'''
from rtypes.pcc.attributes import dimension, primarykey, predicate
from rtypes.pcc.types.subset import subset
from rtypes.pcc.types.set import pcc_set
from rtypes.pcc.types.projection import projection
from rtypes.pcc.types.impure import impure
from datamodel.search.server_datamodel import Link, ServerCopy

@pcc_set
class Yyuan13Jianl9DiyuegLink(Link):
    USERAGENTSTRING = "Yyuan13Jianl9Diyueg"

    @dimension(str)
    def user_agent_string(self):
        return self.USERAGENTSTRING

    @user_agent_string.setter
    def user_agent_string(self, v):
        # TODO (rachar): Make it such that some dimensions do not need setters.
        pass


@subset(Yyuan13Jianl9DiyuegLink)
class Yyuan13Jianl9DiyuegUnprocessedLink(object):
    @predicate(Yyuan13Jianl9DiyuegLink.download_complete, Yyuan13Jianl9DiyuegLink.error_reason)
    def __predicate__(download_complete, error_reason):
        return not (download_complete or error_reason)


@impure
@subset(Yyuan13Jianl9DiyuegUnprocessedLink)
class OneYyuan13Jianl9DiyuegUnProcessedLink(Yyuan13Jianl9DiyuegLink):
    __limit__ = 1

    @predicate(Yyuan13Jianl9DiyuegLink.download_complete, Yyuan13Jianl9DiyuegLink.error_reason)
    def __predicate__(download_complete, error_reason):
        return not (download_complete or error_reason)

@projection(Yyuan13Jianl9DiyuegLink, Yyuan13Jianl9DiyuegLink.url, Yyuan13Jianl9DiyuegLink.download_complete)
class Yyuan13Jianl9DiyuegProjectionLink(object):
    pass
