import PAsearchSites
import PAgenres

def posterAlreadyExists(posterUrl,metadata):
    for p in metadata.posters.keys():
        Log(p.lower())
        if p.lower() == posterUrl.lower():
            Log("Found " + posterUrl + " in posters collection")
            return True

    for p in metadata.art.keys():
        if p.lower() == posterUrl.lower():
            return True
    return False

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate, searchAll, searchSiteID):
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle)
    for searchResult in searchResults.xpath('//div[@class="scene"]'):
        Log(str(searchResult.get('href')))
        titleNoFormatting = searchResult.xpath('.//h4[@itemprop="name"]/a[1]')[0].text_content().strip()
        releaseDate = searchResult.xpath('.//small[@class="date"]')[0].text_content().strip().replace("Added: ", "")
        curID = searchResult.xpath('.//h4[@itemprop="name"]/a[1]')[0].get('href').replace('/','_').replace("?","!")
        lowerResultTitle = str(titleNoFormatting).lower()
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [TheDickSuckers] " + releaseDate, score = score, lang = lang))
    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')
    metadata.studio = 'Fabulous Cash'
    url = str(metadata.id).split("|")[0].replace('_','/').replace("!","?")
    detailsPageElements = HTML.ElementFromURL(url)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@itemprop="name"]')[0].text_content().strip()
    
    # Summary
    metadata.summary = detailsPageElements.xpath('//header[h1[@itemprop="name"]]/p[@itemprop="description"]')[0].text_content().strip()
    #paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
    metadata.collections.clear()
    tagline = "The Dick Suckers"
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.title = detailsPageElements.xpath('//h1[@itemprop="name"]')[0].text_content().strip()

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//header[h1[@itemprop="name"]]/p/a')

    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().strip('\n').lower()
            movieGenres.addGenre(genreName)


    # Release Date
    date = detailsPageElements.xpath('//header[h1[@itemprop="name"]]/p[contains(.,"Added:")]')
    if len(date) > 0:
        date = date[0].text_content().strip().replace("Added: ", "")
        date_object = datetime.strptime(date, '%m-%d-%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//header[h1[@itemprop="name"]]/h4/a')
    if len(actors) > 0:
        for actorLink in actors:
            actorName = str(actorLink.text_content().strip())
            actorPageURL = actorLink.get("href")
            actorPage = HTML.ElementFromURL(PAsearchSites.getSearchBaseURL(siteID)+actorPageURL)
            actorPhotoURL = actorPage.xpath('//div[@class="scene"][1]//img')[0].get("src")
            movieActors.addActor(actorName,actorPhotoURL)

    #Posters
    i = 1
    try:
        background = detailsPageElements.xpath('//aside//img')[0].get('src').replace("https:","http:")
        Log("BG DL: " + background)
        metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    except:
        pass

    return metadata
