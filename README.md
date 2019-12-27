# IMDb Web scraping (top ranked movies)

## Description
This script gathers data from the top ranked movies in imdb along with its actors and directors. This data is saved in json format in four files:
* artists.json - columns: 'id', 'artistName', 'birthPlace', 'birthDate', 'deathDate', 'pictureurl', 'bio', 'realName' and 'height';
* movies.json - columns: 'id', 'title', 'runtime', 'releaseDate', 'plot' and 'posterUrl';
* movieArtists.json - columns: 'movieId', 'artistsId' and 'roleId' (1 if actor, 2 if director);
* movieGenres.json - columns: 'movieId' and 'genreId' (genres declared in dictionary 'genresDic' inside imdbWebScraperTopRated).

## Used libraries
* BeautifulSoup
* requests
* json
* lxml
* os
* timeit