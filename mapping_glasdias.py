#!/usr/bin/env python
"""Summary
"""
# coding: utf-8


import pandas as pd
import numpy as np
import random
import hashlib


def cast_value(value):
    return str(value)

def float_to_int(value):
    return pd.to_numeric(value, downcast='integer' )  if not pd.isnull(value) else value

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

# function to define the level 
def set_level(value, level):
    return level if not pd.isnull(value) else value

# function to set the value for a column
def set_value(value):
    return value if not pd.isnull(value) else value

# function to set the value for a column
def set_organisation(value):
    if value == 'Internationales Institut für das Studium der Jugendzeichnung':
        return "Organisation"
    else:
        return "Fotograf/in"


def main():
    """Summary"""

    path_to_file = "D:/mastranelena/Desktop/Pestalozzianum/Glasdias/Export2/glasdias_full_noexp-txt.csv"
    data = pd.read_csv(path_to_file, encoding='utf-8', index_col=False)

### data preparation ###
    data['Bestand'] = "Bestand zu " + data['Teilserie']
    data['Teilbestand'] = "Teilbestand zu " + data['Teilserie']
    data['Gruppe'] = "Gruppe zu " + data['Teilserie']

    # merge title column with alternate title    
    data['Titel'].loc[data['AlternativerTitel'].notnull() == True] = data['Titel'] + "/[" + data['Titel'] + " " + data['AlternativerTitel'] + "]"
    #data['Titel'].loc[data['Titel'].notnull() == False] = "[" + data['AlternativerTitel'] + "]"

    # rename title columns
    #data.rename(columns={'THEMEN NAME (Stufe Kollektion)': 'Path', 'Titel Teilserie': 'Teilserie', 'Titel Akte': 'Akte', 'Titel': 'Objekt'}, inplace=True)
    data.rename(columns={'Titel Teilserie': 'Teilserie', 'Titel': 'Objekt'}, inplace=True)

    # rename scopeAndContent columns
    #data.rename(columns={'BESCHREIBUNG (Stufe Kollektion)': 'scope_Serie', 'Merkmale Teilserie': 'scope_Teilserie', 'Merkmale der Akte': 'scope_Akte', 'Beschreibung': 'scope_Objekt'}, inplace=True)
    data.rename(columns={'Merkmale Teilserie': 'scope_Teilserie', 'Beschreibung': 'scope_Objekt'}, inplace=True)

    # create column for level "Bestand"
    data['Bestand'] = data['Path'].apply(split_column, number=(0))

    # create column for level "Teilbestand"
    data['Teilbestand'] = data['Path'].apply(split_column, number=(1))

    # create column for level "Serie"
    data['Gruppe'] = data['Path'].apply(split_column, number=(2))

    # create column for level "Serie"
    data['Serie'] = data['Path'].apply(split_column, number=(3))

    ### LevelOfDescription (lod)
    data['lod'] = "Objekt"

    ### Identifier
    # create column for identifier
    data['identifier'] = data['Signatur']#.replace({r'(.*)(.tif|.tiff|.jpg|.pdf)' : r'\1'}, regex=True)

    ### add identifier
    data['digitalObjectPath'] = data['Url']

    ### RadGeneralMaterialDesignation
    data['radGeneralMaterialDesignation'] = "Glasdiapositiv"

    ### PublicationStatus
    data['publicationStatus'] = "Entwurf"

    ### TODO: AlternativeIdentifiers
    data['alternativeIdentifiers'] = data['Record']
    data['alternativeIdentifiers'].loc[data['Signatur'].notnull() == True] = data['alternativeIdentifiers'].astype(str) + "|" + data['Signatur']

    data['alternativeIdentifierLabels'] = data['alternativeIdentifierLabels'].loc[data['Record'].notnull() == True] = "Record"
    data['alternativeIdentifierLabels'].loc[data['Signatur'].notnull() == True] = data['alternativeIdentifierLabels'] + "|" + "Signatur"

    ### digitalObjectP
    data['digitalObjectP'] = data['Path']
    data['digitalObjectP'].loc[data['Teilserie'].notnull() == True] = data['digitalObjectP'] + "/" + data['Teilserie']
    #data['digitalObjectP'].loc[data['Akte'].notnull() == True] = data['digitalObjectP'] + "/" + data['Akte']
    data['digitalObjectP'].loc[data['identifier'].notnull() == True] = data['identifier']
    # sort data
    data = data.sort_values(by = ['digitalObjectP'])
    print(data)

    ### HierarchyPath
    data['hierarchyPath'] = "0_" + data['Bestand']
    data['hierarchyPathBestand'] = data['hierarchyPath']
    data['hierarchyPath'] = data['hierarchyPath'] + "/1_" + data['Teilbestand']
    data['hierarchyPathTeilbestand'] = data['hierarchyPath']

    data['hierarchyPath'] = data['hierarchyPath'] + "/2_" + data['Gruppe']
    data['hierarchyPathGruppe'] = data['hierarchyPath']

    data['hierarchyPath'] = data['hierarchyPath'] + "/3_" + data['Serie']
    data['hierarchyPathSerie'] = data['hierarchyPath']

    data['hierarchyPath'].loc[data['Teilserie'].notnull() == True] = data['hierarchyPath'] + "/4_" + data['Teilserie']
    data['hierarchyPathTeilserie'] = data['hierarchyPath']

    #data['hierarchyPath'].loc[data['Akte'].notnull() == True] = data['hierarchyPath'] + "/4_" + data['Akte']
    #data['hierarchyPathAkte'] = data['hierarchyPath']

    ### Count values for ExtentAndMedium
    #data['countTeilbestand'] = data.groupby('hierarchyPathTeilbestand')['hierarchyPathTeilbestand'].transform('countTeilbestand')
    data['count'] = data.groupby('Bestand')['Bestand'].transform('count')
    data['count'] = data.groupby('Teilbestand')['Teilbestand'].transform('count')
    data['count'] = data.groupby('Gruppe')['Gruppe'].transform('count')
    data['count'] = data.groupby('Serie')['Serie'].transform('count')
    data['count'].loc[data['Teilserie'].notnull() == True] = data.groupby('Teilserie')['Teilserie'].transform('count')
    #data['count'].loc[data['Akte'].notnull() == True] = data.groupby('Akte')['Akte'].transform('count')

    ### Author
    data['author'] = data['Urheber']

    data['eventTypes'] = "Herstellung"
    data['eventActors'] = data['Urheber']

    # Create field for "eventDescription" 
    data['eventDescriptions'] = data['Verlag']
    data['eventDescriptions'].loc[(data['eventDescriptions'].notnull() == True) & (data['Herstellung'].notnull() == True)] = data['eventDescriptions'] + ", " + data['Herstellung']
    data['eventDescriptions'].loc[data['eventDescriptions'].notnull() == False] = data['Herstellung']

    # Set eventStartDates, eventEndDates and eventDates
    data['eventStartDates'] = data[['Zeitraum von', 'Datierung']].apply(lambda x: str(x['Datierung']) if x['Datierung'] == np.nan else str(x['Zeitraum von']), axis=1)
    data['eventEndDates'] = data[['Zeitraum bis', 'Datierung']].apply(lambda x: str(x['Datierung']) if x['Datierung'] == np.nan else str(x['Zeitraum bis']), axis=1)
    data['eventDates'] = data['Datierung']
    data['myDates'] = data[['eventStartDates', 'eventEndDates', 'eventDates']].apply(lambda x: str(x['eventDates']).replace('.0', '') if x['eventDates'] == np.nan else str(x['eventStartDates']).replace('.0', '') + "-" + str(x['eventEndDates']).replace('.0', ''), axis=1)
    print(data['myDates'])

    ### Create eventPlaces ###
    data['eventPlaces'] = data['Ort']
    #data['eventPlaces'].loc[data['Kanton'].notnull() == True] = data['eventPlaces'] + ", " + data['Kanton']
    #data['eventPlaces'].loc[data['Region'].notnull() == True] = data['eventPlaces'] + ", " + data['Region']
    #data['eventPlaces'].loc[data['Land'].notnull() == True] = data['eventPlaces'] + ", " + data['Land']


    ### Create subject ###
    #data['subjectAccessPoints'] = data['Alter']
    #data['subjectAccessPoints'] = data['subjectAccessPoints'] + "|" + data['gender']

    ### Prämierung ###
    #data['Preis'].loc[data['Preis'].notnull() == True] = data['Preis'] + " (Prämierung)"
    #data['subjectAccessPoints'].loc[data['Preis'].notnull() == True] = data['subjectAccessPoints'] + "|" + data['Preis']

    ### Create subjectAccessPoints ###
    data['subjectAccessPoints'] = data['Schlagworte'] + " (Schlagwort)"
    #data['Schlagworte'] = data['Schlagworte'].str.replace(', ', ' (Schlagwort)|')
    #data['subjectAccessPoints'] = data['subjectAccessPoints'] + "|" + data['Schlagworte'] + " (Schlagwort)"

    ### ExtentAndMedium ###
    data['extentAndMedium'] = "Technik: " + data['Technik']

    ### add values from field Trägermaterial
    data['Trägermaterial'] = data['Trägermaterial']
    data['extentAndMedium'].loc[data['Trägermaterial'].notnull() == True] = data['extentAndMedium'] + "| Trägermaterial: " + data['Trägermaterial']

    # add values from field Masse
    # if not null add to extentAndMedium
    data['extent'] = data['Masse']

    data['extentAndMedium'].loc[data['extent'].notnull() == True] = data['extentAndMedium'] + "| " + data['extent']

    ### GenreAccessPoints (Technik) ###
    data['genre'] = data['Technik'].str.replace(', ', '|')
    data['genreAccessPoints'] = data['genre']

    ### Tags ###
    #data['scope_Objekt'].loc[data['Tag(s)'].notnull() == True] = data['scope_Objekt'] + "| Tags: " + data['Tag(s)']
    #data['scope_Objekt'].loc[data['scope_Objekt'].notnull() == False] = "Tags: " + data['Tag(s)']

    ### NameAccessPoints ###
    #data['Kanon'] = data['Kanon'] + " (Referenz)"
    #data['nameAccessPoints'] = data['Kanon']
    #data['nameAccessPoints'].loc[data['Kanon'].notnull() == True] = data['Kanon']

    ### Lehrperson resp. Herstellung ###
    data['teacher'] = data['Herstellung']
    #data['nameAccessPoints'].loc[(data['nameAccessPoints'].notnull() == True) & (data['teacher'].notnull() == True)] = data['nameAccessPoints'] + "|" + data['teacher']
    #data['nameAccessPoints'].loc[data['nameAccessPoints'].notnull() == False] = data['teacher']
    data['nameAccessPoints'] = data['teacher']

    ### Schulhaus resp. Verlag ###
    data['school'] = data['Verlag']
    data['nameAccessPoints'].loc[(data['nameAccessPoints'].notnull() == True) & (data['school'].notnull() == True)] = data['nameAccessPoints'] + "|" + data['school']
    data['nameAccessPoints'].loc[data['nameAccessPoints'].notnull() == False] = data['school']

    ### Körperschaft/Wettbewerb ###
    #data['NORM Körperschaft'].loc[data['NORM Körperschaft'].notnull() == True] = data['NORM Körperschaft'] + " (Wettbewerb)"
    #data['nameAccessPoints'].loc[(data['nameAccessPoints'].notnull() == True) & (data['NORM Körperschaft'].notnull() == True)] = data['nameAccessPoints'] + "|" + data['NORM Körperschaft']
    #data['nameAccessPoints'].loc[data['nameAccessPoints'].notnull() == False] = data['NORM Körperschaft']

    ### Prämierung ###
    #data['nameAccessPoints'].loc[data['Preis'].notnull() == True] = data['nameAccessPoints'] + "|" + data['Preis'] + " (Prämierung)"

    ### Ort ###
    data['placeAccessPoints'] = data['eventPlaces']

