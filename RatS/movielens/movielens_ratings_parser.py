import os
import re
import sys

from RatS.base.base_ratings_downloader import RatingsDownloader
from RatS.movielens.movielens_site import Movielens


class MovielensRatingsParser(RatingsDownloader):
    def __init__(self, args):
        super(MovielensRatingsParser, self).__init__(Movielens(args), args)
        self.downloaded_file_name = 'movielens-ratings.csv'

    def _parse_ratings(self):
        self._download_ratings_csv()
        self._rename_csv_file(self.downloaded_file_name)
        self.movies = self._parse_movies_from_csv(os.path.join(self.exports_folder, self.csv_filename))

    def _call_download_url(self):
        self.site.browser.get('https://movielens.org/api/users/me/movielens-ratings.csv')

    def _convert_csv_row_to_movie(self, row):
        movie = dict()

        if self.args and self.args.verbose and self.args.verbose >= 1:
            sys.stdout.write('\r===== {site_displayname}: reading movie from CSV: \r\n'.format(
                site_displayname=self.site.site_displayname
            ))
            for r in row:
                sys.stdout.write(r + '\r\n')
            sys.stdout.flush()

        year = self.__extract_year(movie, row)
        movie['title'] = row[5].replace(year, '').strip()

        movie[self.site.site_name.lower()] = dict()
        movie[self.site.site_name.lower()]['id'] = row[0]
        movie[self.site.site_name.lower()]['url'] = 'https://movielens.org/movies/{movie_url_path}'.format(
            movie_url_path=row[0]
        )
        movie[self.site.site_name.lower()]['my_rating'] = int(float(row[3]) * 2)

        self.__extract_imdb_informations(movie, row)
        self.__extract_tmdb_informations(movie, row)

        return movie

    @staticmethod
    def __extract_tmdb_informations(movie, row):
        movie['tmdb'] = dict()
        movie['tmdb']['id'] = row[2]
        movie['tmdb']['url'] = 'https://www.themoviedb.org/movie/{tmdb_id}'.format(tmdb_id=movie['tmdb']['id'])

    @staticmethod
    def __extract_imdb_informations(movie, row):
        movie['imdb'] = dict()
        movie['imdb']['id'] = row[1]
        if 'tt' not in movie['imdb']['id']:
            movie['imdb']['id'] = 'tt{imdb_id_number}'.format(imdb_id_number=row[1])
        movie['imdb']['url'] = 'http://www.imdb.com/title/{imdb_id}'.format(imdb_id=movie['imdb']['id'])

    @staticmethod
    def __extract_year(movie, row):
        find_year = re.findall(r'(\(\d{4}\))', row[5])
        if find_year:
            year = find_year[-1]
            movie['year'] = int(re.findall(r'\((\d{4})\)', row[5])[-1])
        else:  # no movie year in CSV
            year = '()'
            movie['year'] = 0
        return year
