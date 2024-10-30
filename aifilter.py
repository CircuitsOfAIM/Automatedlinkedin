import json
import openai
from tinydb import TinyDB, Query as DBQuery

API_KEY ='API_KEY'

SYS_CONT = '''You are to assess the suitability of a candidate for a job based onthe provided job description and the candidate's brief information (from their CV and a questionnaire).Your task is to return a score between 0 and 100, which reflects how well the candidate matches the job requirements. IMPORTANT, if the job description specifies German (or anything rather English) Language requirements as mandatory and the candidate does not meet these, you must return a score of -1.'''

SELF_INFO= '''

EDUCATION:[[{"degree":"DEGREE","institution":"UNIVERSITY","field":"YOUR SUBJECT","period":"TIME","courses":[{"title":"COURESE TITLE","description":"DESCRIPTION."}]}]
]

SKILLS=Programming Languages [Python (2/3), Java (SCOURE/3),...]; Scientific Computing [Numpy(2/3), Pytorch(2/3), ...]; Development Tools [Git(2/3), Linux(2/3)...]; ...]

EXPERIENCES=[{"_default":{"1":{"title":"EXPERIENCE","type":"experience","description":"DESCRITPIOIN","technologies":[TECHNOLOGIES USED]}}]

SOME_OF_THINGS_I_LIKE =[{"categories":{"OS_hardware_abstraction_level":{"examples":["Linux"]},"distributed_systems":{"examples":["GPUs","HPC"]}}}]
]

CERTIFICATES= [...]

SOME_OF_MY_FAVOURITE_JOB_TITLES(RATE)=[...]

PREFERED_JOB_LOCATION=[...]

'''

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "extracted_data",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "score": {
                    "type": "string"
                },
                "description": {
                    "type": "string"
                }
            },
            "required": ["score", "description"],
            "additionalProperties": False
        }
    }
}

#retrive jobs data have not been sent to openai 
##having list of ids
db = TinyDB('db.json')
JOB_DATA = DBQuery()
todo_job_data_ls = db.search((JOB_DATA.type=='job_data') & (JOB_DATA.state=='todo'))

##getting descriptoin and title 
for j_data in todo_job_data_ls:
	print(f'PROCESSING:{j_data["job_id"]}')

	#request openai
	openai.api_key= API_KEY
	res = openai.chat.completions.create(
	    model="gpt-4o-mini",
	    messages=[
	        {
	        "role": "system", "content": SYS_CONT},
	        {
	            "role": "user",
	            "content": f"DOCUMENT 1:[{j_data['title']}\n{j_data['job_description']}] \n DOCUMENT 2:[{SELF_INFO}]"
	        }
	    ],
	    response_format=RESPONSE_FORMAT
	)

	res_json = {
	"job_id":j_data["job_id"],
	"chat_id":f"{res.id}",
	"choices":{
		"finish_reason":f"{res.choices[0].finish_reason}",
		"index":f"{res.choices[0].index}",
		"log_probs":f"{res.choices[0].logprobs}",
		"message":{
			"content":json.loads(res.choices[0].message.content),
			"refusal":f"{res.choices[0].message.refusal}",
			"role":f"{res.choices[0].message.role}",
			"function_call":f"{res.choices[0].message.function_call}",
			"tool_call":f"{res.choices[0].message.tool_calls}",
		}

	},
	"created":f"{res.created}",
	"model":f"{res.model}",
	"object":f"{res.object}",
	"chat_id":f"{res.id}",
	"service_tier":f"{res.service_tier}",
	"system_fingerprint":f"{res.system_fingerprint}",
	"usage":{
		"completion_tokens":f"{res.usage.completion_tokens}",
		"prompt_tokens":f"{res.usage.prompt_tokens}",
		"total_tokens":f"{res.usage.total_tokens}",
	},
	"state":"todo",
	"type":"ai_res"
	}
	#store the response json 
	db.insert(res_json)
	print('RESPONSE stored')

	#updating the state of job
	db.update({"state":"done"},(JOB_DATA.type == 'job_data')&(JOB_DATA.job_id ==j_data["job_id"]))
	print('job_data state updated')
