import pandas as pd
import numpy as np
from playsound import playsound
import os
from googletrans import Translator
from gtts import gTTS
import speech_recognition as sr
import wave
import pyaudio

IDF_MARCH = "1.wav"

EXIT = "exit.mp3"

GOOD_OR_BAD = "good_or_bad.mp3"

COUNTRY_ERROR = "country_error.mp3"

NAME_COUNTRY = "name_country.mp3"

OPENING = "opening.mp3"

OUTPUT_MP3 = "output.mp3"
NUM_OF_SENTENCE_TO_SAY = 4

PATH_TO_DATA = "20210407.csv"
ULTRA = 'ultra'
OWN_CONTINENT = "own_continent"
WORLD = "world"
TOTAL_DEATHS = "TotalDeaths"
DEATHS_M_POP = "Deaths/1M pop"
DEATHEVERY_X_PPL = "1 Deathevery X ppl"
CASEEVERY_X_PPL = "1 Caseevery X ppl"
M_POP = "Tests/1M pop"
TOTAL_TESTS = "TotalTests"
COUNTRY = 'Country,Other'
CONT = 'Continent'
TOTAL_CASES = 'TotalCases'
CASES_PER_MIL = 'Tot Cases/1M pop'

langs = {
    "South Africa": "af",
    "Arabic": "ar",
    "Bangladesh": "bn",
    "Bosnia": "bs",
    "Switzerland": 'fr',
    "Catalan": "ca",
    "Czech": "cs",
    "Welsh": "cy",
    "Denmark": "da",
    "Germany": "de",
    "Greece": "el",
    "English": "en",
    "UK": "en",
    "USA": "en",
    "Australia": "en",
    "New Zealand": "en",
    "Esperanto": "eo",
    "Spanish": "es",
    "Estonia": "et",
    "Finland": "fi",
    "France": "fr",
    "Gujarati": "gu",
    "India": "hi",
    "Croatia": "hr",
    "Hungary": "hu",
    "Armenia": "hy",
    "Indonesia": "id",
    "Iceland": "is",
    "Italy": "it",
    "Japan": "ja",
    "Javanese": "jw",
    "Cambodia": "km",
    "Kannada": "kn",
    "North Korea": "ko",
    "South Korea": "ko",
    "Latin": "la",
    "Latvia": "lv",
    "Macedonia": "mk",
    "Malayalam": "ml",
    "Marathi": "mr",
    "Myanmar": "my",
    "Nepal": "ne",
    "Netherlands": "nl",
    "Norway": "no",
    "Poland": "pl",
    "Brazil": "pt",
    "Portugal": "pt",
    "Romania": "ro",
    "Russia": "ru",
    "Israel": "en",
    "Sri Lanka": "si",
    "Slovakia": "sk",
    "Albania": "sq",
    "Serbia": "sr",
    "Sundanese": "su",
    "Sweden": "sv",
    "Tanzania": "sw",
    "Tamil": "ta",
    "Telugu": "te",
    "Thailand": "th",
    "Philippines": "tl",
    "Turkey": "tr",
    "Ukraine": "uk",
    "Pakistan": "ur",
    "Vietnam": "vi",
    "China": "zh-CN",
    "Taiwan": "zh-CN",
}

synom = {'united states': "USA", 'united states of america': "USA", "england": "UK", "britain": "UK",
         "united kingdom": "UK",
         "united arab emirates": 'uae', "usa": 'usa', 'uk': 'k'}
spanish = "Argentina,Bolivia,Chile,Colombia,Costa Rica,Cuba,Dominican Republic,Ecuador,El Salvador,Guatemala,Honduras,Mexico,Nicaragua,Panama,Paraguay,Peru,Puerto Rico,Uruguay,Venezuela Spain"
arabic = "Palestine,Algeria,Bahrain,Chad,Comoros,Djibouti,Egypt,Iraq,Jordan,Kuwait,Lebanon,Libya,Mauritania,Morocco,Oman,Qatar,Saudi Arabia,Somalia,Sudan,Syria,Tunisia,UAE,Yemen"
spanish = spanish.split(",")
arabic = arabic.split(",")
for lang in spanish:
    langs[lang] = 'es'
