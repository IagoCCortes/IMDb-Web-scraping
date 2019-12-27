from bs4 import BeautifulSoup as bs
import requests
import json
import lxml
import os
import timeit

# def cleanhtml(raw_html):
#   cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
#   cleantext = re.sub(cleanr, '', raw_html)
#   return cleantext

genresDic = {'Action': 1, 'Adventure': 2, 'Animation': 3, 'Biography': 4,
             'Comedy': 5, 'Crime': 6, 'Documentary': 7, 'Drama': 8,
             'Family': 9, 'Fantasy': 10, 'Film-Noir': 11, 'History': 12,
             'Horror': 13, 'Music': 14, 'Musical': 15, 'Mystery': 16,
             'Romance': 17, 'Sci-Fi': 18, 'Short Film': 19, 'Sport': 20,
             'Superhero': 21, 'Thriller': 22, 'War': 23, 'Western': 24}

roles = ['actor', 'director']
totalTime = 0.0
starsList = list
artistIterator = 1             
movieIterator = 1
artists = {}
source = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250').text
soup = bs(source, 'lxml')
movieHeaders = soup.find_all('td', class_='titleColumn')
with open('movies.json', 'w+') as mFile, open('artists.json', 'w+') as aFile, open('movieGenres.json', 'w+') as mGFile, open('movieArtists.json', 'w+') as mAFile:
    mFile.write('{\n\t"movies": [\n')
    aFile.write('{\n\t"artists": [\n')
    mGFile.write('{\n\t"movieGenres": [\n')
    mAFile.write('{\n\t"movieArtists": [\n')


    for movieHeader in movieHeaders:
        start = timeit.default_timer()
        link = movieHeader.find('a', href=True)
        movieSource = requests.get('http://imdb.com' + link['href']).text
        movieSoup = bs(movieSource, 'lxml')

        for runtimeDiv in movieSoup.find_all('div', class_='txt-block'):
            runtimeStr = runtimeDiv.find('time')
            if runtimeStr != None:
                break

        try:
            runtime = runtimeStr.text.split()[0]
        except:
            runtime = None
        

        plot = movieSoup.find('div', attrs={'class': 'summary_text'}).text

        jsonString = movieSoup.find('script', attrs={'type': 'application/ld+json'}).text

        mData = json.loads(jsonString)

        title = mData['name']
        posterUrl = mData['image']
        releaseDate = mData['datePublished']
        movieData = {
            'id': movieIterator, 'title': title, 'runtime': runtime, 
            'releaseDate': releaseDate, 'plot': plot, 'posterUrl': posterUrl
        }

        # write to movies
        mFile.write('\t\t')
        json.dump(movieData, mFile)
        mFile.write(',\n')
        #################################

        genresKey = mData['genre']
        genres = []
        if isinstance(genresKey, str):
            genres.append(genresDic[genresKey])
        else:
            for genre in genresKey:
                genres.append(genresDic[genre])
        # write to movieGenres
        for genre in genres:
            movieGenreData = { 'MovieId': movieIterator, 'GenreId': genre}
            mGFile.write('\t\t')
            json.dump(movieGenreData, mGFile)
            mGFile.write(',\n')
        #################################
        for role in roles:
            stars = mData[role]
            if isinstance(stars, dict):
                starsList = []
                starsList.append(stars)
            else:
                starsList = stars
            for star in starsList:
                artistUrl = star['url'].split('/')[2]
                mAFile.write('\t\t')
                if artistUrl in artists.keys():
                    json.dump({ 'MovieId': movieIterator, 'ArtistId': artists[artistUrl], 'RoleId': (1 if role == 'actor' else 2)}, mAFile)
                    mAFile.write(',\n')
                    continue
                json.dump({ 'MovieId': movieIterator, 'ArtistId': artistIterator, 'RoleId': (1 if role == 'actor' else 2)}, mAFile)
                mAFile.write(',\n')
                artists[artistUrl] = artistIterator
                artistName = star['name']

                artistSource = requests.get('https://www.imdb.com/name/' + artistUrl).text
                artistDetailSource = requests.get('https://www.imdb.com/name/' + artistUrl + '/bio').text
                artistSoup = bs(artistSource, 'lxml')
                artistDetailSoup = bs(artistDetailSource, 'lxml')

                for place in artistSoup.find_all('div', attrs={'id': 'name-born-info'}):
                    try:
                        birthPlace = place.find_all('a')[2].text
                    except:
                        birthPlace = None

                jsonArtistString = artistSoup.find('script', attrs={'type': 'application/ld+json'}).text

                aData = json.loads(jsonArtistString)
                try:
                    pictureUrl = aData['image']
                except:
                    pictureUrl = None

                try:
                    birthDate = aData['birthDate']
                except:
                    birthDate = None
                
                try:
                    deathDate = aData['deathDate']
                except:
                    deathDate = None

                try:
                    bio = artistDetailSoup.find('div', attrs={'class': ['soda', 'odd']}).text
                except:
                    bio = None

                try:
                    realName = artistDetailSoup.find("td", text="Birth Name").find_next_sibling("td").text
                except:
                    realName = None

                try:
                    heightstr = artistDetailSoup.find("td", text="Height").find_next_sibling("td").text
                    digits = [int(s) for s in heightstr.split('(')[1] if s.isdigit()]
                    height = ''.join(map(str, digits))
                    if len(height) == 2 and height[0] in ['1','2']:
                        height += '0'
                except:
                    height = None

                artistsData = {
                    'id': artistIterator,
                    'artistName': artistName, 'birthPlace': birthPlace, 
                    'birthDate': birthDate, 'deathDate': deathDate,
                    'pictureurl': pictureUrl,
                    'bio': bio,
                    'realName': realName,
                    'height': height
                }
                # write to artists
                aFile.write('\t\t')
                json.dump(artistsData, aFile)
                aFile.write(',\n')
                artistIterator += 1
        #################################   

        
        print(str(movieIterator) + ' - ' + title)
        stop = timeit.default_timer()
        totalTime += (stop - start)
        print('Time: ', stop - start)
        if movieIterator == movieHeaders.__len__:
            break

        movieIterator += 1
    
    # deletes last comma and finishes the json format for all the files
    mFile.seek(mFile.tell() - 3, os.SEEK_SET)
    mFile.write('\n\t]\n}')
    aFile.seek(aFile.tell() - 3, os.SEEK_SET)
    aFile.write('\n\t]\n}')
    mGFile.seek(mGFile.tell() - 3, os.SEEK_SET)
    mGFile.write('\n\t]\n}')
    mAFile.seek(mAFile.tell() - 3, os.SEEK_SET)
    mAFile.write('\n\t]\n}')
    print('Runtime: ' + str(totalTime) + 's')