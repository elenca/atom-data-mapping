#!/usr/bin/env python
"""Summary
"""
# coding: utf-8

### TODO:
# add filename to digitalobjectpath
# 


import pandas as pd
import numpy as np
import random
import hashlib


def cast_value(value):
    return str(value)

def split_it(val):
    if str(val) == 'NaN':
        return val
    else: 
        return str(val. split('.')[0])

# function to split a value in a column
# in this case to extract the value for the level "Serie" from 'THEMEN NAME (Stufe Kollektion)'
def split_column(value, number):
    if str(value) == 'NaN':
        return value
    else: 
        return str(value. split('/')[number])

# function to create a hash
def set_hash(value):
    if str(value) == 'unbekannt':
        # set a random value
        u = random.randint(1000,9999)
        return '0' + str(u)
    else: 
        return int(hashlib.sha256(value.encode('utf-8')).hexdigest(), 16) % 10**5

# function to set gender
def set_gender(value):
    if str(value) == 'unbekannt':
        return "ohne Geschlechtsangabe"
    elif str(value) == 'm (♂)':
        return "männlich"
    elif str(value) == 'w (♀)':
        return "weiblich"
    elif str(value) == 'NaN':
        return value

# function to set the age
def set_age(value):
    if str(value) == 'keine Angaben':
        return "keine Angaben (Alter)"
    else:
        return value + " Jahre (Alter)"

# function to set the school class
def set_class(value):
    if value is not np.nan:
        return str(value) + " (Schulklasse)"
    else:
        return value


def main():
    """Summary"""

    path_to_file = "D:/mastranelena/Desktop/Pestalozzianum/Jupyter_Notebook/Medadaten_Dump_20190325.csv"
    data = pd.read_csv(path_to_file, encoding='utf-8', index_col=False)

