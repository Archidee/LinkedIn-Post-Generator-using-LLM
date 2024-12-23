import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from llm_helper import llm


def process_posts(raw_file_path,processed_file_path="data/processed_posts.json"):
    enriched_posts=[]
    with open(raw_file_path,encoding='utf-8') as file:
        posts=json.load(file)
        for post in posts:
            metadata=extract_metadata(post['text'])
            post_with_metadata= post | metadata
            enriched_posts.append(post_with_metadata)

    unified_tags= get_unified_tags(enriched_posts)

    for post in enriched_posts:
        current_tags=post['tags']
        new_tags={unified_tags[tag] for tag in current_tags}
        post['tags'] = list(new_tags)

    with open(processed_file_path,encoding='utf-8',mode='w') as outfile:
        json.dump(enriched_posts,outfile,indent=4)


def get_unified_tags ( posts_with_metadata):
    unique_tags = set()
    for post in posts_with_metadata :
        unique_tags.update(post['tags'])

    unique_tags_list=', '.join(unique_tags)   

    template=''' I will give you a list of tags. You need to uify tags with following requrements.
    1. Tags are unified and merged to create a shorter list
       Example 1: "Artificial Intelligence", "Machine Learning", "AI Software" can al be merged into a single term "AI"

       Example 2: "Startups", "Startup Funding", "entrepreneur" can be merged into single term "Entrepreneurship"

       Example 3: "Innovation", "Tech advancement", "Tech Discovery" can be mapped to "Tech Insights"

    2. Each tag should follow title case convention. Example : " Entrepreneurship", "Tech Insights".

    3. Output should be jason object , No preamble
    4. Output should have mapping of original tag and unifie tag.
     For example: {{"Artifical Intelligence ": " AI",  "AI Software": "AI", "Motivation": "Motivation" }}
    
    Here is the list of tags: 
    {tags}

    '''  
    pt=PromptTemplate.from_template(template)
    chain=pt|llm
    response=chain.invoke(input={'tags':str(unique_tags_list)})

    try:
        json_parser = JsonOutputParser()
        res=json_parser.parse(response.content)
    except OutputParserExemption:
        raise OutputParserExemption ( "unable to parse")
    
    

    return res
    for epost in enriched_posts:
        print(epost)


def extract_metadata(post):
    
    template='''
    You are given a LinkedIn post. You need to extract number of lines and tags.
    1. Return valid JSON. No Preamble.
    2.JSON should have exactly two keys : line_count, language and tags.
    3.tags is an array of text tags. Extract maximum of three tags.

    Here is the actual post on which you have to perform this task : 
    {post}

    '''
    pt= PromptTemplate.from_template(template)
    chain = pt | llm
    response=chain.invoke(input = {'post': post})
    
    try:
        json_parser=JsonOutputParser()
        res=json_parser.parse(response.content)
    except OutputParserExemption:
        raise OutputParserExemption ( "unable to parse")
    
    return res

if __name__=="__main__":
    process_posts("data/raw_posts.json","data/processed_posts.json")


