class CrawlerError(Exception): pass
class TransientError(CrawlerError): pass
class PermanentError(CrawlerError): pass
class NetworkError(CrawlerError): pass
class ParseError(CrawlerError): pass