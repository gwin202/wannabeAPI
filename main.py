import logging
from groq import Groq
from dotenv import load_dotenv  # Update this line
load_dotenv()
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import os
from supabase import create_client
import database
from fastapi.middleware.cors import CORSMiddleware


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


# Allow requests from http://localhost:8081
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081", os.environ.get("ALLOW_ORIGIN")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.post('/prompt')
async def api(body: database.UserInput):
    try:
        prompt_text = f"""
        Generate personalized career choice recommendations strictly from the following list of courses:

 1.⁠ ⁠Medicine and Surgery
 2.⁠ ⁠Law
 3.⁠ ⁠Civil Engineering
 4.⁠ ⁠Mechanical Engineering
 5.⁠ ⁠Electrical Engineering
 6.⁠ ⁠Computer Science
 7.⁠ ⁠Information Technology
 8.⁠ ⁠Business Administration
 9.⁠ ⁠Accounting
10.⁠ ⁠Nursing and Nursing Science
11.⁠ ⁠Agriculture
12.⁠ ⁠Mass Communication
13.⁠ ⁠Environmental Science
14.⁠ ⁠Education
15.⁠ ⁠Pharmacy

Consider the user's favourite tasks, soft skills, and technical skills to provide the most suitable recommendations. The user details are as follows:

Username: {body.username}
Favorite Tasks/Activities:  {body.task_activities}

Soft Skills:
  1. {body.softskill1}
  2. {body.softskill2}
  3. {body.softskill3}

Technical Skills:
  1.  {body.technical1}
  2. {body.technical2}
  3. {body.technical3}

Career choices:
 1.⁠ ⁠{body.career1}
 2.⁠ ⁠{body.career2}
 3.⁠ ⁠{body.career3}

Please analyze this information and recommend the top three most suitable courses from the given list. Additionally, provide a brief explanation for each recommendation, detailing why it aligns well with the username preferences and skills in 150 words only.
        """
    except Exception as e:
         print(e)
         raise HTTPException(status_code=422, detail="Unprocessable Entity")
    
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
    