for lang in arabic:
    langs[lang] = 'ar'


def get_parameters(df, country, parameter, ascending, supremom):
    """
    Creates a dictionary of statistics which can be presented as good or bad
    """
    ultras = ['usa', 'uk', 'france', 'germany', "canada", "uae", 'russia']
    # remove junk
    df = df[~df[COUNTRY].isin(["Total:", "Total: ", "Asia", "South America", "North America", " Total:", "Europe"])]
    cases_dict = {}
    county_row = df[df[COUNTRY] == country]
    # compare the country to the entire world
    sorted_table = df.sort_values(parameter, ascending=ascending).reset_index(drop=True)
    if sorted_table.index[sorted_table[COUNTRY] == country][0] < supremom[0]:
        cases_dict[WORLD] = sorted_table.index[sorted_table[COUNTRY] == country][0]
    # compare the country to its continent
    sorted_table = df[df[CONT] == county_row[CONT].values[0]].sort_values(parameter, ascending=ascending).reset_index(
        drop=True)
    if sorted_table.index[sorted_table[COUNTRY] == country][0] < supremom[1]:
        cases_dict[OWN_CONTINENT] = sorted_table.index[sorted_table[COUNTRY] == country][0]
    # finds a continent which makes the country looks good/ bad
    conti = list(set(df[CONT]) - set(county_row[CONT]))
    np.random.shuffle(conti)
    for cont in conti:
        sorted_table = df[df[CONT] == cont].append(county_row).sort_values(parameter, ascending=ascending).reset_index(
            drop=True)
        if sorted_table.index[sorted_table[COUNTRY] == country] < sorted_table.shape[0] / 2:
            cases_dict[CONT] = (cont, sorted_table.index[sorted_table[COUNTRY] == country].values[0])
            break
    np.random.shuffle(ultras)
    # finds a rich country which country did better than it.
    for ult in ultras:
        if df[df[COUNTRY] == ult][parameter].values[0] > county_row[parameter].values[0]:
            cases_dict[ULTRA] = ult
            break
    return cases_dict


# printer functions
def print_good_tot(country, res: dict, continent, cases, good=True):
    sentence_list = []
    more_or_less = "less" if good else "more"
    least_or_highest = "least" if good else "highest"
    for key, val in res.items():
        if key == WORLD:
            sentence_list.append(
                f"{country} is the {val + 1} country with the {least_or_highest} amount of corona {cases} in the whole world!\n")
        elif key == OWN_CONTINENT:
            sentence_list.append(
                f"In {continent}, {country} is the {val + 1} country with the {least_or_highest} amount of corona {cases}!\n")
        elif key == CONT:
            if val[1] == 0:
                sentence_list.append(f"{country} had {more_or_less} Covid-19 than whole countries of {val[0]}!")
            else:
                sentence_list.append(f"{country} had {more_or_less} {cases} than most of {val[0]}.")
        elif key == ULTRA and good:
            sentence_list.append(f"{country} had {more_or_less} {cases} than the great and powerful  {val}.")
    return sentence_list


def print_good_tests(country, res: dict, continent, tests, good=True):
    sentence_list = []
    more_or_less = "less" if not good else "more"
    least_or_highest = "least" if not good else "highest"
    for key, val in res.items():
        if key == WORLD:
            sentence_list.append(
                f"{country} is the {val + 1}  country with the {least_or_highest} amount of {tests} in the whole world!")
        elif key == OWN_CONTINENT:
            sentence_list.append(
                f"In whole of {continent}, {country} is the {val + 1} country with the {least_or_highest}"
                f" amount of corona {tests}!")
        elif key == CONT:
            if val[1] == 0:
                sentence_list.append(
                    f"{country} had {more_or_less} Covid-19 {tests} than whole countries of  {val[0]}!")
            else:
                sentence_list.append(f"{country} had {more_or_less} {tests} than most of {val[0]}.")
        elif key == ULTRA and good:
            sentence_list.append(f"{country} had {more_or_less} {tests} than the great and powerful  {val}.")
    return sentence_list


