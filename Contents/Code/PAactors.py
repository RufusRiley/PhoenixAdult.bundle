class PhoenixActors:
    actorsTable = None
    photosTable = None
    actorsNum = 0
    def __init__(self):
        self.actorsTable = [None] * 100
        self.photosTable = [None] * 100
        self.actorsNum = 0
    def addActor(self,newActor,newPhoto):
        self.actorsTable[self.actorsNum] = newActor
        self.photosTable[self.actorsNum] = newPhoto
        self.actorsNum = self.actorsNum + 1
    def clearActors(self):
        self.actorsNum = 0
    def processActors(self,metadata):
        actorsProcessed = 0
        while actorsProcessed < self.actorsNum:
            skip = False
            # Save the potentional new Actor or Actress to a new variable, replace any &nbsp; with a true space, and strip off any surrounding whitespace
            newActor = self.actorsTable[actorsProcessed].replace("\xc2\xa0", " ").strip()
            
            ##### Skip an actor completely; this could be used to filter out male actors if desired
            if "Bad Name" == newActor:
                skip = True

            ##### Replace by actor name; for actors that have different aliases in the industry
            if "Doris Ivy" == newActor:
                newActor = "Gina Gerson"

            ##### Replace by site + actor; use when an actor just has an alias or abbreviated name on one site
            if metadata.tagline == "GloryHoleSecrets" and "Brandi B" == newActor:
                newActor = "Brandi Bae"

            if not skip:
                role = metadata.roles.new()
                role.name = newActor
                role.photo = self.photosTable[actorsProcessed]
            actorsProcessed = actorsProcessed + 1
