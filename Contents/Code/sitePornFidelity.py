import PAsearchSites
import PAgenres
import re

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchPageContent = HTTP.Request("https://www.pornfidelity.com") #The search page seems to redirect to PornFidelity.com if you didn't just come from there, so I open this first to trick it...
    searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/search/?site=2&page=1&search=" + encodedTitle)
    if str(searchPageContent).find('No episodes found, please try again') != -1:
        #Log(encodedTitle)
        #Try again with a shortened title
        shortTitle=re.sub(r"[eE][0-9][0-9]*%20","",encodedTitle)
        shortTitle=re.sub(r"^([^%][^%]*%20[^%][^%]*)%20.*$",r"\1",shortTitle)
        Log(encodedTitle + " became " + shortTitle)
        searchPageContent = HTTP.Request("https://www.pornfidelity.com/episodes/search/?site=2&page=1&search=" + shortTitle)

    searchPageContent = str(searchPageContent).split('":"')
    searchPageResult = searchPageContent[len(searchPageContent)-1][:-2]
    searchPageResult = searchPageResult.replace('\\n',"").replace('\\',"")
    #Log(searchPageResult)
    searchResults = HTML.ElementFromString(searchPageResult)
    for searchResult in searchResults.xpath('//div[contains(@class,"d-flex")]'):
        titleNoFormatting = searchResult.xpath('.//a[@class="text-pf"]')[0].text_content().strip()
        Log(titleNoFormatting)
        curID = searchResult.xpath('.//a[@class="text-pf"]')[0].get('href')
        curID = curID.replace('/','_')
        curID = curID[8:-19]
        Log("ID: " + curID)
        releasedDate = searchResult.xpath('.//div[contains(@class,"text-left")]')[0].text_content().strip()[10:]
        if ", 20" not in releasedDate:
            releasedDate = releasedDate + ", " + str(datetime.now().year)
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        if searchByDateActor != True:
            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
        else:
            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %m, $Y')
            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
        titleNoFormatting = titleNoFormatting + " [" + PAsearchSites.getSearchSiteName(siteNum) + ", " + releasedDate + "]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

    return results


def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('_','/')

    url = "https://" + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    metadata.studio = "PornFidelity"
    metadata.summary = detailsPageElements.xpath('//p[contains(@class,"card-text")]')[0].text_content()
    metadata.title = detailsPageElements.xpath('//h4')[0].text_content()[36:].strip()
    tagline = "PornFidelity"
    Log(metadata.title)
    metadataParts = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//h4')
    for metadataPart in metadataParts:
        if "Published" in metadataPart.text_content():
            releasedDate = metadataPart.text_content()[39:49]
            Log(releasedDate)
            date_object = datetime.strptime(releasedDate, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year 

    metadata.tagline = tagline
    metadata.collections.clear()
    metadata.collections.add(tagline)

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre("Hardcore")
    movieGenres.addGenre("Heterosexual")

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[contains(@class,"episode-summary")]//a[contains(@href,"/models/")]')
    if len(actors) > 0:
        for actorLink in actors:
            actorName = actorLink.text_content()
            actorPageURL = actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorPhotoURL = actorPage.xpath('//img[@class="img-fluid"]')[0].get("src")
            movieActors.addActor(actorName,actorPhotoURL)

    # Posters/Background
    valid_names = list()
    pageSource = str(HTTP.Request(url))
    posterStartPos = pageSource.index('poster: "')
    posterEndPos = pageSource.index('"',posterStartPos+10)
    background = pageSource[posterStartPos+9:posterEndPos]
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    try:
        metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    except:
        pass
    try:
        metadata.posters[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    except:
        pass


    
    return metadata
