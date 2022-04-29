import combine_dataframe
file = open('../data/plists_categories.txt')
cats = file.read()

cats = cats.split(', ')

for j in [i for i in cats]:
    t_df=combine_dataframe.features_of_playlist(j)