from pydantic import BaseModel
class TokenData(BaseModel):
    accessToken: str
    refresh_token: str
class UserInput(BaseModel):
    username: str
    task_activities: str
    softskill1: str
    softskill2: str
    softskill3: str
    technical1: str
    technical2: str
    technical3: str
    career1: str
    career2: str
    career3: str
class TechnicalSkills(BaseModel):
    userId: str
    technical1: str
    technical2: str
    technical3: str

class Skill(BaseModel):
    softskill1: str
    softskill2: str
    softskill3: str
    userId: str
class Career(BaseModel):
    userId: str
    career1: str
    career2: str
    career3: str
    
class profiles(BaseModel):
    User_id: str
    highestEducationLevel: str
    who_are_you: str