def print_good_x(country, res: dict, continent, amount, parameter, good=True):
    sentence = ""
    lowest_or_hishest = "lowest" if good else "highest"
    more_or_less = "less" if good else "more"
    if len(res.values()):
        sentence += f"{country} have 1 {parameter} for {amount} people, Which is:\n"
    for key, val in res.items():
        if key == WORLD:
            sentence += f"the {val + 1} most {lowest_or_hishest} in the whole world!\n"
        elif key == OWN_CONTINENT:
            sentence += f"the {val + 1} most {lowest_or_hishest} in {continent}.\n"
        elif key == CONT:
            if val[1] == 0:
                sentence += f"{more_or_less} than whole {val[0]}!\n"
            else:
                sentence += f"{more_or_less} than most of {val[0]}.\n"
        elif key == ULTRA and good:
            sentence += f"{more_or_less} than the great and powerful  {val}."
    return sentence


def get_data(df, country, good=True):
    sentences = []
    bool_list = [True, False] if good else [False, True]
    continent = df[df[COUNTRY] == country][CONT].values[0]
    tot_cases = get_parameters(df, country, TOTAL_CASES, bool_list[0], [20, 10])
    sentences += print_good_tot(country, tot_cases, continent, "cases", good)
    case_per = get_parameters(df, country, CASES_PER_MIL, bool_list[0], [20, 10])
    sentences += print_good_tot(country, case_per, continent, "cases per million", good)
    tot_test = get_parameters(df, country, TOTAL_TESTS, bool_list[1], [20, 10])
    sentences += print_good_tests(country, tot_test, continent, "tests", good)
    test_per = get_parameters(df, country, M_POP, bool_list[1], [20, 10])
    sentences += print_good_tests(country, test_per, continent, "tests per million", good)
    case_x_ppl = get_parameters(df, country, CASEEVERY_X_PPL, bool_list[1], [20, 10])
    sentences.append(
        print_good_x(country, case_x_ppl, continent, df[df[COUNTRY] == country][CASEEVERY_X_PPL].values[0], "cases",
                     good))
    death_x_people = get_parameters(df, country, DEATHEVERY_X_PPL, bool_list[1], [30, 20])
    sentences.append(
        print_good_x(country, death_x_people, continent, df[df[COUNTRY] == country][DEATHEVERY_X_PPL].values[0],
                     "death",
                     good))
    death_per = get_parameters(df, country, DEATHS_M_POP, bool_list[0], [30, 20])
    sentences += print_good_tot(country, death_per, continent, "deaths per million", good)
    tot_death = get_parameters(df, country, TOTAL_DEATHS, bool_list[0], [30, 20])
    sentences += print_good_tot(country, tot_death, continent, "deaths", good)
    return sentences


def get_country_name(df):
    no_country = True
    country = ""
    r = sr.Recognizer()
    mic = sr.Microphone()
    while no_country:
        playsound(NAME_COUNTRY)
        with mic as source:
            audio = r.listen(source)
        country = r.recognize_google(audio).lower()
        if country in synom.keys():
            country = synom[country]
        if country not in df[COUNTRY].tolist():
            random_country = df[COUNTRY].tolist()[np.random.randint(0, len(df[COUNTRY].tolist()) - 1)]
            play_n_delete(False, 'en', f"{country} is not available, try other country, for example - {random_country}")
            print(f"{country} is not available, try other country, for example - {random_country}")
        else:
            no_country = False
    return country.lower()


