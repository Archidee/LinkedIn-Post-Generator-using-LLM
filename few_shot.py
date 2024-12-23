import json
import pandas as pd



class FewShotPosts:
    def __init__ (self, file_path="data/processed_posts.json"):
        self.df = None
        self.unique_tags= None
        self.load_posts(file_path)

    def load_posts(self,file_path):
        
        try:
            with open(file_path, encoding='utf-8') as f :
        
                posts=json.load(f)
                df =pd.json_normalize(posts)
                if "line_count" not in df.columns:
                    raise KeyError("Missing 'line_count' column in data.")

                df['length']= df['line_count'].apply(self.categorize_length)
                all_tags=df['tags'].apply(lambda x: x).sum()
                self.unique_tags = set(list(all_tags))

                self.df = df
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
        except json.JSONDecodeError:
            print(f"Error: File '{file_path}' is not a valid JSON.")
        except Exception as e:
            print(f"Error: {e}")
    

            
    def categorize_length(self,line_count):
        if line_count<7:
            return "Short"
        elif 7<=line_count<15:
            return "Medium"
        else:
            return "long"
    def get_tags(self):
        return self.unique_tags
        
    def get_filtered_posts(self,length,tag):
        df_filtered_list = self.df[

            (self.df['length']==length) & 
            (self.df['tags'].apply(lambda tags: tag in tags)) 
        ]

        return df_filtered_list.to_dict(orient='records')
  #  pass

if __name__=="__main__":
    fs = FewShotPosts()
    posts=fs.get_filtered_posts('Short','AI')
    print(posts)

    #result = fs.df.columns
    
    #print(result)

    pass
    