import csv
import rdflib
import re
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS

# Create a graph
g = rdflib.Graph()

# Define namespaces
schema = Namespace('http://schema.org/')
xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

# Parent-Child relationships
parent_orgs = {
    "Biennale De L'illustration De Bratislava : Grand Prix" : "Biennale De L'illustration De Bratislava",
    "Biennale De L'illustration De Bratislava : Plaques D'or" : "Biennale De L'illustration De Bratislava",
    "Biennale De L'illustration De Bratislava : Pommes D'or" : "Biennale De L'illustration De Bratislava",
    "Figures Futur : Prix Des Médiateurs" : "Figures Futur",
    "Figures Futur : Prix Du Jury" : "Figures Futur",
    "Figures Futur : Prix Du Public" : "Figures Futur",
    "Figures Futur : Prix Du Public Enfants" : "Figures Futur",
    "Les Pépites Du Salon De Montreuil : Pépite Bande Dessinée" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Bd/Manga" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De La Création Numérique" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De La Petite Enfance" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De L’Adaptation Cinéma D’Animation" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De L’Adaptation Cinéma D’Animation - Courts Et Moyens Métrages" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De L’Adaptation Cinéma D’Animation - Séries Télévisées" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite De L’Album" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Des Grands" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Des Moyens" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Des Petits" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Documentaire" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Documentaire/Livre D’Art" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Livre Audio/Histoires En Musique" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Livre D’Art" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Livre Ovni / Coup De Cœur De L’Équipe Du Salon" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Premier Album" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Roman 9-12 Ans" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Roman Ado Européen" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Du Roman Européen Pour Adolescents" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite D’Or" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Fiction Ados" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Fiction Junior" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Livre Illustré" : "Les Pépites Du Salon De Montreuil",
    "Les Pépites Du Salon De Montreuil : Pépite Roman" : "Les Pépites Du Salon De Montreuil",
    "Prix Bernard Versele : 1 Chouette" : "Prix Bernard Versele",
    "Prix Bernard Versele : 2 Chouettes" : "Prix Bernard Versele",
    "Prix Bernard Versele : 3 Chouettes" : "Prix Bernard Versele",
    "Prix Bernard Versele : 4 Chouettes" : "Prix Bernard Versele",
    "Prix Bernard Versele : 5 Chouettes" : "Prix Bernard Versele",
    "Prix Bologna Ragazzi: Arte Novita - Prix Arts Nouveauté" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Bologna Ragazzi Award Books & Seeds" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Bologna Ragazzi Award On Art - Architecture & Design" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Cinema - Categoria Speciale" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Comics - Early Reader" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Comics - Middle Grade" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Comics - Young Adult" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fiction" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fiction Award" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fiction Enfance (6-9 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fiction Jeunesse (10-16 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fiction Première Enfance (0-5 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Fotografia - Categoria Speciale" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Mention" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Mention Spéciale" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Mention Spéciale Fiction" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Mentions" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Mentions Spéciales" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: New Horizons" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: New Horizons Award" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: New Media Prize" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Non Fiction" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Non Fiction Award" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Non Fiction Enfance (6-9 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Non Fiction Jeunesse (10-16 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Non Fiction Première Enfance (0-5 Ans)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Opera Prima" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Poesia - Categoria Speciale" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Prix Non-Fiction" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Prix Nouveaux Horizons" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Prix Opera Prima (Première Œuvre)" : "Prix Bologna Ragazzi",
    "Prix Bologna Ragazzi: Prix Opéra Prima (Première Œuvre)" : "Prix Bologna Ragazzi",
    "Prix Bulles De Cristal : Catégorie Des 11-14 Ans" : "Prix Bulles De Cristal",
    "Prix Bulles De Cristal : Catégorie Des 15-18 Ans" : "Prix Bulles De Cristal",
    "Prix Cendres : Mention" : "Prix Cendres",
    "Prix Chronos Alzheimer" : "Prix Chronos",
    "Prix Chronos De Littérature" : "Prix Chronos",
    "Prix Chronos De Littérature : 4E - 3E" : "Prix Chronos",
    "Prix Chronos De Littérature : 4E – 3E" : "Prix Chronos",
    "Prix Chronos De Littérature : 6E - 5E" : "Prix Chronos",
    "Prix Chronos De Littérature : 6E – 5E" : "Prix Chronos",
    "Prix Chronos De Littérature : Ce1 - Ce2" : "Prix Chronos",
    "Prix Chronos De Littérature : Ce1 – Ce2" : "Prix Chronos",
    "Prix Chronos De Littérature : Cm1 - Cm2" : "Prix Chronos",
    "Prix Chronos De Littérature : Cm1 – Cm2" : "Prix Chronos",
    "Prix Chronos De Littérature : Lycéens, 20 Ans Et Plus" : "Prix Chronos",
    "Prix Chronos De Littérature : Maternelle – Cp" : "Prix Chronos",
    "Prix De La Pièce De Théâtre Contemporain Pour Le Jeune Public : 3Ème-2Nde" : "Prix De La Pièce De Théâtre Contemporain Pour Le Jeune Public",
    "Prix des libraires : Lauréat 2023 Essai Québec" : "Prix des libraires",
    "Prix des libraires : Lauréat 2023 Poésie Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 0-5 Ans Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 0-5 Ans Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 12-17 Ans Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 12-17 Ans Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 2023 Volet Adulte Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 2023 Volet Adulte Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 6-11 Ans Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats 6-11 Ans Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats Bd Jeunesse Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats Bd Jeunesse Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats Roman-Nouvelles-Récit 2023 Hors Québec" : "Prix des libraires",
    "Prix des libraires : Lauréats Roman-Nouvelles-Récit 2023 Québec" : "Prix des libraires",
    "Prix Du Roman Historique Jeunesse : 3ème-Seconde" : "Prix Du Roman Historique Jeunesse",
    "Prix Du Roman Historique Jeunesse : 5ème-4ème" : "Prix Du Roman Historique Jeunesse",
    "Prix Du Roman Historique Jeunesse : Cm2-6ème" : "Prix Du Roman Historique Jeunesse",
    "Prix Du Roman Historique Jeunesse : Lycée" : "Prix Du Roman Historique Jeunesse",
    "Prix Enfantaisie : Catégorie Album" : "Prix Enfantaisie",
    "Prix Enfantaisie : Catégorie Roman - Prix Farniente" : "Prix Enfantaisie",
    "Prix Farniente : Basket Jaune (13+)" : "Prix Farniente",
    "Prix Farniente : Basket Orange" : "Prix Farniente",
    "Prix Farniente : Basket Verte (15+)" : "Prix Farniente",
    "Prix Farniente : Chameau (15+)" : "Prix Farniente",
    "Prix Farniente : Deux Baskets" : "Prix Farniente",
    "Prix Farniente : Dromadaire (13+)" : "Prix Farniente",
    "Prix Farniente : Prix Evasion (15+)" : "Prix Farniente",
    "Prix Farniente : Prix Victor (13+)" : "Prix Farniente",
    "Prix Farniente : Sélection Jaune (13+)" : "Prix Farniente",
    "Prix Farniente : Sélection Verte (15+)" : "Prix Farniente",
    "Prix Farniente : Une Basket" : "Prix Farniente",
    "Prix Franco-Allemand Pour La Littérature De Jeunesse : Allemagne" : "Prix Franco-Allemand Pour La Littérature De Jeunesse",
    "Prix Franco-Allemand Pour La Littérature De Jeunesse : France" : "Prix Franco-Allemand Pour La Littérature De Jeunesse",
    "Prix Imaginales : Catégorie Jeunesse" : "Prix Imaginales",
    "Prix Imaginales : Catégorie Album" : "Prix Imaginales",
    "Prix Imaginales Des Collégiens" : "Prix Imaginales",
    "Prix Imaginales Des Ecoliers" : "Prix Imaginales",
    "Prix Imaginales Des Lycéens" : "Prix Imaginales",
    "Prix La Science Se Livre : Catégorie 4-8 Ans" : "Prix La Science Se Livre",
    "Prix La Science Se Livre : Catégorie 9-14 Ans" : "Prix La Science Se Livre",
    "Prix La Science Se Livre : Catégorie Adolescents 11-15 Ans" : "Prix La Science Se Livre",
    "Prix Libbylit (Mention Spéciale - Album-Roman)" : "Prix Libbylit",
    "Prix Libbylit (Mention Spéciale - Hors Catégorie)" : "Prix Libbylit",
    "Prix Libbylit (Mention Spéciale - Théâtre Jeunesse)" : "Prix Libbylit",
    "Prix Libbylit (Mention Spéciale Du Jury)" : "Prix Libbylit",
    "Prix Libbylit (Mention Spéciale)" : "Prix Libbylit",
    "Prix Libbylit (Ovni)" : "Prix Libbylit",
    "Prix Littéraire Hackmatack (Égalité!)" : "Prix Littéraire Hackmatack",
    "Prix Littéralouest : 10-11 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 4-5 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 4Ème-3Ème" : "Prix Littéralouest",
    "Prix Littéralouest : 5-6 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 6-7 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 6Ème-5Ème" : "Prix Littéralouest",
    "Prix Littéralouest : 7-8 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 8-9 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : 9-10 Ans" : "Prix Littéralouest",
    "Prix Littéralouest : Bd (Collège)" : "Prix Littéralouest",
    "Prix Littéralouest : Moins De 4 Ans" : "Prix Littéralouest",
    "Prix Livrentête : Albums" : "Prix Livrentête",
    "Prix Livrentête : Albums 3+" : "Prix Livrentête",
    "Prix Livrentête : Albums 5+" : "Prix Livrentête",
    "Prix Livrentête : Bandes Dessinées Juniors 12 Ans Et Plus" : "Prix Livrentête",
    "Prix Livrentête : Bd Enfants" : "Prix Livrentête",
    "Prix Livrentête : Bd Juniors" : "Prix Livrentête",
    "Prix Livrentête : Livres D’Images" : "Prix Livrentête",
    "Prix Livrentête : Premiers Romans" : "Prix Livrentête",
    "Prix Livrentête : Premières Bd" : "Prix Livrentête",
    "Prix Livrentête : Premières Lectures" : "Prix Livrentête",
    "Prix Livrentête : Romans Ados" : "Prix Livrentête",
    "Prix Livrentête : Romans Enfants" : "Prix Livrentête",
    "Prix Livrentête : Romans Juniors" : "Prix Livrentête",
    "Prix Livrentête : Sélection Albums À Partir De 3 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection Albums À Partir De 5 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection Bd À Partir De 10 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection Bd À Partir De 13 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection Premières Bd À Partir De 7 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection Premières Lectures À Partir De 7 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection À Partir De 12 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection À Partir De 15 Ans" : "Prix Livrentête",
    "Prix Livrentête : Sélection À Partir De 9 Ans" : "Prix Livrentête",
    "Prix Lu Et Partagé : Grand Prix De L'Album" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Extra-Ordinaire" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Jeune Talent" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Petite Enfance" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Roman Ado" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Roman Junior" : "Prix Lu Et Partagé",
    "Prix Lu Et Partagé : Prix Spécial Du Jury Roman" : "Prix Lu Et Partagé",
    "Prix Mangawa : Catégorie Seinen" : "Prix Mangawa",
    "Prix Mangawa : Catégorie Shojo" : "Prix Mangawa",
    "Prix Mangawa : Catégorie Shonen" : "Prix Mangawa",
    "Prix Petit Angle : Petit Angle Étranger" : "Prix Petit Angle",
    "Prix Petit Angle : Prix Spécial" : "Prix Petit Angle",
    "Prix Petit Angle : Prix Spécial Du Jury" : "Prix Petit Angle",
    "Prix Real : 11-14 Ans" : "Prix Real",
    "Prix Real : 15-18 Ans" : "Prix Real",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Album" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Coup De Cœur Jury Enfants" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Francophonie" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Mention Speciale" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Mention Spéciale" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Mention Spéciale Environnement" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Prix Spécial Poésie" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Saint-Exupéry - Valeurs Jeunesse : Roman" : "Prix Saint-Exupéry - Valeurs Jeunesse",
    "Prix Sorcières : Ados" : "Prix Sorcières",
    "Prix Sorcières : Albums" : "Prix Sorcières",
    "Prix Sorcières : Carrément Beau, Maxi" : "Prix Sorcières",
    "Prix Sorcières : Carrément Beau, Mini" : "Prix Sorcières",
    "Prix Sorcières : Carrément Passionnant, Maxi" : "Prix Sorcières",
    "Prix Sorcières : Carrément Passionnant, Mini" : "Prix Sorcières",
    "Prix Sorcières : Carrément Sorcières, Fiction" : "Prix Sorcières",
    "Prix Sorcières : Carrément Sorcières, Non Fiction" : "Prix Sorcières",
    "Prix Sorcières : Documentaire" : "Prix Sorcières",
    "Prix Sorcières : Documentaires" : "Prix Sorcières",
    "Prix Sorcières : Première Lecture" : "Prix Sorcières",
    "Prix Sorcières : Premières Lectures" : "Prix Sorcières",
    "Prix Sorcières : Roman Ados" : "Prix Sorcières",
    "Prix Sorcières : Romans 9-12 Ans" : "Prix Sorcières",
    "Prix Sorcières : Romans Adolescents" : "Prix Sorcières",
    "Prix Sorcières : Romans Jeunes" : "Prix Sorcières",
    "Prix Sorcières : Romans Juniors" : "Prix Sorcières",
    "Prix Sorcières : Tout-Petits" : "Prix Sorcières",
    "Prix Talents Cultura : Les Talents Bandes Dessinées 2021" : "Prix Talents Cultura",
    "Prix Talents Cultura : Les Talents Jeunesse 2021" : "Prix Talents Cultura",
    "Prix Talents Cultura : Les Talents Romans 2021" : "Prix Talents Cultura",
    "Prix Tatoulu : Tatou Blanc" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Bleu" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Jaune" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Noir" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Rose" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Rouge" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Vert" : "Prix Tatoulu",
    "Prix Tatoulu : Tatou Violet" : "Prix Tatoulu",
    "Prix Unicef De Littérature Jeunesse : Catégorie 0-5 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 0-6 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 13-15 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 13-18 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 3-5 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 6-8 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 8-11 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Prix Unicef De Littérature Jeunesse : Catégorie 9-12 Ans" : "Prix Unicef De Littérature Jeunesse",
    "Tam-Tam Du Livre De Jeunesse : Dlire/Canal Bd Catégorie Bande Dessinée" : "Tam-Tam Du Livre De Jeunesse",
    "Tam-Tam Du Livre De Jeunesse : Dlire/Canal Bd Catégorie Manga" : "Tam-Tam Du Livre De Jeunesse",
    "Tam-Tam Du Livre De Jeunesse : J'aime Lire" : "Tam-Tam Du Livre De Jeunesse",
    "Tam-Tam Du Livre De Jeunesse : Je Bouquine" : "Tam-Tam Du Livre De Jeunesse"
}

# Regular expression to match non-alphanumeric characters, with exceptions
pattern = re.compile(r'[^a-zA-Z0-9À-ÖØ-öø-ÿ]+')

# Read organizations from CSV file
with open('./awards.csv', 'r', encoding="utf-8") as f:
    reader = csv.reader(f)
    orgs = [row[0] for row in reader]

for org in orgs:
    # Replace sequences of non-alphanumeric characters with a single underscore
    org_name = pattern.sub('_', org)
    org_uri = URIRef(f'{schema}{org_name}')
    g.add((org_uri, RDF.type, schema.Organization))
    g.add((org_uri, schema.name, Literal(org, datatype=xsd.string)))

    # Check if org has parent organization
    if org in parent_orgs:
        parent_org = parent_orgs[org]
        parent_org_name = pattern.sub('_', parent_org)
        parent_org_uri = URIRef(f'{schema}{parent_org_name}')
        g.add((org_uri, schema.parentOrganization, parent_org_uri))
        g.add((parent_org_uri, schema.subOrganization, org_uri))

# Serialize the graph in Turtle format and write it to a file
with open('./awards_conversion.ttl', 'w', encoding="utf-8") as f:
    f.write(g.serialize(format='turtle'))
