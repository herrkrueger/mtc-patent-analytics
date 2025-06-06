import pandas as pd

class TreeData():

    def __init__(self, scheme, scheme_by_level_and_parent):
        self.scheme = scheme
        self.scheme_by_level_and_parent = scheme_by_level_and_parent


    def get_children(self, level, symbol, scheme_by_level_and_parent):
        parent = (level + 1, symbol)
        children_group = self.scheme_by_level_and_parent.get_group(parent)
        children_symbols = children_group['symbol'].tolist()
        children_dates = children_group['creation_date'].tolist()
        children_sizes = children_group['size'].tolist()
        children_sizes_percent = children_group['size_percent'].tolist()
        children_sizes_normalised = children_group['size_normalised'].tolist()
        children = []
        for i in range(len(children_group)):
            child = {"name" : children_symbols[i] , "date" : str(children_dates[i])[:4] , "size" : children_sizes[i], "size_percent" : children_sizes_percent[i], "size_normalised" : children_sizes_normalised[i]}
            children.append(child)
        return children

    def flatten_nested_json(self, data):
        symbols=[]
        for key, value in data.items():
            if key == "name":
                symbols.append(value)
            elif isinstance(value, list):
                for element in value:
                    symbols += self.flatten_nested_json(element)
        return symbols

    def get_titles(self, language, symbols):
        titles = pd.DataFrame(symbols, columns=['symbol']).set_index('symbol').join(self.scheme[['symbol', 'title_' + language]].set_index('symbol'))
        titles.reset_index(level=0, inplace=True)
        titles = titles.to_json(orient='records')
        return titles