### end : data preparation ###


### levels of description ###
    df_sub = data.drop_duplicates(subset='hierarchyPath', keep='first', inplace=False)

    # create a dataframe for the level "Bestand" and append it to the dataframe "df_lod"
    # set the levelOfDescription, title and scopeAndContent
    df_sub['lod'] = df_sub['Bestand'].apply(set_level, level=('0Bestand'))
    df_Bestand = df_sub.loc[df_sub['lod'] == '0Bestand']
    df_Bestand['title'] = df_Bestand['Bestand'].apply(set_value)
    #df_Bestand['scopeAndContent'] = df_Bestand['scope_Bestand'].apply(set_value)
    df_Bestand['digitalObjectP'] = df_Bestand['digitalObjectP'].apply(set_value)
    df_Bestand['hierarchyPath'] = df_Bestand['hierarchyPathBestand']
    # set the count value as the number of objects at group level
    df_Bestand['extentAndMedium'] = df_Bestand['count'].apply(set_value)
    df_Bestand['extentAndMedium'] = df_Bestand['extentAndMedium'].astype(str) + " Objekte"

    # set the eventStartDates, eventEndDates and eventDates
    df_Bestand['eventStartDates'] = np.nan
    df_Bestand['eventEndDates'] = np.nan
    df_Bestand['eventDates'] = np.nan

    # set the "Medium", "Provenienz" and "Besitzvermerk"
    df_Bestand['radGeneralMaterialDesignation'] = df_Bestand['Medium/Typ'].apply(set_value)
    df_Bestand['eventActors'] = df_Bestand['Urheberrecht'].apply(set_value)
    #df_Bestand['eventActors'] = df_Bestand['PROVENIENZ (Stufe Kollektion)'].apply(set_value)
    df_Bestand['archivalHistory'] = df_Bestand['AnmerkungTitel'].apply(set_value)

    # drop duplicates of type "Serie"
    df_Bestand = df_Bestand.drop_duplicates(subset='Bestand', keep='first', inplace=False)

    # append the level "Serie" to a new dataframe "df_lod"
    df_lod = df_Bestand

    # create a dataframe for the level "Teilbestand" and append it to the dataframe "df_lod"
    # set the levelOfDescription, title and scopeAndContent
    df_sub['lod'] = df_sub['Teilbestand'].apply(set_level, level=('1Teilbestand'))
    df_Teilbestand = df_sub.loc[df_sub['lod'] == '1Teilbestand']
    df_Teilbestand['title'] = df_Teilbestand['Teilbestand'].apply(set_value)
    #df_Teilbestand['scopeAndContent'] = df_Teilbestand['scope_Teilbestand'].apply(set_value)
    df_Teilbestand['digitalObjectP'] = df_Teilbestand['digitalObjectP'].apply(set_value)
    df_Teilbestand['hierarchyPath'] = df_Teilbestand['hierarchyPathTeilbestand']
    # set the count value as the number of objects at group level
    df_Teilbestand['extentAndMedium'] = df_Teilbestand['count'].apply(set_value)
    df_Teilbestand['extentAndMedium'] = df_Teilbestand['extentAndMedium'].astype(str) + " Objekte"

    # set the eventStartDates, eventEndDates and eventDates
    df_Teilbestand['eventStartDates'] = np.nan
    df_Teilbestand['eventEndDates'] = np.nan
    df_Teilbestand['eventDates'] = np.nan

    # set the "Medium", "Provenienz" and "Besitzvermerk"
    df_Teilbestand['radGeneralMaterialDesignation'] = df_Teilbestand['Medium/Typ'].apply(set_value)
    df_Teilbestand['eventActors'] = df_Teilbestand['Urheberrecht'].apply(set_value)
    #df_Teilbestand['eventActors'] = df_Teilbestand['PROVENIENZ (Stufe Kollektion)'].apply(set_value)
    df_Teilbestand['archivalHistory'] = df_Teilbestand['AnmerkungTitel'].apply(set_value)

    # drop duplicates of type "Serie"
    df_Teilbestand = df_Teilbestand.drop_duplicates(subset='Teilbestand', keep='first', inplace=False)

    # append the level "Serie" to a new dataframe "df_lod"
    df_lod = df_lod.append(df_Teilbestand)

    # create a dataframe for the level "Gruppe" and append it to the dataframe "df_lod"
    # set the levelOfDescription, title and scopeAndContent
    df_sub['lod'] = df_sub['Gruppe'].apply(set_level, level=('2Gruppe'))
    df_Gruppe = df_sub.loc[df_sub['lod'] == '2Gruppe']
    df_Gruppe['title'] = df_Gruppe['Gruppe'].apply(set_value)
    #df_Gruppe['scopeAndContent'] = df_Gruppe['scope_Gruppe'].apply(set_value)
    df_Gruppe['digitalObjectP'] = df_Gruppe['digitalObjectP'].apply(set_value)
    df_Gruppe['hierarchyPath'] = df_Gruppe['hierarchyPathGruppe'].apply(set_value)
    # set the count value as the number of objects at group level
    df_Gruppe['extentAndMedium'] = df_Gruppe['count'].apply(set_value)
    df_Gruppe['extentAndMedium'] = df_Gruppe['extentAndMedium'].astype(str) + " Objekte"

    # set the eventStartDates, eventEndDates and eventDates
    df_Gruppe['eventStartDates'] = np.nan
    df_Gruppe['eventEndDates'] = np.nan
    df_Gruppe['eventDates'] = np.nan

    # set the "Medium", "Provenienz" and "Besitzvermerk"
    df_Gruppe['radGeneralMaterialDesignation'] = df_Gruppe['Medium/Typ'].apply(set_value)
    df_Gruppe['eventActors'] = df_Gruppe['Urheberrecht'].apply(set_value)
    #df_Gruppe['eventActors'] = df_Gruppe['PROVENIENZ (Stufe Kollektion)'].apply(set_value)
    df_Gruppe['archivalHistory'] = df_Gruppe['AnmerkungTitel'].apply(set_value)

    # drop duplicates of type "Serie"
    df_Gruppe = df_Gruppe.drop_duplicates(subset='Gruppe', keep='first', inplace=False)

    # append the level "Serie" to a new dataframe "df_lod"
    df_lod = df_lod.append(df_Gruppe)

    # create a dataframe for the level "Serie" and append it to the dataframe "df_lod"
    # set the levelOfDescription, title and scopeAndContent
    df_sub['lod'] = df_sub['Serie'].apply(set_level, level=('3Serie'))
    df_serie = df_sub.loc[df_sub['lod'] == '3Serie']
    df_serie['title'] = df_serie['Serie'].apply(set_value)
    #df_serie['scopeAndContent'] = df_serie['scope_Serie'].apply(set_value)
    df_serie['digitalObjectP'] = df_serie['digitalObjectP'].apply(set_value)
    df_serie['hierarchyPath'] = df_serie['hierarchyPathSerie']
    # set the count value as the number of objects at serie level
    df_serie['extentAndMedium'] = df_serie['count'].apply(set_value)
    df_serie['extentAndMedium'] = df_serie['extentAndMedium'].astype(str) + " Objekte"

    # set the eventStartDates, eventEndDates and eventDates
    df_serie['eventStartDates'] = np.nan
    df_serie['eventEndDates'] = np.nan
    df_serie['eventDates'] = np.nan

    # set the "Medium", "Provenienz" and "Besitzvermerk"
    df_serie['radGeneralMaterialDesignation'] = df_serie['Medium/Typ'].apply(set_value)
    df_serie['eventActors'] = df_serie['Urheberrecht'].apply(set_value)
    #df_serie['eventActors'] = df_serie['PROVENIENZ (Stufe Kollektion)'].apply(set_value)
    df_serie['archivalHistory'] = df_serie['AnmerkungTitel'].apply(set_value)

    # drop duplicates of type "Serie"
    df_serie = df_serie.drop_duplicates(subset='Serie', keep='first', inplace=False)

    # append the level "Serie" to a new dataframe "df_lod"
    df_lod = df_lod.append(df_serie)

    # create a dataframe for the level "Teilserie" and append to "df_lod"
    df_sub['lod'] = df_sub['Teilserie'].apply(set_level, level=('4Teilserie'))
    df_teilserie = df_sub.loc[df_sub['lod'] == '4Teilserie']
    df_teilserie['title'] = df_teilserie['Teilserie'].apply(set_value)
    #TODO: df_teilserie['title'] = df_teilserie['Teilserie'].str.replace('\,.*$','')
    df_teilserie['scopeAndContent'] = df_teilserie['Teilserie'].apply(set_value)
    df_teilserie['digitalObjectP'] = df_teilserie['digitalObjectP'].apply(set_value)
    df_teilserie['hierarchyPath'] = df_teilserie['hierarchyPathTeilserie']
    df_teilserie['extentAndMedium'] = df_teilserie['count'].apply(set_value)
    df_teilserie['extentAndMedium'] = df_teilserie['extentAndMedium'].astype(str) + " Objekte"
    #TODO: Prüfen, ob korrekt
    #df_teilserie['eventActors'].loc[df_teilserie['NORM Körperschaft'].notnull() == True] = df_teilserie['NORM Körperschaft'].apply(set_value)
    #df_teilserie['eventActors'].loc[df_teilserie['NORM Körperschaft'].notnull() == False] = ""

    # drop duplicates of type "Serie"
    df_teilserie = df_teilserie.drop_duplicates(subset='Teilserie', keep='first', inplace=False)

    df_lod = df_lod.append(df_teilserie)

    # create a dataframe for the level "Akte" and append to "df_lod"
    #df_sub['lod'] = df_sub['Akte'].apply(set_level, level=('3Akte'))
    #df_akte = df_sub.loc[df_sub['lod'] == '3Akte']
    #df_akte['title'] = df_akte['Akte'].apply(set_value)
    #df_akte['scopeAndContent'] = df_akte['scope_Akte'].apply(set_value)
    #df_akte['digitalObjectP'] = df_akte['digitalObjectP'].apply(set_value)
    #df_akte['hierarchyPath'] = df_akte['hierarchyPathAkte'].apply(set_value)
    #df_akte['extentAndMedium'] = df_akte['count'].apply(set_value)
    #df_akte['extentAndMedium'] = df_akte['extentAndMedium'].astype(str) + " Objekte"
    #df_akte['eventActors'] = ""
    #df_lod = df_lod.append(df_akte)

    #s1 = pd.Series(['0Bestand', 'Bestand', 'Bestand', '0_Bestand'])
    #s2 = pd.Series(['0Teilbestand', 'Teilbestand', 'Bestand/Teilbestand', '0_Bestand/1_Teilbestand'])
    #df_bestand = pd.DataFrame([list(s1), list(s2)], columns =  ["lod", "title", 'digitalObjectP', 'hierarchyPath'], index=[0,0])
    #df_lod = df_lod.append(df_bestand)

    # final columns
    df_column_names = [
        'lod',
        'title',
        'scopeAndContent',
        'digitalObjectP',
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

    ### data transformation ###

    # transform data before merging with levels of description
    # set the level "Objekt", title and scopeAndContent
    data['lod'] = '4Objekt'
    data['title'] = data['Objekt'].apply(set_value)
    data['scopeAndContent'] = data['scope_Objekt'].apply(set_value)
    #data['digitalObjectP'] = data['digitalObjectP'].apply(set_value)
    #data['hierarchyPath'] = data['hierarchyPath'].apply(set_value)

    ### data merging ###

    # merge data with levels of description
    mydata = pd.concat([data, df_lod])

    mydata['culture'] = "de"

    # sort the index by the index number and the level
    mydata = mydata.sort_index()
    mydata = mydata.rename_axis('MyIndex')#.sort_values(by = ['digitalObjectP'])
    #mydata = mydata.rename_axis('MyIndex').sort_values(by = ['MyIndex', 'lod'])

    # reset the index
    mydata = mydata.reset_index()
    print(mydata)

    # rename levels of description
    mydata['lod'] = mydata['lod'].str.replace('\d+', '')

    # add repostiory name to all ressources
    mydata['repository'] = "Historische Glasdias"

    # add digitalObjectP to check the right position
    mydata['digitalObjectP'] = mydata['hierarchyPath']
    mydata['digitalObjectP'].loc[mydata['identifier'].notnull() == True] = mydata['digitalObjectP'] + "/" + mydata['identifier']

    mydata = mydata.rename_axis('MyIndex').sort_values(by = ['digitalObjectP'])
    print(mydata)

    #mydata = mydata.drop_duplicates(subset='digitalObjectP', keep='first', inplace=False)

    # rename columns
    mydata.rename(columns={
        'lod': 'levelOfDescription',
        #'Ressourcen-ID(s)': 'alternativeIdentifiers',
        #'Alternativer Titel': 'alternateTitle', #omitted
        'Notizen (intern)1': 'radPublishersSeriesNote',
        #'Zustand': 'physicalCharacteristics',
        'Portal Publikation': 'radTitleProperOfPublishersSeries',
        'Kamera': 'radNotePhysicalDescription'}, inplace=True)

    # final columns
    column_names = [
        'alternativeIdentifiers',
        'alternativeIdentifierLabels',
        'repository',
        'hierarchyPath',
        #'digitalObjectP',
        #'legacyId',
        #'parentId',
        'scopeAndContent',
        #'radNotePhysicalDescription',
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
        #'physicalCharacteristics',
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
    #mydata_final['eventStartDates'] = pd.to_numeric(mydata_final['eventStartDates'], downcast='integer')
    #mydata_final['eventStartDates'] = mydata_final['eventStartDates']

    # export data to csv file
    export_csv = mydata.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Glasdias\Export2\export_df_all.csv', encoding='utf-8', index = None, header=True)

    # export data to csv file
    export_csv_final = mydata_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Glasdias\Export2\information-objects.csv', encoding='utf-8', index = None, header=True)


### authority records ###
    # authors
    df_author = mydata[['author', 'Urheber', 'teacher', 'myDates', 'eventStartDates', 'eventEndDates', 'eventDates']]
    df_author['authorizedFormOfName'] = df_author['author'].drop_duplicates()
    df_author['parentAuthorizedFormOfName'] = df_author['author']
    df_author['alternateForm'] = df_author['Urheber']

    df_author['sourceAuthorizedFormOfName'] = df_author['author']
    df_author['targetAuthorizedFormOfName'] = df_author['teacher']

    df_author['datesOfExistence'] = df_author['myDates']
    df_author['date'] = df_author['eventDates']
    df_author['startDate'] = df_author['eventStartDates']
    df_author['endDate'] = df_author['eventEndDates']

    df_author['actorOccupations'] = df_author['authorizedFormOfName'].apply(set_organisation)
    df_author['formType'] = "parallel"
    df_author['culture'] = "de"
    df_author['category'] = "hierarchisch"
    df_author['description'] = "Urheber/in - Körperschaft"
    df_author = df_author.dropna(subset=['authorizedFormOfName'])
    print(df_author)

    # teachers resp. Herstellung
    df_teacher = mydata[['teacher']].drop_duplicates()
    df_teacher['authorizedFormOfName'] = df_teacher
    #df_teacher['datesOfExistence'] = df_teacher['Datierung']
    df_teacher['actorOccupations'] = "Körperschaft"

    # merge data with levels of description
    df_persons = df_author.append(df_teacher)
    df_persons['typeOfEntity'] = "Organisation"
    df_persons['culture'] = "de"

    #df_kanon = mydata[['Kanon']].drop_duplicates()
    #df_kanon['authorizedFormOfName'] = df_kanon['Kanon']
    #df_kanon['actorOccupations'] = "Referenz"

    #df_preis = mydata[['Preis']].drop_duplicates()
    #df_preis['authorizedFormOfName'] = df_preis['Preis']
    #df_preis['actorOccupations'] = "Prämierung"

    #df_wettbwewerb = mydata[['NORM Körperschaft']].drop_duplicates()
    #df_wettbwewerb['authorizedFormOfName'] = df_wettbwewerb['NORM Körperschaft']
    #df_wettbwewerb['actorOccupations'] = "Wettbewerb"

    # school resp. Verlag
    df_school = mydata[['school']].drop_duplicates()
    df_school['authorizedFormOfName'] = df_school['school']
    df_school['actorOccupations'] = "Verlag"

    #df_organisations = df_kanon.append([df_preis, df_wettbwewerb, df_school]) # df_kanon.append(df_preis)
    df_organisations = df_school # df_kanon.append(df_preis)
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
    export_csv_authorities = myauthorities_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Glasdias\Export2\authority-records.csv', encoding='utf-8', index = None, header=True)

    export_csv_aliases = myaliases_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Glasdias\Export2\authority-records-aliases.csv', encoding='utf-8', index = None, header=True)

    export_csv_relationships = myrelationships_final.to_csv (r'D:\mastranelena\Desktop\Pestalozzianum\Glasdias\Export2\authority-records-relationships.csv', encoding='utf-8', index = None, header=True)


if __name__ == '__main__':
    main()
