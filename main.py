# main.py
import streamlit as st
from few_shot import FewShotPosts # Assuming FewShotPosts is correctly defined elsewhere
from post_generator import generate_post # Assuming generate_post is correctly defined

length_options=["Short","Medium","Long"]


def main():
    st.title("LinkedIn Post generator")
    col1, col2, col3 = st.columns(3) # col3 is defined but not used, just an observation
    
    fs = FewShotPosts()
    tags = fs.get_tags() # <--- THIS IS THE LIKELY CULPRIT

    # --- DEBUGGING STEP ---
    # Let's see what 'tags' actually is:
    print(f"DEBUG: tags = {tags}")
    print(f"DEBUG: type(tags) = {type(tags)}")
    # You can also display this in Streamlit if you run it locally:
    # st.write(f"Debug: tags = {tags}")
    # st.write(f"Debug: type(tags) = {type(tags)}")
    # --- END DEBUGGING STEP ---

    # --- Defensive Programming: Ensure 'tags' is iterable ---
    # If 'tags' might be None or not a list/tuple, provide a default or handle it
    if not isinstance(tags, (list, tuple, set)):
        st.warning(f"Warning: `fs.get_tags()` returned a non-iterable type ({type(tags)}). Using default tags.")
        # Option 1: Provide default tags
        tags = ["Default Tag 1", "Default Tag 2", "No Tags Found"] 
        # Option 2: Or, if no tags means the selectbox shouldn't appear, you could conditionally render it
        # or display an error message. For now, let's use default tags.

    # Ensure tags are not empty, otherwise selectbox might look weird or error
    if not tags:
        tags = ["No tags available"]
    # --- End Defensive Programming ---

    with col1:
        # Now 'tags' should be a valid iterable
        selected_tag = st.selectbox("Tags", options=tags) 
    with col2:
        selected_length = st.selectbox("Length",options=length_options)
    
    if st.button("Generate Post"):
        # Make sure selected_tag is not one of your fallback values if that's an issue for generate_post
        if selected_tag in ["No Tags Found", "No tags available", "Default Tag 1", "Default Tag 2"]:
            st.error(f"Please ensure valid tags are available and selected. Current selection: {selected_tag}")
        else:
            post = generate_post(selected_length,selected_tag)
            st.write(post)

if __name__ == "__main__":
    main()