@app.post('/addProfile')
async def addProfile(body: dict):
    try:
        userId = body['user_id']
        name = body['name']
        email = body['email']
        photoURL = body['photo_url']
        data, count = supabase.table('profiles').insert({
            "id": userId, 
            "displayName": name,
            "email": email,
            "photoURL": photoURL
        }).execute()
        return {"message": "User created successfully", "data": data, "count": count}
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error creating user")
        
    
@app.post('/get_user_details')
async def get_user_details(body: dict):
    try:
        jwt = body['accessToken']
        data = supabase.auth.get_user(jwt)
        user_data = {
            "id": data.user.id,
            "avatar_url": data.user.user_metadata['avatar_url'],
            "email": data.user.user_metadata['email'],
            "full_name": data.user.user_metadata['full_name']
        }
        
        return {"message": "Got user details Successfully", "data": user_data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error in getting user details")

@app.get('/get_user_info/{userId}')
async def get_user_info(userId: str):
    try:
        response, count = supabase.table('profiles').select('*, careers(*), softskills(*),technicalSkills(*)').eq('id',userId).execute()
        
        return {"data": response}
        
    except Exception as e:
        print(e)
        
@app.post('/get_descrip')
async def get_descrip(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
     write a brief description of the {body["career_name"]} course, highlighting its main focus and career paths.
     In not more than 100 words
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
@app.post('/get_scope')
async def get_scope(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
     What are the job prospects and scope of the {body["career_name"]} field in Nigeria, and what industries can graduates work in?
     In not more than 100 words
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
@app.post('/get_steps')
async def get_steps(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
    Outline the step-by-step process of pursuing a career in {body["career_name"]}, from education to professional certification.
    In not more than 100 words

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
@app.post('/get_top_uni')
async def get_top_uni(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
   List the top universities in Nigeria that offer {body["career_name"]} courses, including their location and program duration.
   In not more than 100 words

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
@app.post('/get_salary')
async def get_salary(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
   What is the average salary range per annum for {body["career_name"]} professionals in Nigeria, and how does experience affect salary? 
   In not more than 100 words

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

@app.post('/get_top_skills')
async def get_top_skills(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
        What are the essential skills required to succeed in the {body["career_name"]} field, and how can they be developed?
        In not more than 100 words

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

@app.post('/get_work_life')
async def get_work_life(body: dict):
    # Construct the prompt based on the provided data
    prompt_text = f"""
    What is the typical work-life balance like for {body["career_name"]} professionals, and how can they maintain a healthy balance between work and personal life?
    In not more than 100 words
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

@app.post('/addtechnicalSkills')
async def addTechnicalSkills(body: dict):
    try:
        
        technical1 = body["technical1"]
        technical2 = body["technical2"]
        technical3  = body["technical3"]
        userId = body["userId"]
        response = supabase.table('technicalSkills').select('id','*', count='exact').eq('userId', userId).execute()
        if response.count > 0:
            data, count = supabase.table('technicalSkills').update({
                "technical1": technical1, 
                "technical2": technical2,
                "technical3": technical3,
            }).eq('userId',userId).execute()
            return {"message": "Career Updated successfully", "data": data}
        else:
            data, count = supabase.table('technicalSkills').insert({
                "technical1": technical1, 
                "technical2": technical2,
                "technical3": technical3, 
                "userId": userId
            }).execute()
            return {"message": "Career added successfully", "data": data}
            
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error adding Technical Skill")
    
@app.post('/update_EducationLevel')
async def updatehighestEducationLevel(body: dict):
    try:
        userId = body['userId']
        highestEducationLevel = body['highestEducationLevel']
        who_are_you = body['who_are_you']
        data, count = supabase.table('profiles').update({"highestEducationLevel": highestEducationLevel, "who_are_you": who_are_you}).eq('id',userId).execute()
        return {"message": "Updated highestEducationLevel successfully","data": data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error updating user's highestEducationLevel")
    
@app.post("/updateActivities")
async def updateActivities(body: dict):
    try:
        
        userId = body['userId']
        activities = body['activities']
        data, count = supabase.table('profiles').update({"activities": activities}).eq('id',userId).execute()
        return {"message": "Updated Activities successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error updating user's Activities")
@app.post('/addSoftskill')
async def addSoftskill(body: dict):
    try:
        userId = body['userId']
        response = supabase.table('softskills').select('id','*', count='exact').eq('userId', userId).execute()
        
        # Check if the user already has softskills
        if  response.count > 0:
            softskill1 = body["softskill1"]
            softskill2 = body["softskill2"]
            softskill3 = body["softskill3"]
            
            data = supabase.table('softskills').update({
                "softskill1": softskill1,
                "softskill2": softskill2,
                "softskill3": softskill3,
            }).eq('userId', userId).execute()
            
            return {"message": "Updated softskill successfully", "data": data}
        else:
            
            softskill1 = body["softskill1"]
            softskill2 = body["softskill2"]
            softskill3 = body["softskill3"]
            
            data = supabase.table('softskills').insert({
                "softskill1": softskill1,
                "softskill2": softskill2,
                "softskill3": softskill3,
                "userId": userId
            }).execute()
            
            return {"message": "Added softskill successfully", "data": data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error in Adding Soft Skill")
    
@app.post('/addcareer')
async def addCareer(body: dict):
    try:
        career1 = body['career1']
        career2 = body['career2']
        career3 = body['career3']
        userId= body['userId']
        response = supabase.table('softskills').select('id','*', count='exact').eq('userId', userId).execute()
        if response.count > 0:
            
            data, count = supabase.table('careers').update({
                "career1": career1, 
                "career2": career2,
                "career3": career3, 
                
            }).eq("userId", userId).execute()
            return {"message": "Career Update successfully","data": data}
        else:
            data, count = supabase.table('careers').insert({
                "career1": career1, 
                "career2": career2,
                "career3": career3, 
                "userId": userId
            }).execute()
            return {"message": "Career added successfully","data": data}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error adding career")
          
        
if __name__ == '__main__':
    import uvicorn
    # Run the FastAPI app using Uvicorn on port 8003
    uvicorn.run(app, host="localhost", port=8003)