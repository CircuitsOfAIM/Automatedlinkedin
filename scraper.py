import json
from tinydb import TinyDB, Query as DBQuery
from datetime import datetime
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters,OnSiteOrRemoteFilters, SalaryBaseFilters

#mode of searching with jobid
MODE_4JID = False

# Change root logger level (default is WARN)
logging.basicConfig(level=logging.INFO)


#retriving job ids from db
db = TinyDB('db.json')
j_data = DBQuery()
all_job_data = db.search(j_data.type=="job_data")
JOB_IDS =[jdata['job_id'] for jdata in all_job_data]


# called once for each successfully processed job
def on_data(data: EventData):
    job_id_ls = JOB_IDS

    #preventing repeated jobs
    if data.job_id in job_id_ls:
        return

    data_dict = {"type":"job_data","state":"todo","job_id":data.job_id,"title":data.title,"company":data.company,"URL":data.company_link,"date":data.date,"job link":data.link,"insight":data.insights,
    "job_description":data.description}
    try:
        db.insert(data_dict)
        print('job added to db')
    except:
        print('DB ERROR: something happened')


# Fired once for each page (25 jobs)
def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')


#event listeneres for the 4jid
def on_data_4jid(data: EventData):
    job_id = data.job_id.split(':')[-1]
    data_dict = {"type":"job_data","state":"todo","job_id":job_id,"title":data.title,"company":data.company,"date":data.date,"job link":JOB_PAGE_URL+job_id,"insight":data.insights,
    "job_description":data.description}
    try:
        db.insert(data_dict)
        print('job added to db')
    except:
        print('DB ERROR: something happened')

def on_metrics_4jid(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error_4jid(error):
    print('[ON_ERROR]', error)


def on_end_4jid():
    print('[ON_END]')

scraper = LinkedinScraper(
    chrome_executable_path="/usr/bin/chromedriver",  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_binary_location="/usr/bin/google-chrome",  # Custom path to Chrome/Chromium binary (e.g. /foo/bar/chrome-mac/Chromium.app/Contents/MacOS/Chromium)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=0.5,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=50  # Page load timeout (in seconds)    
)

queries = [
    Query(
        query='working student deep learning',
        options=QueryOptions(
            locations=['Germany'],
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            page_offset=0,  # How many pages to skip
            limit=30,
            filters=QueryFilters(
                # company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[
                TypeFilters.FULL_TIME,
                TypeFilters.PART_TIME,
                TypeFilters.CONTRACT,
                TypeFilters.INTERNSHIP
                ],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL,ExperienceLevelFilters.ASSOCIATE],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE,OnSiteOrRemoteFilters.HYBRID],
                # experience=[ExperienceLevelFilters.MID_SENIOR],
                # base_salary=SalaryBaseFilters.SALARY_100K
            )
        )
    ),
    Query(
        query='working student machine learning',
        options=QueryOptions(
            locations=['Germany'],
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            page_offset=0,  # How many pages to skip
            limit=30,
            filters=QueryFilters(
                # company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[
                TypeFilters.FULL_TIME,
                TypeFilters.PART_TIME,
                TypeFilters.CONTRACT,
                TypeFilters.INTERNSHIP
                ],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL,ExperienceLevelFilters.ASSOCIATE],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE,OnSiteOrRemoteFilters.HYBRID],
                # experience=[ExperienceLevelFilters.MID_SENIOR],
                # base_salary=SalaryBaseFilters.SALARY_100K
            )
        )
    ),    
    Query(
            query='working student Artificial Intelligence',
            options=QueryOptions(
                locations=['Germany'],
                apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
                skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
                page_offset=0,  # How many pages to skip
                limit=30,
                filters=QueryFilters(
                    # company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.MONTH,
                    type=[
                    TypeFilters.FULL_TIME,
                    TypeFilters.PART_TIME,
                    TypeFilters.CONTRACT,
                    TypeFilters.INTERNSHIP
                    ],
                    experience=[ExperienceLevelFilters.ENTRY_LEVEL,ExperienceLevelFilters.ASSOCIATE],
                    on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE,OnSiteOrRemoteFilters.HYBRID],
                    # experience=[ExperienceLevelFilters.MID_SENIOR],
                    # base_salary=SalaryBaseFilters.SALARY_100K
                )
            )
        ),
    Query(
        query='working student',
        options=QueryOptions(
            locations=['Germany'],
            apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
            skip_promoted_jobs=False,  # Skip promoted jobs. Default to False.
            page_offset=0,  # How many pages to skip
            limit=30,
            filters=QueryFilters(
                # company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                relevance=RelevanceFilters.RECENT,
                time=TimeFilters.MONTH,
                type=[
                TypeFilters.FULL_TIME,
                TypeFilters.PART_TIME,
                TypeFilters.CONTRACT,
                TypeFilters.INTERNSHIP
                ],
                experience=[ExperienceLevelFilters.ENTRY_LEVEL,ExperienceLevelFilters.ASSOCIATE],
                on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE,OnSiteOrRemoteFilters.HYBRID],
                # experience=[ExperienceLevelFilters.MID_SENIOR],
                # base_salary=SalaryBaseFilters.SALARY_100K
            )
        )
    ),
]

if not MODE_4JID:
    # Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    scraper.run(queries)


if MODE_4JID:
    job_ids = YAMLJOBID_LIST
    #event listeners for the 4jid
    scraper.on(Events.DATA, on_data_4jid)
    scraper.on(Events.ERROR, on_error_4jid)
    scraper.on(Events.END, on_end_4jid)

    scraper.run_4jid(job_ids)