### data preparation ###

    # merge title column with alternate title    
    data['Titel'].loc[data['Alternativer Titel'].notnull() == True] = data['Titel'] + "/[" + data['Alternativer Titel'] + "]"
    data['Titel'].loc[data['Titel'].notnull() == False] = "[" + data['Alternativer Titel'] + "]"

    # rename title columns
    data.rename(columns={'THEMEN NAME (Stufe Kollektion)': 'Path', 'Titel Teilserie': 'Teilserie', 'Titel Akte': 'Akte', 'Titel': 'Objekt'}, inplace=True)

    # rename scopeAndContent columns
    data.rename(columns={'BESCHREIBUNG (Stufe Kollektion)': 'scope_Serie', 'Merkmale Teilserie': 'scope_Teilserie', 'Merkmale der Akte': 'scope_Akte', 'Beschreibung': 'scope_Objekt'}, inplace=True)

    # create column for level "Bestand"
    data['Bestand'] = data['Path'].apply(split_column, number=(0))

    # create column for level "Teilbestand"
    data['Teilbestand'] = data['Path'].apply(split_column, number=(1))

    # create column for level "Serie"
    data['Serie'] = data['Path'].apply(split_column, number=(2))

    ### Identifier
    # create column for identifier
    data['identifier'] = data['Original Dateiname / Signatur'].replace({r'(.*)(.tif|.tiff|.jpg|.pdf)' : r'\1'}, regex=True)

    ### RadGeneralMaterialDesignation
    data['radGeneralMaterialDesignation'] = "Kinderzeichnung"

    ### PublicationStatus
    data['publicationStatus'] = data['Portal Publikation'].str.replace('NEIN', 'Entwurf')

    ### AlternativeIdentifiers
    data['alternativeIdentifiers'] = data['Ressourcen-ID(s)']
    data['alternativeIdentifiers'].loc[data['Kartei Heller'].notnull() == True] = data['alternativeIdentifiers'].astype(str) + "|" + data['Kartei Heller'].astype(str).replace({r'(.*)(.0)' : r'\1'}, regex=True)
    data['alternativeIdentifiers'].loc[data['Kartei Weidmann'].notnull() == True] = data['alternativeIdentifiers'].astype(str) + "|" + data['Kartei Weidmann'].astype(str).replace({r'(.*)(.0)' : r'\1'}, regex=True)

    data['alternativeIdentifierLabels'] = data['alternativeIdentifierLabels'].loc[data['Ressourcen-ID(s)'].notnull() == True] = "Ressourcen-ID"
    data['alternativeIdentifierLabels'].loc[data['Kartei Heller'].notnull() == True] = data['alternativeIdentifierLabels'] + "|" + "Kartei Heller"
    data['alternativeIdentifierLabels'].loc[data['Kartei Weidmann'].notnull() == True] = data['alternativeIdentifierLabels'] + "|" + "Kartei Weidmann"

    ### DigitalObjectPath
    data['digitalObjectPath'] = data['Path']
    data['digitalObjectPath'].loc[data['Teilserie'].notnull() == True] = data['digitalObjectPath'] + "/" + data['Teilserie']
    data['digitalObjectPath'].loc[data['Akte'].notnull() == True] = data['digitalObjectPath'] + "/" + data['Akte']
    data['digitalObjectP'] = data['digitalObjectPath']

    ### add identifier
    data['digitalObjectPath'].loc[data['identifier'].notnull() == True] = data['digitalObjectPath'] + "/" + data['identifier']

    ### HierarchyPath
    data['hierarchyPath'] = "0_" + data['Bestand']
    data['hierarchyPath'] = data['hierarchyPath'] + "/1_" + data['Teilbestand']
    data['hierarchyPathTeilbestand'] = data['hierarchyPath']

    data['hierarchyPath'] = data['hierarchyPath'] + "/2_" + data['Serie']
    data['hierarchyPathSerie'] = data['hierarchyPath']

    data['hierarchyPath'].loc[data['Teilserie'].notnull() == True] = data['hierarchyPath'] + "/3_" + data['Teilserie']
    data['hierarchyPathTeilserie'] = data['hierarchyPath']

    data['hierarchyPath'].loc[data['Akte'].notnull() == True] = data['hierarchyPath'] + "/4_" + data['Akte']
    data['hierarchyPathAkte'] = data['hierarchyPath']

    data = data.sort_values(by = ['digitalObjectPath'])

    ### LevelOfDescription
    data['lod'] = "Objekt"

    ### Author
    # create new field "author_id"
    # set hash for author
    data['author_id'] = data['Urheber (Name, Vorname)'].apply(set_hash)

    # create new field "gender"
    # create new field "author" 
    # merge gender with hash for author
    data['gender'] = data['Geschlecht'].apply(set_gender)
    data['author'] = data['gender'] + "-" + data['author_id'].apply(cast_value)


    data['eventTypes'] = "Herstellung"
    data['eventActors'] = data['author']
    print(data['author'])


    # Create field for "eventDescription" 
    # add values for "Alter" and "Schulklasse"
    data['Alter'] = data['Alter'].apply(set_age)
    data['Schulklasse'] = data['Schulklasse'].apply(set_class)
    data['eventDescriptions'] = data['Alter'] + ", " + data['Schulklasse']

    # Set eventStartDates, eventEndDates and eventDates
    data['eventStartDates'] = data[['Zeitraum von', 'Datierung']].apply(lambda x: x['Datierung'] if x['Datierung'] is not np.nan else x['Zeitraum von'], axis=1).replace({r'(.*)(\d{4})(.*)' : r'\2'}, regex=True)
    data['eventEndDates'] = data[['Zeitraum bis', 'Datierung']].apply(lambda x: x['Datierung'] if x['Datierung'] is not np.nan else x['Zeitraum bis'], axis=1).replace({r'(.*)(\d{4})(.*)' : r'\2'}, regex=True)
    data['eventDates'] = data['Datierung'].replace({r'(.*)(\d{4})(.*)' : r'\2'}, regex=True)

    ### Create eventPlaces ###
    data['eventPlaces'] = data['Ort']
    data['eventPlaces'].loc[data['Kanton'].notnull() == True] = data['eventPlaces'] + ", " + data['Kanton']
    data['eventPlaces'].loc[data['Region'].notnull() == True] = data['eventPlaces'] + ", " + data['Region']
    data['eventPlaces'].loc[data['Land'].notnull() == True] = data['eventPlaces'] + ", " + data['Land']


    ### Create subject ###
    data['subjectAccessPoints'] = data['Alter']
    data['subjectAccessPoints'] = data['subjectAccessPoints'] + "|" + data['gender']


    ### Create subjectAccessPoints ###
    data['Schlagworte'] = data['Schlagworte'].str.replace(', ', '|')
    data['subjectAccessPoints'] = data['subjectAccessPoints'] + "|" + data['Schlagworte']


    ### GenreAccessPoints (Technik) ###
    data['Technik'] = data['Technik'].str.replace(', ', '|')
    data['genreAccessPoints'] = data['Technik']

    ### ExtentAndMedium ###
    data['extentAndMedium'] = "Technik: " + data['Technik']

    ### add values from field Trägermaterial
    data['Trägermaterial'] = data['Trägermaterial'].str.replace(', ', '|')
    data['extentAndMedium'].loc[data['Trägermaterial'].notnull() == True] = data['extentAndMedium'] + "| Trägermaterial: " + data['Trägermaterial']

    # add values from fields "Blattmasse (H) in cm" and "Blattmasse (B) in cm" and  "Masse (T) in cm"
    # if not null add to extentAndMedium
    data['extent'] = data['Blattmasse (H) in cm']
    data['extent'].loc[data['Blattmasse (B) in cm'].notnull() == True] = data['extent'] + " x " + data['Blattmasse (B) in cm'].astype(str)
    data['extent'].loc[data['Masse (T) in cm'].notnull() == True] = data['extent'] + " x " + data['Masse (T) in cm'].astype(str)
    data['extent'] = data['extent'] + " cm"

    data['extentAndMedium'].loc[data['extent'].notnull() == True] = data['extentAndMedium'] + "| Masse: " + data['extent']


    ### Tags ###
    data['scope_Objekt'].loc[data['Tag(s)'].notnull() == True] = data['scope_Objekt'] + "| Tags: " + data['Tag(s)']

    ### NameAccessPoints ###
    data['nameAccessPoints'] = data['Kanon'] + " (Kanon)"

    ### Lehrperson ###
    data['teacher'] = data['Lehrperson (Name, Vorname)']
    data['teacher'].loc[data['NORM Lehrperson'].notnull() == True] = data['NORM Lehrperson']
    data['nameAccessPoints'].loc[data['teacher'].notnull() == True] = data['nameAccessPoints'] + "|" + data['teacher'] + " (Lehrperson)"

    ### Schulhaus ###
    data['school'] = data['Schulhaus']
    data['school'].loc[data['NORM SHaus'].notnull() == True] = data['NORM SHaus']
    data['nameAccessPoints'].loc[data['school'].notnull() == True] = data['nameAccessPoints'] + "|" + data['school'] + " (Schulhaus)"

    ### Körperschaft/Wettbewerb ###
    data['nameAccessPoints'].loc[data['NORM Körperschaft'].notnull() == True] = data['nameAccessPoints'] + "|" + data['NORM Körperschaft'] + " (Wettbewerb)"

    ### Prämierung ###
    data['nameAccessPoints'].loc[data['Preis'].notnull() == True] = data['nameAccessPoints'] + "|" + data['Preis'] + " (Prämierung)"

    ### Ort ###
    data['placeAccessPoints'] = data['eventPlaces']

    #### Count occurrences
    data['count'] = data['hierarchyPath'].value_counts()
    #data['countTeilbestand'] = data['hierarchyPathTeilbestand'].value_counts()
    #data['countSerie'] = data['hierarchyPathSerie'].value_counts()
    #data['countTeilserie'] = data['hierarchyPathTeilserie'].value_counts()
    #data['countAkte'] = data['hierarchyPathAkte'].value_counts()
    print(data['count'])

