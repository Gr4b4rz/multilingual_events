import wikipedia
from googletrans import Translator
import wikiquote


def main():
    wikipedia
    wikipedia.set_lang("de")
    sentence = wikipedia.summary("facebook", sentences=1)
    print(sentence)
    translator = Translator()
    print(translator.translate(sentence, dest='pl').text)

    # wikiquote
    print(wikiquote.supported_languages())
    grunwald_pl = wikiquote.search('Grunwald', lang='pl')
    grunwald_en = wikiquote.search('Grunwald', lang='en')
    pl_quotes = wikiquote.quotes(grunwald_pl[0], max_quotes=2, lang='pl')
    en_quotes = wikiquote.quotes(grunwald_en[0], max_quotes=2, lang='en')

    print(pl_quotes)
    print(en_quotes)
if __name__== "__main__":
    main()
