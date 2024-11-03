"""
DRAFT
This script is designed to generate a Jazzercise setlist based on a csv file containing a given catalogue.
"""


import pandas as pd
import random
from datetime import datetime

# Import catalogue from csv file
jazzercise_catalogue = pd.read_csv('data/jazzercise_catalogue.csv')

# Clean dataframe as needed
jazzercise_catalogue['year'] = jazzercise_catalogue['year'].fillna(0)
jazzercise_catalogue['year'] = jazzercise_catalogue['year'].astype(int)
pd.set_option('future.no_silent_downcasting', True)
jazzercise_catalogue['descend_to_floor'] = jazzercise_catalogue['descend_to_floor'].fillna(False)
jazzercise_catalogue['ascend_to_stand'] = jazzercise_catalogue['ascend_to_stand'].fillna(False)

current_year = datetime.now().year
one_year_limit = current_year - 1
nine_year_limit = current_year - 9


def convert_length_to_seconds(length):
    """ Convert length in 'MM:SS' format to total seconds """
    minutes, seconds = map(int, length.split(':'))
    return minutes * 60 + seconds

def convert_seconds_to_length(seconds):
    """Convert total seconds to 'MM:SS' format."""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds}"


# Function for selecting a song by many parameters at once (used to enable the nested functions of the setlist creation)
def pull_random_song_by_conditions(df, number=1, **conditions):
    """
    :param df: Initial dataframe containing entire song catalogue information
    :param number: The number of songs requested (default value is 1)
    :param conditions: Key-value pairs where key is the column name and value is the condition.
                       Conditions can be a single value or a tuple for range/comparison (e.g., ('>', 2023)).
    :return: A random song that fits all applied criteria
    """
    filtered_df = df.copy()
    for column, condition in conditions.items():
        if isinstance(condition, tuple):
            operator, value = condition
            if operator == '>':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == '>=':
                filtered_df = filtered_df[filtered_df[column] >= value]
            elif operator == '<':
                filtered_df = filtered_df[filtered_df[column] < value]
            elif operator == '<=':
                filtered_df = filtered_df[filtered_df[column] <= value]
            elif operator == '!=':
                filtered_df = filtered_df[filtered_df[column] != value]
        else:
            filtered_df = filtered_df[filtered_df[column] == condition]
    if len(filtered_df) < number:
        raise ValueError(f"Not enough songs matching the criteria: {conditions}")

    return filtered_df.sample(n=number)


# Composite function for creating a setlist by pulling random songs that fit certain criteria
def create_cardio_sculpt_set(df):
    """
    :param df: Dataframe to pass to the random song function
    :return: A dataframe containing a setlist generated within Cardio Sculpt parameters
    """
    setlist = []
    added_song_titles = set()  # To track added songs by their unique titles

    # Determine which songs can bypass the year >= 2023 condition
    total_slots = 15  # Number of slots before any additional songs
    oldies = random.sample(range(total_slots), 3)  # Randomly pick 3 slots to allow to be up to 10 years old
    unrestricted_slot = random.choice(oldies)  # Randomly pick one slot to allow a song of any age

    def pull_unique_song(**conditions):
        """ Pull a song that hasn't been added to the setlist yet. """
        attempts = 0
        max_attempts = 10  # Max attempts to find a unique song
        while attempts < max_attempts:
            song = pull_random_song_by_conditions(df, number=1, **conditions)
            song_title = song['title'].values[0]  # Use 'title' as the unique identifier
            if song_title not in added_song_titles:
                added_song_titles.add(song_title)
                return song
            attempts += 1
        raise ValueError(f"Unable to find a unique song matching conditions: {conditions}")

    def pull_song_with_condition(index, **conditions):
        """ Uses the established 'free_slots' indices to allow older songs in the setlist """
        if index == unrestricted_slot:
            return pull_unique_song(**conditions)
        elif index in oldies:
            return pull_unique_song(year=('>=', nine_year_limit), **conditions)
        else:
            return pull_unique_song(year=('>=', one_year_limit), **conditions)

    try:
        # Song 1: OI
        setlist.append(pull_song_with_condition(0, purpose='OI'))

        # Song 2: LM
        setlist.append(pull_song_with_condition(1, purpose='LM'))

        # Song 3: M
        setlist.append(pull_song_with_condition(2, purpose='M'))

        # Song 4: MH
        setlist.append(pull_song_with_condition(3, purpose='MH'))

        # Songs 5-6: H
        setlist.extend(pull_song_with_condition(i, purpose='H') for i in range(4, 6))

        # Song 7: MH
        setlist.append(pull_song_with_condition(6, purpose='MH'))

        # Song 8-9: M
        setlist.extend(pull_song_with_condition(i, purpose='M') for i in range(7, 9))

        # Song 10: LM
        setlist.append(pull_song_with_condition(9, purpose='LM'))

        # Songs 11-14: At least one each of MU, MA, and MG in any order (could also be OPT for the one extra)
        purposes_11_13 = ['MU', 'MA', 'MG']
        random.shuffle(purposes_11_13)
        for i, purpose in enumerate(purposes_11_13, start=10):
            setlist.append(pull_song_with_condition(i, purpose=purpose))

        strength_purposes: list[str] = ['MU', 'MA', 'MG', 'OPT']
        purpose_14 = random.choice(strength_purposes)
        setlist.append(pull_song_with_condition(13, purpose=purpose_14))

        # Rule 15: SAE
        setlist.append(pull_song_with_condition(14, purpose='SAE'))

    except ValueError as e:
        print(f"Error: {e}")

    # Calculate total length
    total_length_seconds = sum(convert_length_to_seconds(song['length'].values[0]) for song in setlist)

    # Check if the total length is within the range 52:00 to 56:30 (3120 to 3390 seconds)
    min_length = 31200
    max_songs = 16

    # Add additional songs if the total length is too short
    while total_length_seconds < min_length and len(setlist) < max_songs:
        if total_length_seconds < min_length:
            # Try adding another 'M' song after Song 9
            try:
                additional_song = pull_unique_song(purpose='M')
                setlist.insert(7, additional_song)
                total_length_seconds += convert_length_to_seconds(additional_song['length'].values[0])
            except ValueError:
                # If no 'M' song is available, add a strength_purpose song after 14
                try:
                    additional_song = pull_unique_song(purpose=random.choice(strength_purposes))
                    setlist.insert(-1, additional_song)
                    total_length_seconds += convert_length_to_seconds(additional_song['length'].values[0])
                except ValueError:
                    print("Not enough songs to meet the total length requirement.")
                    break

    if len(setlist) > max_songs:
        setlist = setlist[:max_songs]
        total_length_seconds = sum(convert_length_to_seconds(song['length'].values[0]) for song in setlist)

    # Concatenate all parts of the setlist
    final_setlist = pd.concat(setlist).reset_index(drop=True)

    # Print the total length in MM:SS format
    total_length_mm_ss = convert_seconds_to_length(total_length_seconds)
    print(f"Total Length of Setlist: {total_length_mm_ss}")

    return final_setlist


if __name__ == '__main__':
    while True:
        cardio_sculpt_setlist = create_cardio_sculpt_set(jazzercise_catalogue)

        # Ask the user if they want to continue
        proceed = input('Would you like to continue? (y/n): ').strip().lower()

        if proceed == 'y':
            cardio_sculpt_setlist.to_csv('data/cardio_sculpt_generated_setlist.csv', index=False)
            print('Setlist has been saved to CSV.')
            break
        elif proceed == 'n':
            print('Generating a new setlist...')
        else:
            print('Invalid input. Please enter "y" or "n".')