### end : data preparation ###


### levels of description ###

    # extract levels of description
    duplicates = data[data.duplicated(['Serie', 'Teilserie', 'Akte'])]

    data_index = data.index.tolist()
    duplicates_index = duplicates.index.tolist()

    data_i = pd.Index(data_index)

    duplicates_i = pd.Index(duplicates_index)

    matches = data_i.difference(duplicates_i)

    # create dataframe containing the extracted levels of description
    df_sub = data.iloc[matches]

    # function to define the level 
    def set_level(value, level):
        return level if not pd.isnull(value) else value

    # function to set the value for a column
    def set_value(value):
        return value if not pd.isnull(value) else value

    # create a dataframe for the level "Serie" and append it to the dataframe "df_lod"
    # set the levelOfDescription, title and scopeAndContent
    df_sub['lod'] = df_sub['Serie'].apply(set_level, level=('1Serie'))
    df_serie = df_sub.loc[df_sub['lod'] == '1Serie']
    df_serie['title'] = df_serie['Serie'].apply(set_value)
    df_serie['scopeAndContent'] = df_serie['scope_Serie'].apply(set_value)
    df_serie['digitalObjectPath'] = df_serie['digitalObjectP'].apply(set_value)
    df_serie['hierarchyPath'] = df_serie['hierarchyPath'].apply(set_value)
    df_serie['extentAndMedium'] = df_serie['count'].apply(set_value)

    # set the eventStartDates, eventEndDates and eventDates
    df_serie['eventStartDates'] = df_serie['ENTSTEHUNGSZEIT - VON (Stufe Kollektion)'].apply(set_value)
    df_serie['eventEndDates'] = df_serie['ENTSTEHUNGSZEIT - BIS (Stufe Kollektion)'].apply(set_value)
    df_serie['eventDates'] = np.nan

    # set the "Medium", "Provenienz" and "Besitzvermerk"
    df_serie['radGeneralMaterialDesignation'] = df_serie['MEDIUM  /TYP (Stufe Kollektion)'].apply(set_value)
    df_serie['eventActors'] = df_serie['PROVENIENZ (Stufe Kollektion)'].apply(set_value)
    df_serie['archivalHistory'] = df_serie['BESITZVERMERK (Stufe Kollektion)'].apply(set_value)

    # append the level "Serie" to a new dataframe "df_lod"
    df_lod = df_serie

    # create a dataframe for the level "Teilserie" and append to "df_lod"
    df_sub['lod'] = df_sub['Teilserie'].apply(set_level, level=('2Teilserie'))
    df_teilserie = df_sub.loc[df_sub['lod'] == '2Teilserie']
    df_teilserie['title'] = df_teilserie['Teilserie'].apply(set_value)
    df_teilserie['scopeAndContent'] = df_teilserie['scope_Teilserie'].apply(set_value)
    df_teilserie['digitalObjectPath'] = df_teilserie['digitalObjectP'].apply(set_value)
    df_teilserie['hierarchyPath'] = df_teilserie['hierarchyPath'].apply(set_value)
    df_teilserie['extentAndMedium'] = df_teilserie['count'].apply(set_value)
    df_teilserie['eventActors'] = df_teilserie['NORM Körperschaft'].apply(set_value)
    df_lod = df_lod.append(df_teilserie)

    # create a dataframe for the level "Akte" and append to "df_lod"
    df_sub['lod'] = df_sub['Akte'].apply(set_level, level=('3Akte'))
    df_akte = df_sub.loc[df_sub['lod'] == '3Akte']
    df_akte['title'] = df_akte['Akte'].apply(set_value)
    df_akte['scopeAndContent'] = df_akte['scope_Akte'].apply(set_value)
    df_akte['digitalObjectPath'] = df_akte['digitalObjectP'].apply(set_value)
    df_akte['hierarchyPath'] = df_akte['hierarchyPath'].apply(set_value)
    df_akte['extentAndMedium'] = df_akte['count'].apply(set_value)
    df_lod = df_lod.append(df_akte)

    s1 = pd.Series(['0Bestand', 'IIJ', 'IIJ', '0_IIJ'])
    s2 = pd.Series(['0Teilbestand', 'Kinderzeichnungen Schweiz', 'IIJ/Kinderzeichnungen Schweiz', '0_IIJ/1_Kinderzeichnungen Schweiz'])
    df_bestand = pd.DataFrame([list(s1), list(s2)], columns =  ["lod", "title", 'digitalObjectPath', 'hierarchyPath'], index=[0,0])
    df_lod = df_lod.append(df_bestand)

    # final columns
    df_column_names = [
        'lod',
        'title',
        'scopeAndContent',
        'digitalObjectPath',
        'hierarchyPath',
        'extentAndMedium',
        'eventStartDates',
        'eventEndDates',
        'eventDates',
        'radGeneralMaterialDesignation',
        'eventActors',
        'archivalHistory'
        ]
    df_lod = df_lod[df_column_names]

    print(df_lod)
    print(df_lod.dtypes)

    ### data transformation ###

    # transform data before merging with levels of description
    # set the level "Objekt", title and scopeAndContent
    data['lod'] = '4Objekt'
    data['title'] = data['Objekt'].apply(set_value)
    data['scopeAndContent'] = data['scope_Objekt'].apply(set_value)
    #data['digitalObjectPath'] = data['digitalObjectPath'].apply(set_value)
    #data['hierarchyPath'] = data['hierarchyPath'].apply(set_value)


    ### data merging ###

    # merge data with levels of description
    mydata = pd.concat([data, df_lod])

    mydata['culture'] = "de"

    # sort the index by the index number and the level
    mydata = mydata.sort_index()
    mydata = mydata.rename_axis('MyIndex').sort_values(by = ['digitalObjectPath'])
    #mydata = mydata.rename_axis('MyIndex').sort_values(by = ['MyIndex', 'lod'])

    # reset the index
    mydata = mydata.reset_index()

    # rename levels of description
    mydata['lod'] = mydata['lod'].str.replace('\d+', '')

    # add repostiory name to all ressources
    mydata['repository'] = "Archiv der Kinder- und Jugendzeichnung"

    mydata = mydata.drop_duplicates(subset='digitalObjectPath', keep='first', inplace=False)

    # rename columns
    mydata.rename(columns={
        'lod': 'levelOfDescription',
        #'Ressourcen-ID(s)': 'alternativeIdentifiers',
        #'Alternativer Titel': 'alternateTitle', #omitted
        'Notizen (intern)': 'radPublishersSeriesNote',
        'Zustand': 'physicalCharacteristics',
        'Portal Publikation': 'radTitleProperOfPublishersSeries',
        'Kamera': 'radNotePhysicalDescription'}, inplace=True)

    # final columns
    column_names = [
        'alternativeIdentifiers',
        'alternativeIdentifierLabels',
        'repository',
        'hierarchyPath',
        #'legacyId',
        #'parentId',
        'scopeAndContent',
        'radNotePhysicalDescription',
        'radPublishersSeriesNote',
        'archivalHistory',
        #'alternateTitle',
        'genreAccessPoints',
        #'findingAids',
        'title',
        #'radTitleContinues',
        'identifier',
        'digitalObjectPath',
        'placeAccessPoints',
        #'radTitleProperOfPublishersSeries',
        #'status',
        'publicationStatus',
        'levelOfDescription',
        #'accessRestrictionIsPublic',
        'physicalCharacteristics',
        'subjectAccessPoints',
        'nameAccessPoints',
        #'radNoteGeneral',
        'radGeneralMaterialDesignation',
        'extentAndMedium',
        'eventTypes',
        'eventActors',
        'eventStartDates',
        'eventEndDates',
        'eventDates',
        'eventDescriptions',
        'eventPlaces',
        'culture'
        ]

    # create final dataset with correct column_names
    mydata_final = mydata[column_names]

    # export data to csv file
    export_csv = mydata.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Jupyter_Notebook\export_df_all.csv', encoding='utf-8', index = None, header=True)

    # export data to csv file
    export_csv_final = mydata_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Jupyter_Notebook\information-objects.csv', encoding='utf-8', index = None, header=True)


