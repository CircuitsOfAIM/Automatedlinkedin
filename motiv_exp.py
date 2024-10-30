import json
import openai
from tinydb import TinyDB, Query as DBQuery
import re
from jinja2 import Environment, FileSystemLoader

API_KEY = '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'

MOTIV_TEMP = '''
Dear Hiring Manager, 
PARAGRAPH_1:[I am writing to express my enthusiasm for the [JOB_TITLE] position at [COMPANY_NAME], as advertised. Having a background in [MY_RELATED_BACKGROUND],I am eager to contribute to your team, particularly [RELEVANT_JOB_RESPONSIBILITIES]].
PARAGRAPH_2: THIS PARAGRAPH EXPLAINS WHY I APPLY FOR THIS JOB. ENTHUSIASM TO COMBINE THIS FIELD WITH RELATED AI DOMAINS AND BIONINFORMATIC (LIFE SCIENCE), WITH SOME EXAMPLES IN LIFE SCIENCE. [My deep fascination with [THE JOB SPECIFIC AREA, TECHNOLOGY AND DISCIPLINE], especially their transformative potential in life science and medicine, is a driving force behind my application for this role. Through my studies and experiences, I have been inspired by how these technologies can [A CREATE AND IMPACTFUL EXAMPLE OF APPLICATION OF JOB FIELD IN LIFE SCIENCE AND BIOINFORMATIC]. I am passionate about being at the forefront of this intersection between technology and life sciences, and I believe that this role and work being done on [COMPANY_NAME] will build up will provide knowledge and expertise to pursue this goal in my professional career.]
PARAGRAPH_3: THIS PARAGRAPH EXPLAINS MY  RELEVANT SKILLS AND EXPERIENCES, ITS RESULTS AS WELL AS MY OTHER SKILLS AND EXPERIENCES WITH THEIR BENEFITS[Throughout my academic journey and self-directed learning, I have actively involved to gain experience across a diverse range of topics, driven by a passion for learning and creating. I have tried to [MY RELEVANT SKILLS AND EXPERIENCES TO THIS JOB]. Additionally, [MY OTHER SKILLS AND EXPERIENCES] While these areas may not be directly related to the role, I believe they will enhance my ability to think creatively and apply transferable knowledge to my responsibilities, allowing me to approach challenges from fresh and innovative perspectives.]
PARAGRAPH_4:[I am particularly drawn to this opportunity at [COMPANY_NAME] because of your emphasis [COMPANIES GOAL AND PRODUCT] and the alignment to my personal future career goals. I am eager to bring all my knowledge and skills to your team, where I can contribute to ongoing projects and support the maintenance of existing products. Moreover, [COMPANY_CULTURE] enhancing my abilities while contributing to the success of your projects.]
PARAGRAPH_5:[Thank you for considering my application. I look forward to the opportunity to further discuss how I can contribute to the success of [COMPNAY_NAME].]
Sincerely,

Alireza Iranmanesh
'''
SYS_CONT_MOTIV = f'''
I provide you two documents: document_1, a job description I want to apply for and document 2, information regarding me. write a motivation letter based on the TEMPLATE. don't use determinisic tune.use probabilistic for example instead of "perfectly", use "may perfectly": 
TEMPLATE=[{MOTIV_TEMP}]
'''

SYS_CONT_CV = f'''
I provide you two information: info_1, a job description I want to apply for and inf_2, the list of my experiences. sort the experiences from most relevant and important to least. [IMPORTANT:RETURN THE SORTED LIST OF EXPEREINCE IDs in list (ARRAY).DON NOT RETURN ANYTHING ELSE].
'''

