
class NetImageBuilder:
    def __init__( self ):
        pass
    
    def setAuthor( self, id, name ):
        """set article author"""
        self.id = id
        self.name = name
        return self

    def setFloor( self, floor):
        """set article floor"""
        self.floor = floor
        return self

    def setGP( self, gp ):
        """set article GP"""
        self.gp = gp
        return self

    def setBP( self, bp ):
        """set article BP"""
        self.bp = bp
        return self

    def setImageUrl( self, url ):
        """set image url"""
        self.url = url
        return self


    def build( self ):
        """build the NetImage Object"""
        return NetImage( authorID=self.id, authorName=self.name, floor=self.floor, gp=self.gp, bp=self.bp, imageUrl=self.url )

class NetImage:
    #=============================================================================================================
    def __init__( self, authorID, authorName, floor, gp, bp, imageUrl ):
        self._authorID   = authorID
        self._authorName = authorName
        self._floor      = floor
        self._gp         = gp 
        self._bp         = bp
        self._imageUrl   = imageUrl

    def print( self ):
        """print this article all of infomation"""
        print( "authorID:", self._authorID, "   authorName:", self._authorName, "  floor:", self._floor, "   GP:", self._gp, "   BP:", self._bp  )
        print(  self._imageUrl, "\n" )

    def toString( self ):
        """print this article all of infomation"""
        return "".join( ["authorID:", self._authorID, "   authorName:", self._authorName, "  floor:",  str(self._floor), "   GP:", str(self._gp), "   BP:", str(self._bp), "\n",  self._imageUrl, "\n\n"] ).encode("utf8")

    def getAuthorName(self):
        """get author name"""
        return self._authorName
    
    def getAuthorID(self):
        return self._authorID

    def getFloor(self):
        return self._floor
    
    def getGP(self):
        return self._gp

    def getBP(self):
        return self._bp

    def getImageUrl(self):
        return self._imageUrl

    @staticmethod
    def getBuilder():
        return NetImageBuilder()