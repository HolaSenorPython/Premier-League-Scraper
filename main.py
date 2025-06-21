import requests
from bs4 import BeautifulSoup

URL = "https://www.premierleague.com/stats"
goal_stats = [] # List of Goal scorers
assist_stats = [] # List of assisters

#----------FUNCTIONS FOR SCRAPING-----------#
def get_top_prem_stats():
    global goal_stats, assist_stats
    """This function scrapes for the VERY top goalscorers and assisters."""
    goal_stats.clear() # Clear the list incase it isn't empty to prevent errors
    assist_stats.clear() # DON'T do in the other function because it will clear the 1. ranked player
    try:
        response = requests.get(URL) # Get the url
        response.raise_for_status() # Raise error if there is one
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong while trying to access the Premier League Website: {e} ❌")
        exit()

    # Parse through the text (which is the html file returned) in html parser mode
    soup = BeautifulSoup(response.text, "html.parser")

    # First, get ALL the 1ST RANK stats and filter
    top_everything = soup.find_all('div', class_='top-stats__hero-stats') # All first ranked people in passing, goals, etc.
    top_scorer_n_assister_divs = top_everything[0:2] # Just the goals and assists div

    for index, div in enumerate(top_scorer_n_assister_divs): # do this for the top scorer stats div and top assister stats div
        info_div = div.find('div', class_='top-stats__hero-info') # find the info div
        stat_div = div.find('div', class_='top-stats__hero-stat') # find the actual stat div
        stat = stat_div.get_text(strip=True) # Get the actual statistic text stripped

        if index == 0: # Sooo if we're on the top goalscorer rn,
            info_div_parts = info_div.find_all() # Get all the nested divs in info div
            ranking = info_div_parts[0]
            first_name = info_div_parts[1]
            last_name = info_div_parts[2]
            full_name = first_name.get_text(strip=True) + " " + last_name.get_text(strip=True)
            # Merge the first n last name into one
            goal_scorer_tuple = (ranking.get_text(strip=True), full_name, stat)
            goal_stats.append(goal_scorer_tuple)

        elif index == 1: # But if this is the assister div
            info_div_parts = info_div.find_all()  # Get all the nested divs in info div
            ranking = info_div_parts[0]
            first_name = info_div_parts[1]
            last_name = info_div_parts[2]
            full_name = first_name.get_text(strip=True) + " " + last_name.get_text(strip=True)
            assister_tuple = (ranking.get_text(strip=True), full_name, stat)
            assist_stats.append(assister_tuple)

def get_other_prem_stats():
    global goal_stats, assist_stats
    """Function gets the other 9 goalscorers and assisters."""

    try:
        response = requests.get(URL) # Get the url
        response.raise_for_status() # Raise error if there is one
    except requests.exceptions.RequestException as e:
        print(f"Something went wrong while trying to access the Premier League Website: {e}❌")
        exit()

    # Parse through the text (which is the html file returned) in html parser mode
    soup = BeautifulSoup(response.text, "html.parser")

    # This is where the steps are different. Grab the other 9 for ALL the top stats. (other 9 goalscorers, assisters etc.)
    other_9_everything = soup.find_all('li', class_='top-stats__row top-stats__row--')
    # There are 8 boxes containing top 10 stats, so 80 players overall. (counting repeats) The other 9 for each adds up
    # to 72 players 8 boxes. If I want the first 2 boxes (goals and assisters), I want the first 18 players when filtering
    # by top 9.
    other_9_scorers_n_assisters = other_9_everything[0:18]
    # For all the goalscorer list elements, get the info and add it to our goal stats list:
    for li_elem in other_9_scorers_n_assisters[0:9]:
        ranking = li_elem.find('div', class_='top-stats__row-pos').get_text(strip=True) # Find the ranking element and its text
        statistic = li_elem.find('div', class_='top-stats__row-stat').get_text(strip=True) # Statistic element and its text
        player_name = li_elem.find('a', class_='top-stats__row-name').get_text(strip=True)
        goal_scorer_tuple = (ranking, player_name, statistic)
        goal_stats.append(goal_scorer_tuple)
    # Now for all the ASSISTERS:
    for li_elem in other_9_scorers_n_assisters[9:]:
        ranking = li_elem.find('div', class_='top-stats__row-pos').get_text(strip=True)  # Find the ranking element and its text
        statistic = li_elem.find('div', class_='top-stats__row-stat').get_text(strip=True)  # Statistic element and its text
        player_name = li_elem.find('a', class_='top-stats__row-name').get_text(strip=True)
        assister_tuple = (ranking, player_name, statistic)
        assist_stats.append(assister_tuple)

    print(f"The goal scorers: {goal_stats}")
    print(f"The assisters: {assist_stats}")

#--------FUNCTION FOR MAKING TEXT FILES and HANDLING THEM---------#
def tuple_formatter(le_tuple, stat_list): # This function will format all the tuples into a pretty f-string
    # Basically, depending on the list we pass in, it will return a different f-string
    player_rank = le_tuple[0]
    player_name = le_tuple[1]
    player_stat = le_tuple[2]
    if stat_list == goal_stats:
        return f"{player_name} was #{player_rank} with {player_stat} goals! ⚽🥅"
    elif stat_list == assist_stats:
        return f"{player_name} was #{player_rank} with {player_stat} assists! ⚽🤝"

# Function will create a new text file with the scraped data
def write_to_file():
    global goal_stats, assist_stats
    try:
        with open("stats.txt", 'w', encoding='utf-8') as file:
            file.write("Top Scorers\n\n") # Denote this is the 'Top Scorers section'
            for scorer in goal_stats: # Write all the goalscorers to the file
                goalscorer = tuple_formatter(scorer, goal_stats)
                file.write(f"{goalscorer}\n")
            file.write('\n') # Write a singular new line element lol
            file.write("Top Assisters\n\n") # Denote this is the 'Top Assisters section'
            for assister in assist_stats:
                assist_msg = tuple_formatter(assister, assist_stats)
                file.write(f"{assist_msg}\n")
        print("Your file is ready! ✅ Look for it in this folder.")
    except (OSError, IOError) as e:
        print(f"Something went wrong when writing to file: {e}")

# Start User prompting
print("Howdy! 🤠 This program is going to get the latest premier league\n"
      "stats and save them into a text file for you.\n")
yes_or_no = input("Would you like me to get data from the Premier League for you?\n"
                  "Type 'yes' or 'no'.\n").lower().strip()

# Input check
if yes_or_no == 'yes':
    print("Ok!")
    get_top_prem_stats() # Get 1. in the goalscorer and assister
    get_other_prem_stats() # Get the other 9 for the above ^
    write_to_file() # Make the text file for the user
elif yes_or_no == 'no':
    print("I see. Thanks for your time.")
    exit()