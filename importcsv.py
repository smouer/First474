import pandas as pd
def dataimport(filename):                             
    "Pulls CSV into Python dataframe"
    csv = pd.read_csv (r'C:\Filepath\filename.csv')
    data = pd.DataFrame(csv)
    return(data)
# with data we can feed google query data[LOCATIONSCOLUMNNAME], making sure depot is entered first everytime. 