def get_good_or_bad(country):
    print(f"Do you want to present {country} in a good way or bad way?")
    good_or_bad = ""
    r = sr.Recognizer()
    mic = sr.Microphone()
    play_n_delete(False, 'en', f"Do you want to present {country} in a good way or bad way?", block=False)
    while good_or_bad not in ["good", "bad"]:
        with mic as source:
            audio = r.listen(source)
        good_or_bad = r.recognize_google(audio).lower()
        if "way" in good_or_bad:
            good_or_bad = good_or_bad.replace(" way", "")
        if good_or_bad not in ["good", "bad"]:
            playsound("good_bad_error.mp3")
    return good_or_bad


def play_background(good_or_bad, israel = False):
    folder = "good" if good_or_bad else "bad"
    files = os.listdir(f"{folder}_sounds")
    file = files[np.random.randint(0, len(files) -1)]
    if israel and good_or_bad:
        file = IDF_MARCH
    wf = wave.open(f"{folder}_sounds/{file}", 'rb')
    p = pyaudio.PyAudio()

    def callback(in_data, frame_count, time_info, status):
        data = wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True,
                    stream_callback=callback)
    stream.start_stream()
    return wf, stream, p


def stop_music(wf, stream, p):
    # stop stream
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio
    p.terminate()


def speak(sentences, country, good_or_bad):
    language = langs[country] if country  in langs.keys() else langs[list(langs.keys())[np.random.randint(0, len(langs.keys()))]]
    translate = Translator()
    wf, stream, p = play_background(good_or_bad, country == "Israel")
    for i in sentences:
        trans_sen = translate.translate(text=i, src='en', dest=language)
        print(i)
        play_n_delete(good_or_bad, language, trans_sen.text)
    stop_music(wf, stream, p)


def play_n_delete(slow, language, text, block=True, delete=True):
    output = gTTS(text=text, lang=language, slow=slow)
    output.save(OUTPUT_MP3)
    playsound(OUTPUT_MP3,block)
    if delete:
        os.remove(OUTPUT_MP3)


def main(df):
    country = ""
    while country not in df[COUNTRY].tolist():
        country = get_country_name(df)
        if country == "exit": exit(0)
        if country not in df[COUNTRY].tolist():
            country = country.capitalize()
        else:
            print("enter 'exit' to quit")
            continue
        if country not in df[COUNTRY].tolist():
            print(f"{country} is not available, try other country, for example - Turkey")
    good_or_bad = get_good_or_bad(country)
    play_n_delete(False, 'en', f"\n Here are some {good_or_bad} facts about how {country} managed the covid-19 pandemic:")
    print(f"\n Here are some {good_or_bad} facts about how {country} managed the covid-19 pandemic:")
    sentences = get_data(df, country, True if good_or_bad == 'good' else False)
    if len(sentences) > NUM_OF_SENTENCE_TO_SAY:
        sentences = [sentences[i] for i in np.random.randint(0, len(sentences) - 1, NUM_OF_SENTENCE_TO_SAY)]
    speak(sentences, country, True if good_or_bad == "good" else False)


def to_exit():
    r = sr.Recognizer()
    mic = sr.Microphone()
    print("\nSay exit to quit or anything else to start again\n")
    playsound(EXIT)
    with mic as source:
        audio = r.listen(source)
    exit = r.recognize_google(audio).lower()
    return exit == 'exit'


if __name__ == '__main__':
    df = pd.read_csv(PATH_TO_DATA)
    df = df[~df['Continent'].isin(['Africa', 'Australia/Oceania', '-1', 'All'])]
    df[COUNTRY] = df[COUNTRY].str.lower()
    playsound(OPENING)
    print("\nWelcome to  - 'Hear what you want to hear'\n")
    first = True
    while True:
        main(df)
        if to_exit():
            exit(0)
        first = False
