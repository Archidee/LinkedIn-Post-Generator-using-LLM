import json
import pandas as pd
import os # Useful for path debugging

class FewShotPosts:
    def __init__(self, file_path="data/processed_posts.json"):
        self.df = None
        # Initialize unique_tags as an empty set.
        # This ensures get_tags() can always return an iterable.
        self.unique_tags = set()
        self.load_posts(file_path)

    def load_posts(self, file_path):
        # For debugging path issues, especially in Streamlit deployment
        # print(f"Attempting to load posts from: {os.path.abspath(file_path)}")
        # print(f"Current working directory: {os.getcwd()}")

        try:
            with open(file_path, encoding='utf-8') as f:
                posts_data = json.load(f) # Renamed to avoid conflict if 'posts' is a var name later

            df = pd.json_normalize(posts_data)

            # Validate essential columns
            if "line_count" not in df.columns:
                print(f"Error: Missing 'line_count' column in '{file_path}'. Cannot process posts.")
                # self.df remains None, self.unique_tags remains empty set
                return
            if "tags" not in df.columns:
                print(f"Error: Missing 'tags' column in '{file_path}'. Cannot extract tags.")
                # self.df will be assigned below, but tags processing will be skipped
                # Or you could 'return' here as well if tags are absolutely essential for df.
            
            df['length'] = df['line_count'].apply(self.categorize_length)

            # Robustly collect tags:
            # Assumes each entry in df['tags'] is a list of strings, or NaN/None
            if 'tags' in df.columns:
                all_tags_collected = []
                for tag_list_entry in df['tags'].dropna(): # dropna handles None/NaN gracefully
                    if isinstance(tag_list_entry, list):
                        for tag in tag_list_entry:
                            if isinstance(tag, str): # Ensure individual tags are strings
                                all_tags_collected.append(tag)
                self.unique_tags = set(all_tags_collected)
            # else: self.unique_tags remains an empty set (initialized in __init__)

            self.df = df # Assign the DataFrame only if essential columns are present and processed

        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found. Please check the path.")
            # self.df remains None, self.unique_tags remains empty set
        except json.JSONDecodeError:
            print(f"Error: File '{file_path}' is not a valid JSON. Please check the file content.")
            # self.df remains None, self.unique_tags remains empty set
        except Exception as e: # Catch other potential errors (e.g., from pandas operations)
            print(f"An unexpected error occurred while loading posts: {e}")
            # self.df remains None, self.unique_tags remains empty set

    def categorize_length(self, line_count):
        try:
            lc = int(line_count) # Ensure it's an integer
            if lc < 7:
                return "Short"
            elif 7 <= lc < 15:
                return "Medium"
            else:
                # Consistent capitalization with your length_options in main.py
                return "Long"
        except (ValueError, TypeError):
            # Handle cases where line_count might be non-numeric (e.g., None, string)
            print(f"Warning: Could not categorize length for line_count: {line_count}. Defaulting to 'Unknown'.")
            return "Unknown" # Or a sensible default

    def get_tags(self):
        # Always return a list for st.selectbox. Sorting provides UI consistency.
        return sorted(list(self.unique_tags))

    def get_filtered_posts(self, length, tag):
        if self.df is None or self.df.empty:
            print("DataFrame not loaded or empty. Cannot filter posts.")
            return []

        if not all(col in self.df.columns for col in ['length', 'tags']):
            print("DataFrame is missing 'length' or 'tags' column. Cannot filter posts.")
            return []

        # Ensure filtering against lists in 'tags' column
        df_filtered_list = self.df[
            (self.df['length'] == length) &
            (self.df['tags'].apply(lambda tags_in_post: isinstance(tags_in_post, list) and tag in tags_in_post))
        ]
        return df_filtered_list.to_dict(orient='records')

if __name__ == "__main__":
    # --- Test Scenarios ---
    # 1. Test with a non-existent file (should print FileNotFoundError)
    print("\n--- Test 1: Non-existent file ---")
    fs_non_existent = FewShotPosts(file_path="data/does_not_exist.json")
    print(f"Tags from non-existent file: {fs_non_existent.get_tags()}") # Should be []
    print(f"DataFrame from non-existent file is None: {fs_non_existent.df is None}")

    # 2. Create a dummy valid JSON file for testing
    dummy_data = [
        {"id": 1, "content": "Post 1", "line_count": 5, "tags": ["AI", "Python"]},
        {"id": 2, "content": "Post 2", "line_count": 10, "tags": ["Streamlit", "Python"]},
        {"id": 3, "content": "Post 3", "line_count": 20, "tags": ["AI", "Data"]},
        {"id": 4, "content": "Post 4", "line_count": "invalid", "tags": "not_a_list"}, # Test bad data
        {"id": 5, "content": "Post 5", "line_count": 6} # Missing 'tags' key
    ]
    dummy_file_path = "data/test_processed_posts.json"
    os.makedirs("data", exist_ok=True) # Ensure 'data' directory exists
    with open(dummy_file_path, 'w', encoding='utf-8') as f:
        json.dump(dummy_data, f)

    print(f"\n--- Test 2: Valid file ({dummy_file_path}) ---")
    fs_valid = FewShotPosts(file_path=dummy_file_path)
    print(f"Loaded DataFrame columns: {fs_valid.df.columns.tolist() if fs_valid.df is not None else 'None'}")
    print(f"Unique Tags: {fs_valid.get_tags()}") # Should be ['AI', 'Data', 'Python', 'Streamlit'] (sorted)

    if fs_valid.df is not None:
        print("\n--- Test 3: Filtering (with valid data) ---")
        short_ai_posts = fs_valid.get_filtered_posts('Short', 'AI')
        print(f"Short AI posts: {short_ai_posts}") # Should find one
        
        medium_python_posts = fs_valid.get_filtered_posts('Medium', 'Python')
        print(f"Medium Python posts: {medium_python_posts}") # Should find one

        long_data_posts = fs_valid.get_filtered_posts('Long', 'Data') # 'long' in categorize became 'Long'
        print(f"Long Data posts: {long_data_posts}") # Should find one

        # Test a tag that exists but not with this length
        short_streamlit_posts = fs_valid.get_filtered_posts('Short', 'Streamlit')
        print(f"Short Streamlit posts: {short_streamlit_posts}") # Should be empty

    # Clean up dummy file
    # os.remove(dummy_file_path)
    # print(f"\nCleaned up {dummy_file_path}")
