# seulement 2 sources pour le moment, mais travailler avec 3 pour generaliser
constellation_age = [4,5,6]
bnf_age = [3,4,5,6]
lurelu_age = [3,4,5]

# idée 1: union de toutes les sources
# avantage: simple
# desavantage: source ont le meme poids, pas parametrable
res1 = set(constellation_age + bnf_age + lurelu_age)
print("res1", res1)

#idée 2: intersection sources
# données plus affinées que es2
res2 = set(constellation_age) & set(bnf_age) & set(lurelu_age)
print("res2", res2)

# idée3: intersection sources avec hierarchie
# intuitivement: qualite(constellation) > qualite(lurelu) > qualite bnf
res3 =  set(constellation_age) &  set(bnf_age + lurelu_age) if constellation_age else res1 
# equivalement a 
res33 = constellation_age if constellation_age else res1 
print("res3", res3)
print("res33" , res33)

# idée 3 paramétrable: choisir un golden source qui va decider
opt_constellation_str = "1. constellation"
opt_lurelu_str = "2. lurelu"
opt_bnf_str = "3. bnf"
optNoGoldenSource = "4. No Golden Source"
opt_constellation = "1"
opt_lurelu = "2"
opt_bnf = "3"
options = [opt_constellation, opt_bnf, opt_lurelu]
options_str = [opt_constellation_str, opt_lurelu_str, opt_bnf, optNoGoldenSource, ""]
message = 'Please select the ideal golden source: (default = constellation) ' + str(options_str) + '\n'
user_input = input(message)

res = []
if user_input in options:
    print('You selected:', user_input)
    if user_input == opt_constellation:
        res = constellation_age
    elif user_input == opt_lurelu:
        res = lurelu_age
    elif user_input == opt_bnf:
        res = bnf_age
    elif user_input == optNoGoldenSource:
        res = res1
    else:
        res = constellation_age
    print("res3param", res)

else:
    print('Invalid option selected')

# idee 4: sortir age qui a le plus de poids
# dictionnaire avec compteur
# on print ce qui est le plus utilisé
# desavantage: si un seul age est au max, le range d'age sera petit

from collections import defaultdict

dict_ages = defaultdict(int)

for age in constellation_age:
    dict_ages[age] += 1
for age in lurelu_age:
    dict_ages[age] += 1
for age in bnf_age:
    dict_ages[age] += 1

max_dict = max(dict_ages.values())
res4 = []
for key in dict_ages.keys():
    if dict_ages[key] == max_dict:
        res4.append(key)

print("res4", res4)


# idee 5
# idee 4, mais mettre dans resultat final si dans plusieurs sources (mais parametrable par utilisateur)
    # -> inclu seulement source 1 ou 2 dans dicionnaire
# ex: donne le range d'age qui sont au moins dans 2 sources differentes

# idee 6
# idee 4, mais on peut parametrer le poids de tel ou tel source
    # -> donne plus de poids à source 1 et 2 par rapport à 3
# ex: a chaque fois que constellation ou lurelu donne un age, on lui donne plus de poids dans le dictionnaire
# utile si bcp de sources