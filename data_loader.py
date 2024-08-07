import pandas as pd


class DataLoader:
    def __init__(self, data_path=None):
        '''
        :param data_path: path to a folder that has train.csv, test.csv, validation.csv
        '''
        if data_path and data_path[-1] != '/':
            data_path += '/'
        self.tokenized_data = None
        self.data = None
        self.validation_df = None
        self.test_df = None
        self.train_df = None
        self.data_path = data_path
        if data_path:
            self.load_data()

    def load_data(self):
        '''
        Load the data from the data_path
        '''
        self.train_df = pd.read_csv(self.data_path + 'train.csv')
        self.test_df = pd.read_csv(self.data_path + 'test.csv')
        self.validation_df = pd.read_csv(self.data_path + 'validation.csv')
        self.merge_data()

    def remove_diacritics(self):
        self.data['text'] = self.data['text'].replace("ă", "a", regex=True).replace("â", "a", regex=True)\
            .replace("î", "i", regex=True).replace("ș", "s", regex=True).replace("ț", "t", regex=True).replace("Ă", "A", regex=True)\
            .replace("Â", "A", regex=True).replace("Î", "I", regex=True).replace("Ș", "S", regex=True).replace("Ț", "T", regex=True)

    def load_custom_data(self, df):
        self.data = df

    def load_texts(self, data):
        '''
        :param data: pandas DataFrame with 'title' and 'content' columns
        '''
        self.data = data

    def merge_data(self):
        '''
        Merge the data from the dataframes
        '''
        self.data = pd.concat([self.train_df, self.test_df, self.validation_df])

    def remove_nan(self):
        '''
        Remove the rows that have NaN values
        '''
        self.data = self.data.dropna()
        try:
            self.data = self.data.drop(self.data[self.data['text'].apply(lambda x: x == '')].index)
        except:
            pass

    def keep_only_title_with_balance(self):
        '''
        Keep only the title column
        '''
        def f(x):
            if pd.isnull(x):
                return ''
            x = x.split('.')
            if len(x[0].split()) < 5:
                return ' '.join(x[:2])
            return x[0]

        self.data['text'] = self.data['title'].apply(lambda x: x if not pd.isnull(x) else '') + '-----' + self.data[
            'content'].apply(f)
        self.data = self.data.drop(columns=['title', 'content'])
        self.remove_nan()
        self.balance_data()
        self.data['text'] = self.data['text'].apply(lambda x: x.split('-----')[0])

    def add_first_sentence_to_title(self):
        '''
        Add the first sentence of the content to the title.
        '''
        def f(x):
            if pd.isnull(x):
                return ''
            x = x.split('.')
            if len(x[0].split()) < 5:
                return ' '.join(x[:2])
            return x[0]

        self.data['text'] = self.data['title'].apply(lambda x: x if not pd.isnull(x) else '') + '. ' + self.data[
            'content'].apply(f)
        self.data = self.data.drop(columns=['title', 'content'])
        self.data['text'] = self.data['text'].apply(lambda x: x if not x.startswith('. ') else x[2:])

    def add_content_to_title(self, chars_num):
        '''
        Add the first chars_num characters of the content to the title.
        '''
        def f(text):
            if pd.isnull(text) or len(text) == 0:
                return ''
            final = ""
            for sent in text.split('.'):
                sent = sent.strip()
                if len(final + sent) < chars_num:
                    final += sent + '. '
                else:
                    break
            return final
        self.data['text'] = self.data['title'].apply(lambda x: x if not pd.isnull(x) else '') + '. ' + self.data[
            'content'].apply(f)
        self.data['text'] = self.data['text'].apply(lambda x: x if not x.startswith('. ') else x[2:])

    def balance_data(self):
        satirical_df = self.data[self.data['label'] == 1]
        non_satirical_df = self.data[self.data['label'] == 0]
        min_len = min(len(satirical_df), len(non_satirical_df))
        satirical_df = satirical_df.sample(min_len, random_state=42)
        non_satirical_df = non_satirical_df.sample(min_len, random_state=42)
        self.data = pd.concat([satirical_df, non_satirical_df])

    def remove_multiple_spaces(self):
        self.data['text'] = self.data['text'].replace(r'\s+', ' ', regex=True)

    def remove_html_tags(self):
        self.data['text'] = self.data['text'].replace(r'<[^>]+>', '', regex=True)

    def remove_new_lines(self):
        self.data['text'] = self.data['text'].replace(r'\n', ' ', regex=True)

    def remove_cedilla(self):
        self.data['text'] = self.data['text'].replace("ţ", "ț", regex=True).replace("ş", "ș", regex=True).replace("Ţ", "Ț", regex=True).replace("Ş", "Ș", regex=True)