SELF_INFO= '''

EDUCATION:[[{"degree":"MSc","institution":"University of Göttingen","field":"Computational Biology and Bioinformatics","period":"Oct. 2023 - Present","courses":[{"title":"Models and Algorithms in Bioinformatics","description":"Study of computational models and algorithms used in bioinformatics for analyzing biological data."},{"title":"Machine Learning","description":"Exploration of machine learning techniques and their applications in various fields, including bioinformatics."},{"title":"Data-Science Infrastructure","description":"Tools, software, and concepts essential for running operations on data infrastructures."},{"title":"Structural Biochemistry","description":"Focus on biochemical structures, including cryoEM image processing and crystallography techniques."},{"title":"Neurobiology","description":"Study of the nervous system and brain functions, covering various aspects of neurobiology."}]},{"degree":"Pre-master","institution":"Radboud University","field":"AI: Intelligent Technology","period":"Sept. 2022 - Aug. 2023","GPA":"1.94/4","courses":[{"title":"Calculus","description":"Fundamentals of calculus, including differentiation and integration."},{"title":"Linear Algebra","description":"Study of vector spaces, matrices, and linear transformations."},{"title":"Deep Learning","description":"Techniques and architectures for training deep neural networks."},{"title":"AI Lab Skills","description":"Practical skills in AI, including pandas, numpy, basic data science, and reinforcement learning."},{"title":"Human-Computer Interaction","description":"Design and evaluation of user interfaces and experiences, including basic Unity game development."},{"title":"Cognitive Computational Neuroscience","description":"Seminars on current research in cognitive neuroscience and computational models of brain functions."}]},{"degree":"BSc","institution":"University of Mashhad","field":"Biology","period":"Sept. 2017 - Sept. 2022","GPA":"1.78/4 (German grading system)","courses":[{"title":"General Mathematics"},{"title":"General Chemistry"},{"title":"Chemistry Lab"},{"title":"Plant Anatomy and Morphology"},{"title":"Plant Morphology Lab"},{"title":"Fundamentals of Organic Chemistry (I)"},{"title":"Fundamentals of Biology"},{"title":"Principles and Methods of Plant Taxonomy"},{"title":"General Microbiology Lab"},{"title":"Fundamentals of Ecology Lab"},{"title":"Organic Chemistry Lab"},{"title":"General Microbiology"},{"title":"Fundamentals of Ecology"},{"title":"Biostatistics"},{"title":"Fundamentals of Geology"},{"title":"Laboratory Skills in Biology"},{"title":"Biochemistry Lab"},{"title":"Zoology Lab"},{"title":"Plant Systematics Lab"},{"title":"Plant Systematics"},{"title":"Fundamentals of Biochemistry"},{"title":"Zoology (I)"},{"title":"Thallophytes"},{"title":"Cell Biology Lab"},{"title":"Plant Systematics (II) Lab"},{"title":"Plant Physiology (I) Lab"},{"title":"Animal Physiology (I) Lab"},{"title":"Plant Systematics (II)"},{"title":"Cellular and Molecular Biology"},{"title":"Animal Physiology"},{"title":"Plant Physiology"},{"title":"Fundamentals of Genetics Lab"},{"title":"Fundamentals of Genetics"},{"title":"Radiobiology"},{"title":"Animal Histology Lab"},{"title":"Virology"},{"title":"Animal Histology"},{"title":"Plant Physiology (I)"},{"title":"Biotechnology"},{"title":"Plant Genetics and Breeding"},{"title":"Molecular Biology"},{"title":"Embryology Lab"},{"title":"Biophysics"},{"title":"Evolution"},{"title":"Embryology"},{"title":"Thesis"},{"title":"Medicinal Plants"},{"title":"Applied Ethics"}]}]
]

SKILLS=Programming Languages [Python (2/3), Java (1/3), C# (1/3), JavaScript (1/3), SQL (1/3), Bash (1.5/3)]; Web Development [HTML, CSS, MaterialUI, React(1/3, Flask(1.5/3)]; Scientific Computing [Numpy(2/3), Pytorch(2/3), Scikit-learn(1/3), Pandas(1.5/3), Matplotlib(1.5/3), Gym(0.5/3)]; Development Tools [Git(2/3), Linux(2/3), Unity (+ MRTK)(1/3), Balsamiq, Jira, Plastic SCM, Orange]; Databases [MySQL(1/3), SQLite(1/3), MongoDB(1/3)]; Soft Skills [Advanced English (C1), Creative thinking(3/3), Problem-solving(2/3), Communication(2/3), Collaboration(2/3), Agile(2/3)]; Transferable Skills [Fast Learner (introductory knowledge)(2/3), Adaptable (various tools)(2.5/3), Team Player (Scrum, development lifecycles)(2/3)]

EXPERIENCES=[{"_default":{"1":{"title":"Scrum Developer on Planon Software company","type":"experience","description":"Practical experience on development of indoor navigation for mixed reality glasses Hololens2.","technologies":["Unity","MRTK","C#","Git"],"id":1000},"2":{"title":"Minigames in Unity","type":"experience","description":"Getting familiar with Unity game engine and writing programs in C#. Developed two minigames, one similar to Fruit Ninja and another as a simple car driving game.","technologies":["Unity","C#","Visual Studio","Plastic scm"],"id":2000},"3":{"title":"Performing usability test controller choice in unity-based karting game","type":"experience","description":"Conducted a study to examine the usability of keyboard and mouse controls in Karting games, aiming to identify differences in effectiveness, efficiency, and user engagement.","technologies":["Unity","C#","MRTK","Python","Matplotlib"],"id":3000},"4":{"title":"ML models from scratch","type":"experience","description":"Implemented a Decision Tree model from scratch, trained and tested on the adult income dataset. Achieved accuracy similar to Scikit-learn's implementation after applying various preprocessing routines.","technologies":["Python","Numpy","Pandas"],"id":4000},"5":{"title":"Implementing Several Image classification and generator models","type":"experience","description":"Implemented data handling and preprocessing routines, generated tiny game characters using CNN-GANs, and performed image classification on CIFAR10 using multiple logistic regression, vanilla MLP, and LeNet5, comparing loss and accuracy.","technologies":["Python","Numpy","Pytorch","Jupyter Notebook"],"id":5000},"6":{"title":"Data Pre-processing on US presidential speeches","type":"experience","description":"Performed text preprocessing on US presidential speeches, including lowercasing, tokenization, stopword removal, and stemming. Analyzed the impact of these steps with word cloud visualizations.","technologies":["Python","Numpy","Pandas"],"id":6000},"7":{"title":"Generating Song Lyrics with Recurrent Neural Networks","type":"experience","description":"Developed a three-layer model with embedding, GRU, and linear layers, using CrossEntropyLoss and Adam optimizer to generate song lyrics in different styles from seed text.","technologies":["Python","Numpy","Pytorch","Jupyter Notebook"],"id":7000},"8":{"title":"Phylogenetics tree reconstruction for Rosa x binaloudensis (Rosaceae)","type":"experience","description":"Built an evolutionary tree for a new species using random forest for predicting candidate neighboring trees in SPR search method, achieving 95% correspondence to the original tree based on real log-likelihood values.","technologies":["Python","Numpy","Pandas","Scikit-learn","Ubuntu","Phyml","Raxml","Bioedit"],"id":8000},"9":{"title":"Full stack real estate web application development","type":"experience","description":"Developed a full-stack web application for real estate where users can register, authenticate, browse, create and edit property cases, and manage their profiles.","technologies":["HTML","CSS","Javascript","PHP","mySQL","MVP software architecture"],"id":9000},"10":{"title":"Minigame Maze Generator","type":"experience","description":"Developed a terminal-based maze solver game with a parameterized maze generation using a customized randomized Prim's algorithm. The project is modular and uses Git for version control.","technologies":["Python","Git","Bash Programming","Latex"],"id":10000},"11":{"title":"Design UI for Bitcoin wallet application","type":"experience","description":"Designed an interactive wireframe and visual design for a Bitcoin wallet application, focusing on color schemes, icons, and typography based on a low-fidelity prototype.","technologies":["Balsamiq","Canva","AdobeXD","Figma"],"id":11000},"12":{"title":"Utilizing the GWDG Scientific Compute Cluster (SCC)","type":"experience","description":"Gained experience in connecting via SSH, operating within the Linux shell, managing software environments with the module system and SPACK, and using the SLURM scheduler. Worked with various file systems across the cluster.","technologies":["Linux","Batch Scripting","Slurm"],"id":12000},"13":{"title":"Maze Generator","type":"experience","description":"Individual project for the course 'AI Lab Skills.' Implemented the Randomized Prim algorithm for creating a maze playground and solving it using different search algorithms.","technologies":["Randomized Prim's Algorithm","Maze Generation","Search Algorithms"],"id":13000},"14":{"title":"Evaluation of Different RL Algorithms in a Circular World","type":"experience","description":"Individual project for the course 'Reinforcement Learning.' Compared MDP, MC, and TD approaches for solving a task in a circular world.","technologies":["Reinforcement Learning","Markov Decision Process (MDP)","Monte Carlo (MC)","Temporal-Difference (TD)"],"id":14000}}}]

SOME_OF_THINGS_I_LIKE=[{"categories":{"OS_hardware_abstraction_level":{"examples":["Linux"]},"distributed_systems":{"examples":["GPUs","HPC"]},"art":{"subcategories":{"clothing":{},"art_galleries":{},"art_people":{},"art_communities":{}}},"performing_live_music":{"genres":["techno","electronic","rock"]},"math":{},"activities":{"running":{},"cooking":{},"walking":{}}}}
]

CERTIFICATES= [COURSES = [{"title": "Introduction to Brain and Cognitive Science Course", "institution": "Aren Center at Mashhad, Iran", "duration": "16 hours"}, {"title": "Advanced Course in Neuroscience", "institution": "Interdisciplinary School, Tehran, Iran", "duration": "15 hours"}, {"title": "Introduction to Machine Vision and Image Processing", "institution": "Interdisciplinary School, Tehran, Iran", "duration": "15 hours"}, {"title": "Web Senior (CIW Web Design-PHP & MySQL)", "institution": "i3Center Mashhad, Iran", "duration": "90 hours", "final_score": "740/1000"}]
]

SOME_OF_FAVOURITE_JOB_TITLES(RATE)=[{"ML Eng":"1/3","DL Eng":"2/3","NLP Eng":"2/3","Comp Ling":"1/3","Speech Rec Eng":"2/3","Conv AI Dev":"1/3","CV Eng":"2/3","Img Proc Eng":"2/3","Auto Veh Eng":"2/3","AR/VR Eng":"3/3","RL Eng":"3/3","Robotics Eng (RL)":"3/3","Game AI Dev":"2/3","AI Infra Eng":"2.5/3","MLOps Eng":"2.5/3","Cloud AI Eng":"2/3","Data Eng":"1.5/3","XAI Eng":"2/3","Edge AI Eng":"3/3","Emb AI Dev":"3/3","IoT AI Dev":"2.5/10","AI Firmware Eng":"3/10","Cog Comp Eng":"2/3","AI Sol Arch":"2.5/3","Human Aug Eng":"2.5/3","Bio-AI Dev":"2/3","Prec Med AI":"2/3","BCI Eng":"1.5/3","AI Design Eng":"2.5/3","Comp Des":"2/3","AgriTech AI":"2.5/3","Pers AI Dev":"2/3","Creative AI":"2.5/3","AI Sys Arch":"2.5/3"}]

PREFERED_JOB_LOCATION=[[ON_SITE]=Goettingen,[HYBRID and REMOTE]=anywhere in germany]

'''

