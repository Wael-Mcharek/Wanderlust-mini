# Wanderlust-mini

A GUI software that helps you build and develop your german vocabulary ! This application is developed using PyQt Framework and this is a Beta version.

## Main features
- Easy to use and a minimalist GUI design.
- Add/delete sentences and words into/from the database.
- Auto-check if a sentence or a word already exists in the database.
- Auto-search for words by selecting them.
- Add/delete relationships between words and sentences.

## Getting Started

These instructions will help you setup your application. First of all put all the files in the same folder/directory.

### Prerequisites

1. PyQt5
2. [DEMorphy](https://github.com/DuyguA/DEMorphy/blob/master/README.md)
3. **SourceSansPro-ExtraLight** Font
4. **Broadway Regular** Font
5. [DB Browser for SQLite](https://sqlitebrowser.org) (to browse the SQLite Database)

### Setup your own web scraper
Modify the ```scraper``` method of the ```Data``` class in the **data_class.py** file.

When called this function must return a tuple containing a string and a list:
- The string is the **keyword** that represents the data associated to the searched word . It must be unique. The keyword could be the basic form of the searched word.
- The list is a list of dictionaries. Each dictionary represents a word associated with the searched word.

the dictionary must be in this form:

```
{'keyword': Insert the keyword here again (type: String), 
 'blocknum': the order of the word associated with the searched word (type: String),
 'wordname': the basic form of the word associated with the searched word (type: String),
 'carac': 'basic information such as the gender of the word/plural/pronunciation (type: String)',
 'phrase': idiom(s) or similar concept(s) (type: list containing string(s)),
 'gerdef': german definition(s) (type: list containing string(s)),
 'engdef': english definition(s) (type: list containing string(s)),
 'exampger': german example sentence(s) to understand the context (type: list containing string(s)),
 'exampeng': english translation of the german example sentence(s) (type: list containing string(s))
 }
 # if the dictionary keywords or lists are empty/have no results then insert a 'none' string:
 # Example:
 {'keyword': 'some keyword', 'blocknum': '1', 'wordname': 'some word', 'carac': 'some info', 'phrase': ['none'], 'gerdef': ['german definition'], 'engdef': ['english  definition'], 'exampger': ['none'], 'exampeng': ['none']
 }
 # the 'none' values will not be displayed by the program.
 # block numbers start from 1.
 # you cant set 'keyword' and 'blocknum' and 'wordname' and 'carac' to 'none'
 # you should have at least one 'gerdef' and 'engdef' resluts.
```

### Example of the result returned by the scraper method

keyword (searched word passed to the method): _sprechen_

sample result returned by the method:

```
('sprechen',[
{'keyword': 'sprechen', 'blocknum': '1', 'wordname': 'sprechen', 'carac': 'verb', 'phrase': ['none', 'etw. spricht für sich selbst'], 'gerdef': ['● german definition here', '● second german definition here'], 'engdef': ['english definition here', 'second english definition here'], 'exampger': ['german example here', 'second german example here'], 'exampeng': ['english example here', 'second english example here']}, 
{'keyword': 'sprechen', 'blocknum': '2', 'wordname': 'Sprechen', 'carac': 'noun', 'phrase': ['none'], 'gerdef': ['● german definition here'], 'engdef': ['english definition here'], 'exampger': ['german example here'], 'exampeng': ['english example here']}
])
```

if there are no results for the searched word then the method returns:

```
('', [])
```

## Usage

- You can always search for words in the **search** field
- Insert a german sentence into the **sentence box** (it will be autocompleted if it already exists in the data base). Then press **the insert** button (keyboard). Additionally, you can press the **delete** button (keyboard) to clear the **sentence box**
- When you insert a german sentence, select a word to auto-search it. The program will also auto-transform the selected word into its basic form (example: *hob* -> *heben*).
- When you insert a german sentence, a new field called **English Box** appears. Here you can insert a translation of the german sentence.
- When you insert a german sentence or insert a translation or search for words, the program automatically checks if they already exist in the database. The blue frame indicates that they already exist and the purple frame indicates the opposite.
- To add a search result or a translation or a german sentence to the database, drag and drop the **'+'** button into the respective fields: **sentence box** or **result** or **English Box** fields. (drag and drop using the right-click button)
- To delete a search result or a translation or a german sentence from the database, drag and drop the **'-'** button into the respective fields: **sentence box** or **result** or **English Box** fields. (drag and drop using the right-click button)
- To add a relationship between a search result and a german sentence, click the **'+'** button (the **result** and **sentence box** fields must not be empty and their content must exist in the database). The frame of the **sentence box** is now green, select the manifestation of the searched word in the german sentence (the selected words will be underlinded). You can select multiple words (example : select *gebe* and *auf* in *ich gebe auf* as a manifestation of *aufgeben*). when you finish, click the  **'+'** button to quit this mode and save the relationship in the database (the relationship words will have a colored font) or press the **escape** key (keyboard) to quit without saving.
- To delete a relationship between a search result and a german sentence, click the **'-'** button (the **sentence box** field must not be empty and its content must exist in the database and contain a relationship). The frame of the **sentence box** is now red, select the manifestation of the searched word in the german sentence (the selected words will have a black font again). when you finish, click the  **'-'** button to quit this mode and delete the relationship from the database or press the **escape** key (keyboard) to quit without deleting.

## Info on the database

Everything is stored in the **data.db** file. This database consists of 4 tables:
- **dict** : stores the search results. (like a dictionary)
- **us** : stores all the unique german sentences and their translations.
- **uw** : stores all the unique words.
- **us_uw**: stores the relationships between words and german sentences.

## Notes

It is not mandatory to use english as the reference language. You can program a scraper method that uses other reference languages.

## Future releases and modifications
- Releasing a complete scraper method (i already programmed one but it needs some modifications) and releasing a Windows EXE application.
- Improving **README** + a better usage explanation
- Releasing a refactored, optimized and a cleaned up code (with comments too !).
- Moving the ```lemmatizer``` method into a thread.
- Setting the left-click for the drag and drop instead of the right-click.
- Dark Mode support.
- Touch screen support.
- adding a **Licence and credits** section in **README**.

