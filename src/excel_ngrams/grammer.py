import pandas as pd

class Grammer:

    def word_list_from_excel_doc(self, path, column_name):
        df = pd.read_excel(path)
        return df[column_name].tolist()