SCROE_THRESHOLD = 60
NR_EXPERIENCES = 5
# Function to escape LaTeX special characters


def escape_latex(text):
    if isinstance(text, int):
        text = str(text)
    special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
        '|': r'\textbar{}',
    }
    regex = re.compile('|'.join(re.escape(key)
                                for key in special_chars.keys()))
    return regex.sub(lambda match: special_chars[match.group()], text)


def create_docs_direcotry(dir_path:str,job_id:str,company_name:str):
    '''directory for each specific jobs'''
    import os

    # Define the directory path you want to create
    directory_path = f'{dir_path}/{str.replace(j_data["company"]," ","")}_{job_id}'

    # Create the directory
    # exist_ok=True allows the directory to exist without raising an error
    os.makedirs(directory_path, exist_ok=True)

    print(f"dir '{directory_path}' created ")
    return directory_path

openai.api_key = API_KEY

db = TinyDB('db.json')
QUERY_OBJ = DBQuery()

# connecting to cv_db
cv_db = TinyDB('./cv_db.json')
CV_DATA = DBQuery()

DOCS_PATH = './doc_outputs'

# sorting responses based on score
score_ls = []
for res in (db.search((QUERY_OBJ.type == 'ai_res'))):
    if (res['state'] == 'todo') & ((int(res["choices"]["message"]["content"]["score"])) >= SCROE_THRESHOLD):
        score_ls.append({'res_id': res["job_id"], "score": int(
            res["choices"]["message"]["content"]["score"])})
