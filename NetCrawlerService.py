# Web Crewler
import urllib.request as URL_REQUEST
import math as MATH
from bs4 import BeautifulSoup

from obj.NetImage import NetImage

class NetCrawlerService:
    MAX_FLOOR_PER_PAGE = 20 # acconding to bahamut page, each page have 20 floor
    def __init__(self):
        self.netImageList = []
        pass

    def getScore( self, element ):
        """let score(str) convert to integer"""
        scoreStr = element.select( "span" )[0].text
        if scoreStr ==  "爆":
            return 9999
        elif scoreStr == "X":
            return -9999
        elif scoreStr == "-":
            return 0
        else:
            return int(scoreStr)       

    def getUrlData( self, url ):
        # example1 url: https://forum.gamer.com.tw/C.php?bsn=60076&snA=5993618&tnum=54
        # example2 url: https://forum.gamer.com.tw/C.php?page=2&bsn=60076&snA=5993618&tnum=54
        url        = url.split( "bsn=" )[1]        # 60076&snA=5993618&tnum=54
        
        temp       = url.split( "&snA=" )
        bsn        = temp[0]                       # 60076
        url        = temp[1].split( "&tnum=" )    # 5993618&tnum=54
        snA        = url[0]
        maxFloor   = int( url[1] )

        maxPage = MATH.ceil(maxFloor / self.MAX_FLOOR_PER_PAGE)

        print( "bsn:", bsn, "  snA:", snA, "  max floor:", maxFloor, "   max page:", maxPage )

        return [bsn, snA, maxFloor, maxPage]
        
    def getData( self, url, floor=[1, 999999], outputDebugTxt=False ):
        """ get the bahamut image"""

        # get the info of url
        [bsn, snA, maxFloor, maxPage] = self.getUrlData( url )
       
        self.bsnPre     = bsn
        self.snaPre     = snA
        self.maxFloor   = maxFloor

        # setting floor
        currentMinPage = MATH.ceil( floor[0] / self.MAX_FLOOR_PER_PAGE )
        currentMaxPage = min( MATH.ceil( floor[1] / self.MAX_FLOOR_PER_PAGE ), maxPage )
        nowPage = currentMinPage
        
        # get every page of this form
        for nowPage in range(currentMinPage, currentMaxPage + 1):  
            url = "".join( ["https://forum.gamer.com.tw/C.php?", "page=", str(nowPage), "&bsn=", bsn, "&snA=", snA] )

            htmlRequest = URL_REQUEST.Request( url, headers={'User-Agent': 'Mozilla/5.0'} )
            htmlRaw     = URL_REQUEST.urlopen( htmlRequest ).read()

            soupHTML = BeautifulSoup( htmlRaw, "html.parser")
            
    

            # get whole articles in this page
            for article in soupHTML.select( "section" ):

                # check that aritcle is removed or not
                if article.has_attr( "id" ) == False:
                    continue
                
                if len( article.select( ".c-disable" ) ) >= 1:
                    continue

                # check floor, break if lower or exceed
                nowFloor = int( article.select( ".floor" )[0][ "data-floor" ] )
                if nowFloor < floor[0] or nowFloor > floor[1]:
                    break

                # get this artcle infomation
                authorID        = article.select( ".userid" )[0].text
                authorName      = article.select( ".username" )[0].text
                articleGP       = self.getScore( article.select( ".postgp" )[0] )
                articleBP       = self.getScore( article.select( ".postbp" )[0] )

                # initial netImage builder
                netImageBuilder = NetImage.getBuilder()
                netImageBuilder.setAuthor( authorID, authorName )
                netImageBuilder.setFloor( nowFloor )
                netImageBuilder.setGP( articleGP )
                netImageBuilder.setBP( articleBP )
                                            
                # getting image url
                for imgURL in article.select( ".photoswipe-image" ):
                    netImageBuilder.setImageUrl( imgURL[ "href" ] )
                    self.netImageList.append( netImageBuilder.build() )


        # just verify web crawler are correct or not
        if( outputDebugTxt == True ):
            text_file = open("result.txt", "wb")
            for netImage in netImageList:
                text_file.write( netImage.toString() )
            text_file.close()


        return self.netImageList

        
        
