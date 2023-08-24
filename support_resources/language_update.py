from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
from langdetect import detect, LangDetectException

g = Graph()

# Parsing the .ttl file
g.parse("./merged_output.ttl", format="turtle")

ns1 = Namespace("http://schema.org/")

allowed_languages = ['en']  # English
excluded_books = ['Rouge Matou', "L'arrache-mots", 'Les secrets de Faith Green', 'Hypallage (T. 1). Amour chrome',
                  'Thomas', 'Le grand spectacle', 'Les secrets de Faith Green', 'Happy birthday grand-mère', 
                  'Cancer ascendant Autruche', 'Lilly sous la mer', 'Sous le grand banian', 'Z comme Zinkoff', 
                  'Georgia, tous mes rêves chantent', 'Totem', 'Robinson Crusoe', 'Sous Terre', 'Mon bison', 
                  '10 petits insectes', 'Beyrouth-sur-Seine', 'Charlotte', 'Bjorn le Morphir', 'Mary tempête', 
                  'Pas touche à Charly !', 'RC 2722', '1,2,3 petits chats', 'JONAH (T. 1). LES SENTINELLES', 
                  'Horror Games (T. 1). Ne te retourne pas !', 'Hush ! Hush !', 'Sous le grand banian', 
                  "Et l'on chercha Tortue", 'Les Secrets de Faith Green', "Magic Charly (T. 1). L'apprenti", 
                  'Oh, Boy!', 'Christophe au grand cœur', 'Edmond et Amandine', 'Les Willoughby', 
                  'Le Petit Chaperon rouge de Jacob & Wilhelm Grimm', 'Mon bison', 'Macbeth de William Shakespeare', 
                  'Cache-cache cauchemars', 'Polly', 'Raymond rêve', 'Canines', 'Non !', 'Jardin secret',  
                  'Bjorn le Morphir', 'Cherche amis', 'Les Orphelins d’Abbey Road (T.1)', 'Nox (t.1). Ici-bas', 
                  'Traces', 'Rouge', 'Nox (T. 1). Ici-bas', 'Felix Têtedeveau', 'Apocalypsis. Cavalier Rouge : Edo',  
                  '20 pieds sous terre', 'Chat tricote', 'Mon chat Boudin', 'Chat rouge, chat bleu', 'Jefferson', 
                  'Longtemps', 'Sousbrouillard', 'Thomas, prince professionnel', 'Trash anxieuse', 'Mr. Loverman', 
                  'Thomas', 'Cher monsieur Donald Trump', 'Christophe au grand cœur', 'Fourchon', 'Léviathan T.1', 
                  'Léviathan T.1', 'Cabot-Caboche', 'Christophe au grand cœur', 'Des choses formidables', 
                  'Edmond et Amandine', 'Cabot-Caboche', 'Mr. Loverman', 'Pow Pow, t’es mort!', 'Nous', 'Cher connard']

for s,p,o in g.triples((None, RDF.type, ns1.Book)):
    # Get the name of the book
    name = g.value(s, ns1.name)
    if name and name.strip() and name not in excluded_books:  # Skip empty strings, strings that only contain whitespace, and names in the excluded list
        try:
            detected_language = detect(name)
            if detected_language in allowed_languages:
                #print(f"URI of the book: {s}, Name of the book: {name}, Detected Language: {detected_language}")

                # remove old inLanguage attribute if it exists
                old_language = g.value(s, ns1.inLanguage)
                if old_language is not None:
                    g.remove((s, ns1.inLanguage, old_language))

                # add new inLanguage attribute
                g.add((s, ns1.inLanguage, Literal('Anglais')))
        except LangDetectException:
            print(f"Could not detect language for book: {name}")
    else:
        print(f"Book '{name}' is in the excluded list.")

# Serialize the graph into a new .ttl file
g.serialize(destination='./merged_output.ttl', format='turtle')
