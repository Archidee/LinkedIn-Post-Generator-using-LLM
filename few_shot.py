import json
import pandas as pd
import streamlit as st # Import streamlit if you want to use st.error or st.warning here

class FewShotPosts:
    def __init__(self, file_path="data/processed_posts.json"):
        self.df = None
        # Initialize unique_tags to an empty set (or list) to ensure it's always iterable
        self.unique_tags = set() # <--- CHANGE 1: Initialize as an empty set
        self.load_posts(file_path)

    def load_posts(self, file_path):
        try:
            with open(file_path, encoding='utf-8') as f:
                posts_data = json.load(f) # Renamed to avoid conflict with 'posts' later
            
            # Basic validation of the loaded data structure
            if not isinstance(posts_data, list) or not all(isinstance(item, dict) for item in posts_data):
                # If using streamlit, you can use st.error
                # st.error(f"Error: Expected '{file_path}' to contain a list of JSON objects.")
                print(f"Error: Expected '{file_path}' to contain a list of JSON objects.")
                # self.unique_tags will remain an empty set, which is fine
                return # Exit early if data structure is wrong

            df = pd.json_normalize(posts_data)

            # Validate required columns
            required_columns = ["line_count", "tags"]
            for col in required_columns:
                if col not in df.columns:
                    # If using streamlit, you can use st.error
                    # st.error(f"Error: Missing '{col}' column in data from '{file_path}'.")
                    print(f"Error: Missing '{col}' column in data from '{file_path}'.")
                    # self.unique_tags will remain an empty set
                    return # Exit early

            df['length'] = df['line_count'].apply(self.categorize_length)
            
            # Process tags more robustly
            all_tags_list = []
            for tags_entry in df['tags']:
                if isinstance(tags_entry, list): # Expecting each entry in 'tags' column to be a list
                    for tag in tags_entry:
                        if isinstance(tag, str): # Ensure individual tags are strings
                            all_tags_list.append(tag)
                # else: you might want to log a warning if an entry is not a list of strings

            if all_tags_list: # Check if any tags were actually collected
                self.unique_tags = set(all_tags_list)
            # If no tags are found, self.unique_tags remains the empty set it was initialized to.

            self.df = df
            # print(f"Successfully loaded and processed. Found tags: {self.unique_tags}") # For debugging

        except FileNotFoundError:
            # st.error(f"Error: File '{file_path}' not found.")
            print(f"Error: File '{file_path}' not found.")
            # self.unique_tags will remain an empty set
        except json.JSONDecodeError:
            # st.error(f"Error: File '{file_path}' is not a valid JSON.")
            print(f"Error: File '{file_path}' is not a valid JSON.")
            # self.unique_tags will remain an empty set
        except Exception as e:
            # st.error(f"An unexpected error occurred while loading posts: {e}")
            print(f"An unexpected error occurred while loading posts: {e}")
            # self.unique_tags will remain an empty set

    def categorize_length(self, line_count):
        if not isinstance(line_count, (int, float)): # Basic type check
            return "Unknown" # Or handle as an error
        if line_count < 7:
            return "Short"
        elif 7 <= line_count < 15:
            return "Medium"
        else:
            return "Long" # Corrected "long" to "Long" for consistency with your options

    def get_tags(self):
        # Return a list for st.selectbox, preferably sorted for consistent UI
        return sorted(list(self.unique_tags)) # <--- CHANGE 2: Ensure list output

    def get_filtered_posts(self, length, tag):
        if self.df is None:
            # st.warning("Data not loaded. Cannot filter posts.")
            print("Warning: Data not loaded. Cannot filter posts.")
            return [] # Return empty list if DataFrame isn't loaded

        # Ensure 'tags' column exists before trying to apply a lambda function to it
        if 'tags' not in self.df.columns:
            print("Warning: 'tags' column missing from DataFrame. Cannot filter by tag.")
            return []

        df_filtered = self.df[
            (self.df['length'] == length) &
            (self.df['tags'].apply(lambda tags_list: isinstance(tags_list, list) and tag in tags_list))
        ]
        return df_filtered.to_dict(orient='records')

# Example usage for testing the class itself
if __name__ == "__main__":
    # Create a dummy data/processed_posts.json for testing
    dummy_data = [
        {"title": "Post 1", "content_text": "Hello AI world", "line_count": 5, "tags": ["AI", "Intro"]},
        {"title": "Post 2", "content_text": "Medium post about Python", "line_count": 10, "tags": ["Python", "Development"]},
        {"title": "Post 3", "content_text": "A very long post on AI ethics and its implications.", "line_count": 20, "tags": ["AI", "Ethics", "Future"]},
        {"title": "Post 4", "content_text": "Short and sweet", "line_count": 3, "tags": ["General"]},
        {"title": "Post 5", "content_text": "Post with no tags", "line_count": 8, "tags": []}, # Post with empty tags list
        {"title": "Post 6", "content_text": "Post with malformed tags", "line_count": 6, "tags": "AI"}, # Malformed tag (string instead of list)
        {"title": "Post 7", "content_text": "Post missing tags field", "line_count": 6} # Missing tags field
    ]
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    with open("data/processed_posts.json", "w", encoding='utf-8') as f:
        json.dump(dummy_data, f, indent=2)

    fs = FewShotPosts() # Uses default "data/processed_posts.json"
    
    print("DataFrame columns:", fs.df.columns if fs.df is not None else "None")
    print("DataFrame head:\n", fs.df.head() if fs.df is not None else "None")
    
    tags_for_selectbox = fs.get_tags()
    print("Tags for selectbox:", tags_for_selectbox)
    print("Type of tags for selectbox:", type(tags_for_selectbox))

    if tags_for_selectbox: # Check if there are any tags to filter by
        posts = fs.get_filtered_posts('Short', 'AI')
        print("\nFiltered posts (Short, AI):")
        for post in posts:
            print(post)
    else:
        print("\nNo tags available to filter posts.")

    # Test with a non-existent file
    print("\n--- Testing with non-existent file ---")
    fs_non_existent = FewShotPosts(file_path="data/non_existent.json")
    print("Tags from non-existent file instance:", fs_non_existent.get_tags())

    # Test with a malformed JSON
    print("\n--- Testing with malformed JSON ---")
    with open("data/malformed.json", "w") as f:
        f.write("{'invalid_json': ")
    fs_malformed = FewShotPosts(file_path="data/malformed.json")
    print("Tags from malformed JSON instance:", fs_malformed.get_tags())
