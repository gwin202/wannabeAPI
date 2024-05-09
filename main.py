import logging
from groq import Groq
from dotenv import load_dotenv  # Update this line
load_dotenv()
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
from supabase import create_client
import database



app = FastAPI()
# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.environ.get('API_KEY'))
groq_client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(url, key)

# # List available models
# models = client.models.list()

# for model in models:
#     print(model.id, '-',)

# Define a request model using Pydantic

@app.post('/prompt')
async def prompt(user_input: database.UserInput):
    # Construct the prompt based on the provided data
    prompt_text = f"{user_input.username}, a professional with a vibrant mind and a passion for {user_input.task_activities}, seeks your guidance, ChatGPT. Equipped with strong soft skills like {user_input.softskill1}, {user_input.softskill2}, and {user_input.softskill3}, enjoys applying these technical skills in {user_input.technical1}, {user_input.technical2}, and {user_input.technical3}. While my heart dances between the noble calling of {user_input.career1}, the captivating world of {user_input.career2}, and the intricacies of {user_input.career3} hold equal allure."
    
    # Make a request to OpenAI API to get the response
    try:
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt_text,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return {"response": response.choices[0]['text']}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error communicating with OpenAI API")

@app.post('/api')
async def api(user_input: database.UserInput):
    # Construct the prompt based on the provided data
    prompt_text = f"""{user_input.username}, a professional with a vibrant mind and a passion for {user_input.task_activities}, seeks your guidance. Equipped with strong soft skills like {user_input.softskill1}, {user_input.softskill2}, and {user_input.softskill3}, enjoys applying these technical skills in {user_input.technical1}, {user_input.technical2}, and {user_input.technical3}. While my heart dances between the noble calling of {user_input.career1}, the captivating world of {user_input.career2}, and the intricacies of {user_input.career3} hold equal allure.
    From the diverse landscape of courses available, Medicine and Surgery, Law, Civil Engineering, Mechanical Engineering, Electrical Engineering, Computer Science, Information Technology, Business Administration, Accounting, Nursing and Nursing Science, Agriculture, Mass Communication, Environmental Science, Education, and Pharmacy stand as potential pathways.

    Yet, the path that truly suits me needs to resonate with my unique blend of talents and aspirations. I seek not just a fulfilling career, but one that leverages his strengths, embraces my interests, and makes a meaningful impact on the world.

    Therefore, I turn to you, ChatGPT, to unveil the one courses that shine brightest for me. Guide me, not just by the compass of his initial choices, but by the map of real-life data. Lead us to where these skills find fertile ground, where my interests blossom, and where his future holds its most fulfilling promise.

    Remember, to give recommendations from the list of courses given.
    
    """
    
    try:
        chat_completion = groq_client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt_text}",
            }
        ],
        model="llama3-70b-8192",
        )
        return {"response": chat_completion.choices[0].message.content}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error communicating with Groq Api")
    
@app.post('/get_user_details')
async def get_user_details(data: database.TokenData):
    pass
@app.post('/addtechnicalSkills')
async def addTechnicalSkills(technicalSkills: database.TechnicalSkills):
    try:
        data, count = await supabase.table('technicalSkills').insert({
            "technical1": technicalSkills.technical1, 
            "technical2": technicalSkills.technical2,
            "technical3": technicalSkills.technical3, 
            "user_id": technicalSkills.userId
        }).execute()
        return {"message": "Career added successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error adding Technical Skill")
    
@app.post('/update_EducationLevel')
async def updatehighestEducationLevel(body: dict):
    try:
        userId = body['user_id']
        highestEducationLevel = body['highestEducationLevel']
        who_are_you = body['who_are_you']
        data, count = supabase.table('profiles').update({"highestEducationLevel": highestEducationLevel, "who_are_you": who_are_you}).eq('user_id',userId).execute()
        print(data,count)
        return {"message": "Updated highestEducationLevel successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error updating user's highestEducationLevel")
@app.post('/addSoftskill')
async def addSoftskill(userinput: database.Skill):
    try:
        data, count = supabase.table('profiles').insert({
            "softskill1": userinput.softskill1,
            "softskill2": userinput.softskill2,
            "softskill3": userinput.softskill3,
            "userId": userinput.userId
        })
        return {"message": "Added softskill successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error in Adding Soft Skill")
    
@app.post('/addcareer')
async def addCareer(addcareer: database.Career):
    try:
        data, count = supabase.table('career').insert({
            "career1": addcareer.career1, 
            "career2": addcareer.career2,
            "career3": addcareer.career3, 
            "user_id": addcareer.userId
        }).execute()
        return {"message": "Career added successfully"+data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error adding career")
            
        
if __name__ == '__main__':
    import uvicorn
    # Run the FastAPI app using Uvicorn on port 8003
    uvicorn.run(app, host="localhost", port=8003)