from  llm_helper import llm
from few_shot import FewShotPosts


few_shot=FewShotPosts()

def get_length_str(length):
    if length=="Short":
        return "1 to 7"
    elif length=="Medium":
        return "7 to 15"
    else:
        return "more than 15"

def get_prompt(length,tag):
    prompt= f'''
    Generate a linkedin post using the below informations. No preambles needed. 
    1)Topic: {tag}
    2)Length: {length}
    3)Language: English

 

    
    '''
    examples=few_shot.get_filtered_posts(length,tag)

    if len(examples)>0:
        prompt+="4) Use writing style as per the folling examples:\n"

        for i, post in enumerate(examples):
            post_text=post['text']
            prompt+=f"\n\n Example {i+1}: {post_text}\n"

            if i==2:
                break

    return prompt

def generate_post(tag,length):

    prompt= get_prompt(length,tag)
    response=llm.invoke(prompt)
    return response.content

if __name__=="__main__":
    post=generate_post("Short","AI")
    print(post)
    