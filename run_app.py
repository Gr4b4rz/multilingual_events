import wikipedia
from googletrans import Translator
import argparse
from prettytable import PrettyTable
import requests
from lxml import html
from es_connection import ESWrapper
from nltk import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
import nltk


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("langs", help="Specify languages you want to compare delimated with"
                        "comas", type=str)
    parser.add_argument(
        "title", help="specify the title you want to search for", type=str)
    args = parser.parse_args()

    return (args.langs.split(","), args.title)


def get_full_english_ln_form(ln):
    full_form = ""
    if (ln == 'en'):
        full_form = "english"
    elif (ln == 'de'):
        full_form = "german"
    elif (ln == 'fr'):
        full_form = "french"
    elif (ln == 'it'):
        full_form = "italian"
    elif (ln == 'ru'):
        full_form = "russian"
    elif (ln == 'es'):
        full_form = "spanish"
    elif (ln == 'pt'):
        full_form = "portuguese"
    elif (ln == 'nl'):
        full_form = "norwegian"

    return full_form


def search_for_keywords(content, ln, keywords):
    keyword_hits = []
    translator = Translator()
    stemmer = None
    if (ln == 'pl'):
        f_pl = open('keywords_pl.txt', 'r')
        keywords_pl = [keyword.strip() for keyword in f_pl]
        f_pl.close()
        for keyword in keywords_pl:
            hits_nb = content.count(" {}".format(keyword))
            if hits_nb > 0:
                keyword_hits.append((keyword, hits_nb))
    else:
        translated_keywords = []
        stemmer = SnowballStemmer(
            get_full_english_ln_form(ln), ignore_stopwords=True)
        try:
            with open('keywords_{}.txt'.format(ln), 'r') as f:
                translated_keywords = [keyword.strip() for keyword in f]
        except FileNotFoundError:
            translator = Translator()
            translated_keywords = translator.translate(
                keywords, dest=ln, src='pl')
            translated_keywords = [stemmer.stem(keyword.text.lower()) if keyword.text.count(' ') > 0
                                   else keyword.text.lower() for keyword in translated_keywords]
            translated_keywords = list(dict.fromkeys(translated_keywords))

            print("Creating keywords_{}.txt file".format(ln))
            fw = open("keywords_{}.txt".format(ln), "w+")
            for item in translated_keywords:
                fw.write("%s\n" % item)
            fw.close()

        for keyword in translated_keywords:
            hits_nb = content.count(" {}".format(keyword))
            if hits_nb > 0:
                keyword_hits.append((keyword, hits_nb))

    return keyword_hits


def print_result(keyword_hits, ln):
    print("*** {} ***".format(ln))
    table = PrettyTable(['keyword', 'hits'])
    for keyword in keyword_hits:
        table.add_row([keyword[0], keyword[1]])
    print(table)


def create_ln_dict(keyword_hits, ctx_length, ln):
    number_of_hit_keywords = len(keyword_hits)
    number_of_total_hits = 0
    for keyword in keyword_hits:
        number_of_total_hits += keyword[1]

    ln_dict = {"language": ln, "content_length": ctx_length,
               "various_keyword_hit": number_of_hit_keywords,
               "total_keyword_hits": number_of_total_hits, "keywords": dict(keyword_hits)}
    return ln_dict


def write_to_db(es, es_document):
    es.index(index="processed-data", body=es_document)


def main():
    nltk.download('stopwords')
    (languages, title) = parse_arguments()
    f = open('keywords.txt', 'r')
    keywords = [keyword.strip() for keyword in f]
    f.close()
    es_wrapper = ESWrapper()
    es = es_wrapper.connect_elasticsearch(host='localhost', port=9200)

    wikipedia.set_lang('pl')
    url = wikipedia.page(title=title).url
    req = requests.get(url)
    assert req.status_code, 200
    webpage = html.fromstring(req.content)
    links = webpage.xpath('//a/@href')
    es_document = {'title': title, 'keywords_info': []}

    for ln in languages:
        content = ""
        wikipedia.set_lang(ln)
        keyword_hits = None
        if (ln == 'pl'):
            content = wikipedia.page(title=title).content.lower()
            keyword_hits = search_for_keywords(content, ln, keywords)
        else:
            foreign_title = ""
            phrase = "{}.wikipedia.org/wiki/".format(ln)
            for link in links:
                if phrase in link:
                    x = len("https://.wikipedia.org/wiki/") + len(ln)
                    foreign_title = link[x:None]
            try:
                content = wikipedia.page(title=foreign_title).content.lower()
                keyword_hits = search_for_keywords(content, ln, keywords)
            except:
                continue

        print_result(keyword_hits, ln)
        ln_dict = create_ln_dict(keyword_hits, len(content), ln)
        es_document['keywords_info'].append(ln_dict)

    write_to_db(es, es_document)


if __name__ == "__main__":
    main()
