import wikipedia
from googletrans import Translator
import argparse
from prettytable import PrettyTable
import requests
from lxml import html


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("langs", help="Specify languages you want to compare delimated with"
                        "comas", type=str)
    parser.add_argument("title", help="specify the title you want to search for", type=str)
    args = parser.parse_args()

    return (args.langs.split(","), args.title)

def search_for_keywords(content, ln, keywords):
    keyword_hits = []
    translator = Translator()
    if (ln == 'pl'):
        for keyword in keywords:
            hits_nb = content.count(" {}".format(keyword))
            if hits_nb > 0:
                keyword_hits.append((keyword, hits_nb))
    else:
        translated_keywords = []
        try:
            with open('keywords_{}.txt'.format(ln), 'r') as f:
                translated_keywords = [keyword.strip() for keyword in f]
        except FileNotFoundError:
            translator = Translator()
            translated_keywords = translator.translate(keywords, dest=ln, src='pl')
            translated_keywords = [keyword.text.lower() for keyword in translated_keywords]
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

def main():
    (languages, title) = parse_arguments()
    f = open('keywords.txt', 'r')
    keywords = [keyword.strip() for keyword in f]
    f.close()

    wikipedia.set_lang('pl')
    url = wikipedia.page(title=title).url
    req = requests.get(url)
    assert req.status_code, 200
    webpage = html.fromstring(req.content)
    links = webpage.xpath('//a/@href')

    for ln in languages:
        content = ""
        wikipedia.set_lang(ln)
        if (ln == 'pl'):
            content = wikipedia.page(title=title).content.lower()
            keyword_hits = search_for_keywords(content, ln, keywords)
            print_result(keyword_hits, ln)
        else:
            foreign_title = ""
            phrase = "{}.wikipedia.org/wiki/".format(ln)
            for link in links:
                if phrase in link:
                    x = len("https://.wikipedia.org/wiki/") + len(ln)
                    foreign_title = link[x:None]
            content = wikipedia.page(title=foreign_title).content.lower()

        keyword_hits = search_for_keywords(content, ln, keywords)
        print_result(keyword_hits, ln)

if __name__== "__main__":
    main()
