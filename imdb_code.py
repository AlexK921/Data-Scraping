from imdb_helper_functions import url_to_soup, current_year, save_pairwise_distances_to_csv, read_csv
from imdb_helper_functions import create_graph, create_graph_per_distance, draw_graph, draw_graph_with_filtered_edges
from imdb_helper_functions import save_to_text_file, read_from_text_file
from imdb_helper_functions import build_word_cloud


# main functions
def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None):
    movies = []
    this_year = current_year()
    for movie in actor_page_soup.find_all('div', class_='filmo-row'):
        if num_of_movies_limit is not None and len(movies) >= num_of_movies_limit:
            break
        if movie.find('span', class_='in_production'):
            continue
        year_column = movie.find('span', class_='year_column')
        if year_column:
            year_text = year_column.text.strip()
            if year_text.isdigit() and int(year_text) <= this_year:
                movie_text = movie.text
                if not any(keyword in movie_text for keyword in ["TV Series", "Short", "Video Game", "Video short", "Video", "TV Movie", "TV Mini-Series", "TV Series short", "TV Special"]):
                    movie_url = 'https://www.imdb.com' + movie.find('a')['href']
                    movies.append((movie.find('b').text, movie_url))
    return movies


def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    actors = []
    for actor in cast_page_soup.find_all('td', class_='primary_photo'):
        if num_of_actors_limit is not None and len(actors) >= num_of_actors_limit:
            break
        actor_url = 'https://www.imdb.com' + actor.find('a')['href']
        actors.append((actor.find('img')['title'], actor_url))
    return actors


actors_for_movie_cash = {}
movies_for_actor_cash = {}
def get_movie_distance(actor_start_url, actor_end_url, num_of_actors_limit=None, num_of_movies_limit=None):
    actor_start_page_soup = url_to_soup(actor_start_url + 'fullcredits').find('div', class_='filmo-category-section')
    actor_start_movies = get_movies_by_actor_soup(actor_start_page_soup, num_of_movies_limit)
    actor_end_page_soup = url_to_soup(actor_end_url + 'fullcredits').find('div', class_='filmo-category-section')
    actor_end_movies = get_movies_by_actor_soup(actor_end_page_soup, num_of_movies_limit)

    if actor_start_url not in movies_for_actor_cash:
        movies_for_actor_cash[actor_start_url] = actor_start_movies
    if actor_end_url not in movies_for_actor_cash:
        movies_for_actor_cash[actor_end_url] = actor_end_movies
    current_distance = 1
    for movie in actor_start_movies:
        for movie2 in actor_end_movies:
            if movie[0] == movie2[0]:
                return int(current_distance)
    current_distance += 1
    actors_list_for_start_actor = []
    actors_list_for_end_actor = []
    # Limit for current_distance is 3. Is current_distance > 3 - no connection between two actors.
    while current_distance <= 3:
        for movie in actor_start_movies:
            if movie[1] not in actors_for_movie_cash:
                actors_for_movie_cash[movie[1]] = get_actors_by_movie_soup(url_to_soup(movie[1] + 'fullcredits'), num_of_actors_limit)
            actors_list_for_start_actor += actors_for_movie_cash[movie[1]]
        for movie in actor_end_movies:
            if movie[1] not in actors_for_movie_cash:
                actors_for_movie_cash[movie[1]] = get_actors_by_movie_soup(url_to_soup(movie[1] + 'fullcredits'), num_of_actors_limit)
            actors_list_for_end_actor += actors_for_movie_cash[movie[1]]

        if actor_start_url not in actors_for_movie_cash:
            actors_for_movie_cash[actor_start_url] = actors_list_for_start_actor
        if actor_end_url not in actors_for_movie_cash:
            actors_for_movie_cash[actor_end_url] = actors_list_for_end_actor

        for actor in actors_list_for_start_actor:
            for actor2 in actors_list_for_end_actor:
                if actor[0] == actor2[0]:
                    return int(current_distance)
        current_distance += 1
    return float('inf')


def get_movie_descriptions_by_actor_soup(actor_page_soup):
    all_movies = get_movies_by_actor_soup(actor_page_soup)
    summaries = []
    for movie in all_movies:
        title, url = movie
        summary_url = (url+'plotsummary').replace('?', '/?')
        soup = url_to_soup(summary_url)
        summary = soup.find('div', class_='ipc-html-content-inner-div')
        if summary:
            summary = summary.text
            summaries.append((title, summary))
    return summaries


# part for launching the program
actors = [
    ('Dwayne Johnson', 'https://www.imdb.com/name/nm0425005/'),
    ('Chris Hemsworth', 'https://www.imdb.com/name/nm1165110/'),
    ('Robert Downey Jr.', 'https://www.imdb.com/name/nm0000375/'),
    ('Akshay Kumar', 'https://www.imdb.com/name/nm0474774/'),
    ('Jackie Chan', 'https://www.imdb.com/name/nm0000329/'),
    ('Bradley Cooper', 'https://www.imdb.com/name/nm0177896/'),
    ('Adam Sandler', 'https://www.imdb.com/name/nm0001191/'),
    ('Scarlett Johansson', 'https://www.imdb.com/name/nm0424060/'),
    ('Sofia Vergara', 'https://www.imdb.com/name/nm0005527/'),
    ('Chris Evans', 'https://www.imdb.com/name/nm0262635/')
    ]

# scrape distances
def calculate_pairwise_distances(actors_list):
    pairwise_distances = {}
    for i, actor_start in enumerate(actors_list):
        pairwise_distances[actor_start] = {}
        for j, actor_end in enumerate(actors_list):
            if i == j:
                distance = 0
            else:
                distance = get_movie_distance(actor_start[1], actor_end[1], 5, 5)
            pairwise_distances[actor_start][actor_end] = distance
    return pairwise_distances


pairwise_distances = calculate_pairwise_distances(actors)
csv_file_path = 'distances.csv'
save_pairwise_distances_to_csv(pairwise_distances, actors, csv_file_path)

# draw graph
data = read_csv('distances.csv')
G = create_graph(data)
draw_graph(G)
# draw graph with filtered edges
for i in range(1, 3):
    G = create_graph_per_distance(data, i)
    draw_graph_with_filtered_edges(G, i)

# scrape movie descriptions
for actor in actors:
    name, url = actor
    actor_page_soup = url_to_soup(url + 'fullcredits').find('div', class_='filmo-category-section')
    descriptions = get_movie_descriptions_by_actor_soup(actor_page_soup)
    filename = f"movie_descriptions_{name.replace(' ', '_')}.txt"
    save_to_text_file(descriptions, filename)

# build word cloud
for actor in actors:
    name, url = actor
    filename = f"movie_descriptions_{name.replace(' ', '_')}.txt"
    descriptions = read_from_text_file(filename)
    descriptions = [description for title, description in descriptions]
    print(f"Word cloud for {name}:")
    build_word_cloud(descriptions, name)