sorted_score_ls = sorted(score_ls, key=lambda x: x['score'], reverse=True)


# creating motivation letter and CV for each sorted job
for job_score in sorted_score_ls:
    j_data = db.search((QUERY_OBJ.job_id == job_score["res_id"]) & (
        QUERY_OBJ.type == 'job_data'))[0]

    #creating directory for docs
    docs_dir = create_docs_direcotry(DOCS_PATH,j_data['job_id'],j_data['company'])

    # reequesting open AI for motiv letter
    res = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
            "role": "system", "content": SYS_CONT_MOTIV},
            {
                "role": "user",
                "content": f"DOCUMENT_1:[{j_data['title']}\n {j_data['job_description']}] \n DOCUMENT_2:[{SELF_INFO}]"
            }
        ]
    )
# # latex for motivation letter

    #store in a file (txt)
    with open(f'{docs_dir}/motiv_{str.replace(j_data["company"]," ","")}_{j_data["job_id"]}.tex','w') as file:

        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('template_motiv.tex')

        # Render the template with the dynamic content
        output = template.render(motiv_content=res.choices[0].message.content)
        file.write(output)

        print("LaTeX for motivation letter created.")

    # updating the state of job
    db.update({"state":"motiv_done"},(QUERY_OBJ.type == 'ai_res')&(QUERY_OBJ.job_id ==j_data["job_id"]))
    print('corresponding ai_res state updated')

    # =================================
    # CV EXPERIENCE SORTING
    experiences = cv_db.search(CV_DATA.type == 'experience')

    res_cv = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", "content": SYS_CONT_CV},
            {
                "role": "user",
                "content": f"INFO_1:[{j_data['title']}\n {j_data['job_description']}] \n info_2:[{experiences}]"
            }
        ]
    )


    # sorted and filterd by number of experience constanct
    sorted_exp_ids = json.loads(res_cv.choices[0].message.content)

    # updating the state of job
    db.update({"state": "cv_done"}, (QUERY_OBJ.type == 'ai_res')
              & (QUERY_OBJ.job_id == j_data["job_id"]))
    print('corresponding ai_res state updated')

    # latex for CV
    # reaaranging on order of experiences
    sorted_experiences = [next(item for item in experiences if item['id'] == exp_id)
                          for exp_id in sorted_exp_ids][:NR_EXPERIENCES]

    # handling special characters for both value types of string and list (like technologies)
    corrected_exp = [{key: [escape_latex(i) for i in value] if isinstance(
        value, list) else escape_latex(value) for key, value in exp.items()} for exp in sorted_experiences]

    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template_cv.tex')

    # Render the template with the dynamic content
    output = template.render(experiences_jinja=corrected_exp)

    # Write the output to a .tex file
    with open(f'{docs_dir}/cv_{str.replace(j_data["company"]," ","")}_{j_data["job_id"]}.tex', 'w') as f:
        f.write(output)

    print("LaTeX for CV created")

    #adding metadata
    with open(f'{docs_dir}/meta_{str.replace(j_data["company"]," ","")}_{j_data["job_id"]}.json','w') as f:
        meta={'url':j_data['job link'],'job_id':j_data['job_id']}
        json.dump(meta,f)