### authority records ###
    # authors
    df_author = mydata[['author', 'Urheber (Name, Vorname)', 'teacher', 'eventStartDates', 'eventEndDates', 'eventDates']]
    print(df_author)
    df_author['authorizedFormOfName'] = df_author['author'].drop_duplicates()
    df_author['parentAuthorizedFormOfName'] = df_author['author']
    df_author['alternateForm'] = df_author['Urheber (Name, Vorname)']

    df_author['sourceAuthorizedFormOfName'] = df_author['author']
    df_author['targetAuthorizedFormOfName'] = df_author['teacher']

    df_author['datesOfExistence'] = df_author[['eventStartDates', 'eventEndDates', 'eventDates']].apply(lambda x: str(x['eventDates']) if x['eventDates'] is not np.nan else str(x['eventStartDates']) + "-" + str(x['eventEndDates']), axis=1)
    df_author['date'] = df_author['eventDates']
    df_author['startDate'] = df_author['eventStartDates']
    df_author['endDate'] = df_author['eventEndDates']

    df_author['actorOccupations'] = "Schüler/in"
    df_author['formType'] = "parallel"
    df_author['culture'] = "de"
    df_author['category'] = "hierarchisch"
    df_author['description'] = "Schüler/in - Lehrperson"
    df_author = df_author.dropna(subset=['authorizedFormOfName'])
    print(df_author)

    # teachers
    df_teacher = mydata[['teacher']].drop_duplicates()
    df_teacher['authorizedFormOfName'] = df_teacher
    #df_teacher['datesOfExistence'] = df_teacher['Datierung']
    df_teacher['actorOccupations'] = "Lehrperson"

    # merge data with levels of description
    df_persons = df_author.append(df_teacher)
    df_persons['typeOfEntity'] = "Person"
    df_persons['culture'] = "de"

    df_kanon = mydata[['Kanon']].drop_duplicates()
    df_kanon['authorizedFormOfName'] = df_kanon['Kanon']
    df_kanon['actorOccupations'] = "Kanon"

    df_preis = mydata[['Preis']].drop_duplicates()
    df_preis['authorizedFormOfName'] = df_preis['Preis']
    df_preis['actorOccupations'] = "Prämierung"

    df_wettbwewerb = mydata[['NORM Körperschaft']].drop_duplicates()
    df_wettbwewerb['authorizedFormOfName'] = df_wettbwewerb['NORM Körperschaft']
    df_wettbwewerb['actorOccupations'] = "Wettbewerb"

    df_school = mydata[['school']].drop_duplicates()
    df_school['authorizedFormOfName'] = df_school['school']
    df_school['actorOccupations'] = "Schulhaus"

    df_organisations = df_kanon.append([df_preis, df_wettbwewerb, df_school]) # df_kanon.append(df_preis)
    df_organisations['typeOfEntity'] = "Organisation"
    df_organisations['culture'] = "de"

    # merge persons and organisations
    myauthorities = pd.concat([df_persons, df_organisations])
    myauthorities = myauthorities.dropna(subset=['authorizedFormOfName'])

    # final columns
    column_names_authorities = [
        'culture',
        'typeOfEntity',
        'authorizedFormOfName',
        'datesOfExistence',
        'actorOccupations'
        ]

    # final columns
    column_names_aliases = [
        'culture',
        'alternateForm',
        'formType',
        'parentAuthorizedFormOfName'
        ]

    # final columns
    column_names_relationsships = [
        'sourceAuthorizedFormOfName',
        'targetAuthorizedFormOfName',
        'category',
        'description',
        'date',
        'startDate',
        'endDate',
        'culture'
        ]

    # create final dataset with correct column_names
    myauthorities_final = myauthorities[column_names_authorities]
    #print(myauthorities_final)

    # create final dataset with correct column_names
    myaliases_final = df_author[column_names_aliases]
    print(myaliases_final)

    # create final dataset with correct column_names
    myrelationships_final = df_author[column_names_relationsships]
    myrelationships_final = myrelationships_final.dropna(subset=['targetAuthorizedFormOfName'])
    #print(myrelationships_final)

    # export data to csv file
    export_csv_authorities = myauthorities_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Jupyter_Notebook\authority-records.csv', encoding='utf-8', index = None, header=True)

    export_csv_aliases = myaliases_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Jupyter_Notebook\authority-records-aliases.csv', encoding='utf-8', index = None, header=True)

    export_csv_relationships = myrelationships_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Jupyter_Notebook\authority-records-relationships.csv', encoding='utf-8', index = None, header=True)


if __name__ == '__main__':
    main()
