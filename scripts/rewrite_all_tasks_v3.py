"""
rewrite_all_tasks_v3.py
Master rewrite script: updates all task files and schemas for all 5 domains
using data/gold/by_task/<domain>3/ as ground truth.

Domains: jobs, realestate, academic, ecommerce, government
"""
import json, os, csv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(REPO, "data", "tasks")
SCHEMAS_DIR = os.path.join(REPO, "data", "schemas")

ORDERED_KEYS = [
    "task_id", "domain", "website_id", "website_name", "schema_id",
    "start_url", "sample_detail_url", "instruction",
    "requires_pagination", "requires_detail_page", "max_pages",
    "target_records", "difficulty", "verified_status",
    "verification_basis", "snapshot_required", "expected_fields",
]

def write_jsonl(path, tasks):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for t in tasks:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

def write_csv(path, tasks):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ORDERED_KEYS)
        writer.writeheader()
        for t in tasks:
            row = dict(t)
            row["expected_fields"] = json.dumps(row["expected_fields"])
            writer.writerow(row)

def build_task(base, schema_id, gold):
    t = {}
    for k in ORDERED_KEYS:
        if k == "schema_id":
            t[k] = schema_id
        elif k == "sample_detail_url":
            t[k] = gold.get("sample_detail_url")
        elif k == "target_records":
            t[k] = gold["count"]
        elif k == "expected_fields":
            t[k] = gold["fields"]
        elif k in base:
            t[k] = base[k]
        else:
            t[k] = None
    return t

# ============================================================
# JOBS
# ============================================================
JOBS_TASKS = [
    {"task_id":"WBV1_JOBS_REED_001_LISTING","domain":"Jobs","website_id":"reed","website_name":"Reed",
     "start_url":"https://www.reed.co.uk/jobs/it-jobs",
     "instruction":"Extract job postings from the Reed IT jobs listing page. For each job card, return job_title, company_name, location, employment_type if visible, salary if visible, company_logo_url if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_REED_002_DETAIL","domain":"Jobs","website_id":"reed","website_name":"Reed",
     "start_url":"https://www.reed.co.uk/jobs/it-jobs",
     "instruction":"Open a job posting from the Reed IT jobs listing and extract job_title, company_name, company_logo_url if available, location, employment_type, salary, job_description, about_the_role, about_you, benefits, how_to_apply, apply_url, job_id, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_POSTJOBFREE_001_LISTING","domain":"Jobs","website_id":"postjobfree","website_name":"Postjobfree",
     "start_url":"https://www.postjobfree.com/jobs?q=engineer",
     "instruction":"Extract job postings from PostJobFree search results for 'engineer'. For each job, return job_title, company_name, location, salary if visible, posted_date if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_POSTJOBFREE_002_DETAIL","domain":"Jobs","website_id":"postjobfree","website_name":"Postjobfree",
     "start_url":"https://www.postjobfree.com/jobs?q=engineer",
     "instruction":"Open a job listing from PostJobFree and extract job_title, job_id, company_name, company_overview, location, employment_type, work_arrangement, job_level, salary (structured), salary_min, salary_max, salary_currency, salary_period, job_description, responsibilities, required_qualifications, preferred_qualifications, benefits, physical_requirements, work_environment, equal_opportunity_statement, export_control_requirement, posted_date, apply_url, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_REMOTEOK_001_LISTING","domain":"Jobs","website_id":"remoteok","website_name":"Remoteok",
     "start_url":"https://remoteok.com/remote-dev-jobs",
     "instruction":"Extract remote developer job postings from RemoteOK. For each job, return job_title, company_name, company_logo_url if visible, location, salary if visible, apply_url if visible, tags if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":2,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_REMOTEOK_002_DETAIL","domain":"Jobs","website_id":"remoteok","website_name":"Remoteok",
     "start_url":"https://remoteok.com/remote-dev-jobs",
     "instruction":"Open a remote job posting from RemoteOK and extract job_title, company_name, company_logo_url, location, employment_type, salary, tags, skills, job_description, department, work_arrangement, apply_url, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_RELIEFWEB_001_LISTING","domain":"Jobs","website_id":"reliefweb","website_name":"Reliefweb",
     "start_url":"https://reliefweb.int/jobs",
     "instruction":"Extract humanitarian job postings from ReliefWeb. For each job, return job_title, company_name, country, application_deadline if visible, posted_date if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_RELIEFWEB_002_DETAIL","domain":"Jobs","website_id":"reliefweb","website_name":"Reliefweb",
     "start_url":"https://reliefweb.int/jobs",
     "instruction":"Open a job posting from ReliefWeb and extract job_title, company_name, location, posted_date, application_deadline, job_description, what_we_offer if available, years_of_experience if available, theme if available, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_EUROBRUSSELS_001_LISTING","domain":"Jobs","website_id":"eurobrussels","website_name":"Eurobrussels",
     "start_url":"https://www.eurobrussels.com",
     "instruction":"Extract EU affairs job postings from the EuroBrussels homepage. For each job, return job_title, company_name, location, salary if visible, application_deadline if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_EUROBRUSSELS_002_DETAIL","domain":"Jobs","website_id":"eurobrussels","website_name":"Eurobrussels",
     "start_url":"https://www.eurobrussels.com",
     "instruction":"Open a job posting from EuroBrussels and extract job_title, company_name, location, salary, apply_url, application_deadline, job_description, role_overview, about_company, requirements, benefits, application_procedure, tags, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_UNJOBS_001_LISTING","domain":"Jobs","website_id":"unjobs","website_name":"Unjobs",
     "start_url":"https://unjobs.org",
     "instruction":"Extract UN job postings from the UN Jobs listing page. For each job, return job_title, company_name, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_UNJOBS_002_DETAIL","domain":"Jobs","website_id":"unjobs","website_name":"Unjobs",
     "start_url":"https://unjobs.org",
     "instruction":"Open a UN job posting and extract job_title, company_name, location, employment_type, expected_start_date, application_deadline, qualifications, skills, responsibilities, language_requirements, visa_sponsorship, remuneration, duration, how_to_apply, competencies, assessment, payment_schedule_and_conditions, office, about_unu, about_office_institute, information_about_unu_rosters, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"hard",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_THTJOBS_001_LISTING","domain":"Jobs","website_id":"thtjobs","website_name":"thtjobs",
     "start_url":"https://www.timeshighereducation.com/unijobs/listings/academic-posts/",
     "instruction":"Extract academic job postings from Times Higher Education. For each job, return job_title, company_name, company_logo_url if visible, location, salary if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_THTJOBS_002_DETAIL","domain":"Jobs","website_id":"thtjobs","website_name":"thtjobs",
     "start_url":"https://www.timeshighereducation.com/unijobs/listings/academic-posts/",
     "instruction":"Open an academic job posting from Times Higher Education and extract job_title, company_name, company_logo_url, location, employment_type, hours, application_deadline, academic_discipline, job_type, apply_url, job_description, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_NATURECAREERS_001_LISTING","domain":"Jobs","website_id":"naturecareers","website_name":"Naturecareers",
     "start_url":"https://www.nature.com/naturecareers/jobs",
     "instruction":"Extract scientific job postings from Nature Careers. For each job, return job_title, company_name, location, salary if visible, job_description summary if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_NATURECAREERS_002_DETAIL","domain":"Jobs","website_id":"naturecareers","website_name":"Naturecareers",
     "start_url":"https://www.nature.com/naturecareers/jobs",
     "instruction":"Open a job posting from Nature Careers and extract job_title, company_name, location, salary, employment_type, employment_hours, application_deadline, job_type, discipline, sector, qualification, apply_url, job_description, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_GITHUB_001_LISTING","domain":"Jobs","website_id":"github","website_name":"github",
     "start_url":"https://github.com/about/careers",
     "instruction":"Extract job postings from GitHub Careers. For each job, return job_title, job_id if visible, location, work_arrangement if visible, categories if visible, apply_url if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_GITHUB_002_DETAIL","domain":"Jobs","website_id":"github","website_name":"github",
     "start_url":"https://github.com/about/careers",
     "instruction":"Open a GitHub job posting and extract job_title, job_id, location, employment_type, work_arrangement, job_level, category, compensation_range, overview, who_we_are, responsibilities, qualifications, job_description, about_github, github_values, leadership_principles, manager_fundamentals, eeo_statement, apply_url, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"hard",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_GOOGLE_001_LISTING","domain":"Jobs","website_id":"google","website_name":"google",
     "start_url":"https://careers.google.com/jobs/results/",
     "instruction":"Extract job postings from Google Careers search results. For each job, return job_title, company_name (Google), location, employment_type if visible, job_experience_level if visible, and job_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_JOBS_GOOGLE_002_DETAIL","domain":"Jobs","website_id":"google","website_name":"google",
     "start_url":"https://careers.google.com/jobs/results/",
     "instruction":"Open a Google Careers job posting and extract job_title, company_name, location, job_experience_level, salary_range if available, about_the_job, responsibilities, minimum_qualifications, preferred_qualifications, and job_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
]

JOBS_GOLD = {
    "WBV1_JOBS_REED_001_LISTING":         {"count":25, "sample_detail_url":"https://www.reed.co.uk/jobs/senior-developer/56875053?source=searchResults&filter=%2Fjobs%2Fdeveloper-jobs", "fields":["company_logo_url","company_name","employment_type","job_title","job_url","location","salary"]},
    "WBV1_JOBS_REED_002_DETAIL":          {"count":1,  "sample_detail_url":"https://www.reed.co.uk/jobs/junior-developer/57037836", "fields":["about_the_role","about_you","apply_url","benefits","company_logo_url","company_name","employment_type","how_to_apply","job_description","job_id","job_title","job_url","location","salary"]},
    "WBV1_JOBS_POSTJOBFREE_001_LISTING":  {"count":10, "sample_detail_url":"https://www.postjobfree.com/job/bwv490/mechanical-engineer-iii-santa-barbara-ca", "fields":["company_name","job_title","job_url","location","posted_date","salary"]},
    "WBV1_JOBS_POSTJOBFREE_002_DETAIL":   {"count":1,  "sample_detail_url":"https://www.postjobfree.com/job/bwv490/mechanical-engineer-iii-santa-barbara-ca", "fields":["apply_url","benefits","company_name","company_overview","employment_type","equal_opportunity_statement","export_control_requirement","job_description","job_id","job_level","job_title","job_url","location","physical_requirements","posted_date","preferred_qualifications","required_qualifications","responsibilities","salary","salary_currency","salary_max","salary_min","salary_period","work_arrangement","work_environment"]},
    "WBV1_JOBS_REMOTEOK_001_LISTING":     {"count":150,"sample_detail_url":"https://remoteok.com/remote-jobs/remote-events-marketing-manager-pivotal-health-1132436", "fields":["apply_url","company_logo_url","company_name","job_title","job_url","location","salary","tags"]},
    "WBV1_JOBS_REMOTEOK_002_DETAIL":      {"count":1,  "sample_detail_url":"https://remoteok.com/remote-jobs/remote-digital-solutions-specialist-newport-water-1132423", "fields":["apply_url","company_logo_url","company_name","department","employment_type","job_description","job_title","job_url","location","salary","skills","tags","work_arrangement"]},
    "WBV1_JOBS_RELIEFWEB_001_LISTING":    {"count":20, "sample_detail_url":"https://reliefweb.int/job/4215856/medical-doctor-gaza", "fields":["application_deadline","company_name","country","job_title","job_url","posted_date"]},
    "WBV1_JOBS_RELIEFWEB_002_DETAIL":     {"count":1,  "sample_detail_url":"https://reliefweb.int/job/4215856/medical-doctor-gaza", "fields":["application_deadline","company_name","job_description","job_title","job_url","location","posted_date","theme","what_we_offer","years_of_experience"]},
    "WBV1_JOBS_EUROBRUSSELS_001_LISTING": {"count":19, "sample_detail_url":"https://www.eurobrussels.com/job_display/291646/Public_Affairs_Consultant_EFC_European_Football_Clubs_Brussels_Belgium", "fields":["application_deadline","company_name","job_title","job_url","location","salary"]},
    "WBV1_JOBS_EUROBRUSSELS_002_DETAIL":  {"count":1,  "sample_detail_url":"https://www.eurobrussels.com/job_display/291628/Senior_Communications_Officer_REScoopeu_Brussels_Belgium", "fields":["about_company","application_procedure","apply_url","benefits","company_name","job_description","job_title","job_url","location","requirements","role_overview","salary","tags"]},
    "WBV1_JOBS_UNJOBS_001_LISTING":       {"count":25, "sample_detail_url":"https://unjobs.org/vacancies/1779896650956", "fields":["company_name","job_title","job_url"]},
    "WBV1_JOBS_UNJOBS_002_DETAIL":        {"count":1,  "sample_detail_url":"https://unjobs.org/vacancies/1778623830833", "fields":["about_office_institute","about_unu","application_deadline","assessment","competencies","company_name","duration","employment_type","expected_start_date","how_to_apply","information_about_unu_rosters","job_description","job_title","job_url","language_requirements","location","office","payment_schedule_and_conditions","qualifications","remuneration","responsibilities","skills","visa_sponsorship"]},
    "WBV1_JOBS_THTJOBS_001_LISTING":      {"count":21, "sample_detail_url":"https://www.timeshighereducation.com/unijobs/listing/408414/global-search-for-excellence-the-90-scholars-for-90th-anniversary-strategic-hiring-scheme/?LinkSource=TopJob", "fields":["company_logo_url","company_name","job_title","job_url","location","salary"]},
    "WBV1_JOBS_THTJOBS_002_DETAIL":       {"count":1,  "sample_detail_url":"https://www.timeshighereducation.com/unijobs/listing/408414/global-search-for-excellence-the-90-scholars-for-90th-anniversary-strategic-hiring-scheme/", "fields":["academic_discipline","application_deadline","apply_url","company_logo_url","company_name","employment_type","hours","job_description","job_title","job_type","job_url","location"]},
    "WBV1_JOBS_NATURECAREERS_001_LISTING":{"count":20, "sample_detail_url":"https://www.nature.com/naturecareers/job/12860948/-associate-senior-editor-nature-communications-human-behaviour-/?LinkSource=PremiumListing", "fields":["company_name","job_description","job_title","job_url","location","salary"]},
    "WBV1_JOBS_NATURECAREERS_002_DETAIL": {"count":1,  "sample_detail_url":"https://www.nature.com/naturecareers/job/12859405/full-professorship-w3-for-biochemistry-f-m-d-/?LinkSource=PremiumListing", "fields":["application_deadline","apply_url","company_name","discipline","employment_hours","employment_type","job_description","job_title","job_type","job_url","location","qualification","salary","sector"]},
    "WBV1_JOBS_GITHUB_001_LISTING":       {"count":10, "sample_detail_url":None, "fields":["apply_url","categories","job_id","job_title","job_url","location","work_arrangement"]},
    "WBV1_JOBS_GITHUB_002_DETAIL":        {"count":1,  "sample_detail_url":None, "fields":["about_github","apply_url","category","compensation_range","eeo_statement","employment_type","github_values","job_description","job_id","job_level","job_title","job_url","leadership_principles","location","manager_fundamentals","overview","qualifications","responsibilities","who_we_are","work_arrangement"]},
    "WBV1_JOBS_GOOGLE_001_LISTING":       {"count":20, "sample_detail_url":"https://www.google.com/about/careers/applications/jobs/results/137691136725525190-director-business-intelligence", "fields":["company_name","employment_type","job_experience_level","job_title","job_url","location","qualifications"]},
    "WBV1_JOBS_GOOGLE_002_DETAIL":        {"count":1,  "sample_detail_url":None, "fields":["about_the_job","company_name","job_experience_level","job_title","job_url","location","minimum_qualifications","preferred_qualifications","responsibilities","salary_range"]},
}

def assign_jobs_schema(tid):
    return "job_posting_detail_v1" if "_002_DETAIL" in tid else "job_posting_listing_v1"

jobs_all = [build_task(b, assign_jobs_schema(b["task_id"]), JOBS_GOLD[b["task_id"]]) for b in JOBS_TASKS]
jobs_dev_ids = {"WBV1_JOBS_REED_001_LISTING","WBV1_JOBS_REED_002_DETAIL","WBV1_JOBS_POSTJOBFREE_001_LISTING","WBV1_JOBS_POSTJOBFREE_002_DETAIL"}
jobs_dev  = [t for t in jobs_all if t["task_id"] in jobs_dev_ids]
jobs_test = [t for t in jobs_all if t["task_id"] not in jobs_dev_ids]

write_jsonl(os.path.join(TASKS_DIR, "jobs_all_tasks_20.jsonl"), jobs_all)
write_jsonl(os.path.join(TASKS_DIR, "jobs_dev_tasks_4.jsonl"),  jobs_dev)
write_jsonl(os.path.join(TASKS_DIR, "jobs_test_tasks_16.jsonl"), jobs_test)
write_csv(os.path.join(TASKS_DIR, "jobs_all_tasks_20.csv"), jobs_all)
print(f"JOBS: all={len(jobs_all)} dev={len(jobs_dev)} test={len(jobs_test)}")

# ============================================================
# REAL ESTATE
# ============================================================
RE_TASKS = [
    {"task_id":"WBV1_REAL_RIGHTMOVE_001_LISTING","domain":"Real Estate","website_id":"rightmove","website_name":"Rightmove",
     "start_url":"https://www.rightmove.co.uk",
     "instruction":"Extract property listings from Rightmove search results. For each property card, return address, price, property_type, bedrooms, bathrooms if visible, description if visible, published_date if visible, listing_agent info if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_RIGHTMOVE_002_DETAIL","domain":"Real Estate","website_id":"rightmove","website_name":"Rightmove",
     "start_url":"https://www.rightmove.co.uk",
     "instruction":"Open a property page from Rightmove and extract address, price, property_type, bedrooms, bathrooms, key_features, description, furnish_type if visible, has_parking if visible, published_date, listing_agent_logo, listing_office, listing_agent_location, rating, review_count, reviews if visible, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_DAFT.IE_001_LISTING","domain":"Real Estate","website_id":"daft.ie","website_name":"Daft.ie",
     "start_url":"https://www.daft.ie",
     "instruction":"Extract property listings from Daft.ie search results. For each card, return address, price, property_type, bedrooms, bathrooms if visible, floor_area if visible, energy_rating if visible, listing_agent info if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_DAFT.IE_002_DETAIL","domain":"Real Estate","website_id":"daft.ie","website_name":"Daft.ie",
     "start_url":"https://www.daft.ie",
     "instruction":"Open a property page from Daft.ie and extract address, price, property_type, bedrooms, bathrooms, floor_area, energy_rating, key_features, description, sale_type, published_date, ber_number, estimated_stamp_duty, schools, transport, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_FINN_EIENDOM_001_LISTING","domain":"Real Estate","website_id":"finn_eiendom","website_name":"Finn eiendom",
     "start_url":"https://www.finn.no/realestate/homes/search.html",
     "instruction":"Extract property listings from Finn Eiendom search results. For each card, return listing_title, address, price, total_price if visible, property_type, bedrooms if visible, floor_area if visible, monthly_fees if visible, tenure if visible, open_house_schedule if visible, listing_office if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_FINN_EIENDOM_002_DETAIL","domain":"Real Estate","website_id":"finn_eiendom","website_name":"Finn eiendom",
     "start_url":"https://www.finn.no/realestate/homes/search.html",
     "instruction":"Open a property page from Finn Eiendom and extract listing_title, address, price, total_price, joint_debt, joint_wealth, additional_costs, property_type, bedrooms, floor_area, internal_area, land_area, rooms, room_layout, floor_level, energy_rating, monthly_fees, price_assessment, description, year_built, published_date, listing_id, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_APARTMENTS_001_LISTING","domain":"Real Estate","website_id":"apartments.com","website_name":"Apartments",
     "start_url":"https://www.apartments.com/san-francisco-ca/",
     "instruction":"Extract property listings from Apartments.com San Francisco. For each card, return address, price, property_type, bedrooms, bathrooms, floor_area if visible, parking if visible, mls_number if visible, listing_agent if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_APARTMENTS_002_DETAIL","domain":"Real Estate","website_id":"apartments.com","website_name":"Apartments",
     "start_url":"https://www.apartments.com/the-landing-san-francisco-ca/q9q57k2/",
     "instruction":"Open a property page from Apartments.com and extract all available property details including address, price, property_type, bedrooms, bathrooms, floor_area, lot size fields, year_built, garage, heating_type, appliances, interior/exterior features, rooms, parking, school_district, schools, listing_agent, listing_office, status, sale_type, mls_number, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"hard",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_REDFIN_001_LISTING","domain":"Real Estate","website_id":"redfin","website_name":"Redfin",
     "start_url":"https://www.redfin.com/city/30749/CA/San-Francisco",
     "instruction":"Extract property listings from Redfin San Francisco search results. For each card, return price, bedrooms, bathrooms if visible, floor_area if visible, key_features if visible, open_house_schedule if visible, listing_agent if visible, images_urls if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_REDFIN_002_DETAIL","domain":"Real Estate","website_id":"redfin","website_name":"Redfin",
     "start_url":"https://www.redfin.com/city/30749/CA/San-Francisco",
     "instruction":"Open a property page from Redfin and extract price, property_type, floor_area, land_area if available, year_built if available, status, description, property_details, public_record, around_this_home, listing_agent, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_MAROC_ANNONCES_001_LISTING","domain":"Real Estate","website_id":"maroc_annonces","website_name":"Maroc annonces",
     "start_url":"https://www.marocannonces.com/maroc/immobilier-casablanca-b309-t556.html",
     "instruction":"Extract property listings from Maroc Annonces Casablanca. For each card, return listing_title, address, price, property_type, published_date if visible, images_urls if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_MAROC_ANNONCES_002_DETAIL","domain":"Real Estate","website_id":"maroc_annonces","website_name":"Maroc annonces",
     "start_url":"https://www.marocannonces.com/maroc/immobilier-casablanca-b309-t556.html",
     "instruction":"Open a property page from Maroc Annonces and extract listing_title, listing_id, address, price, floor_area, bathrooms, rooms, description, published_date, listing_agent_name, listing_agent_phone, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_REALESTATE.CO.NZ_001_LISTING","domain":"Real Estate","website_id":"realestate.co.nz","website_name":"Realestate.co.nz",
     "start_url":"https://www.realestate.co.nz/residential/sale",
     "instruction":"Extract property listings from realestate.co.nz. For each card, return listing_title, address, price, sale_type, property_type, bedrooms, bathrooms if visible, floor_area if visible, listing_agent info if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL","domain":"Real Estate","website_id":"realestate.co.nz","website_name":"Realestate.co.nz",
     "start_url":"https://www.realestate.co.nz/residential/sale",
     "instruction":"Open a property page from realestate.co.nz and extract address, price, bedrooms, bathrooms, floor_area, land_area if available, parking if available, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_ONTHEMARKET_001_LISTING","domain":"Real Estate","website_id":"onthemarket","website_name":"Onthemarket",
     "start_url":"https://www.onthemarket.com/for-sale/property/uk/",
     "instruction":"Extract property listings from OnTheMarket UK. For each card, return address, price, property_type, bedrooms, bathrooms if visible, key_features if visible, listing_agent info if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_ONTHEMARKET_002_DETAIL","domain":"Real Estate","website_id":"onthemarket","website_name":"Onthemarket",
     "start_url":"https://www.onthemarket.com/for-sale/property/uk/",
     "instruction":"Open a property page from OnTheMarket and extract listing_title, address, price, property_type, bedrooms, bathrooms, floor_area, key_features, energy_rating, council_tax, nearest_stations, mobile_signal, area_statistics, property_information, about_agent, listing_agent details, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_CENTURY_21_001_LISTING","domain":"Real Estate","website_id":"century_21","website_name":"Century 21",
     "start_url":"https://www.century21.com/real-estate/san-francisco-ca/LCASANFRANCISCO/",
     "instruction":"Extract property listings from Century 21 San Francisco. For each card, return address, price, bedrooms, bathrooms if visible, floor_area if visible, status if visible, open_house_schedule if visible, mls_number if visible, listing_agent if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_CENTURY_21_002_DETAIL","domain":"Real Estate","website_id":"century_21","website_name":"Century 21",
     "start_url":"https://www.century21.com/real-estate/san-francisco-ca/LCASANFRANCISCO/",
     "instruction":"Open a property page from Century 21 and extract address, price, property_type, bedrooms, bathrooms, floor_area, building_area, land_area, year_built, status, published_date, garage, parking, heating, water, flooring, roof, appliances, amenities, kitchen_description, foundation_description, monthly_fees, price_per_area, listing_id, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_LEBONCOIN_001_LISTING","domain":"Real Estate","website_id":"leboncoin","website_name":"Leboncoin",
     "start_url":"https://www.leboncoin.fr/cl/ventes_immobilieres/cp_ch%C3%A2tillon_92320",
     "instruction":"Extract property listings from Leboncoin real estate. For each card, return address, price, price_per_m2 if visible, property_type, rooms if visible, floor_area if visible, energy_rating if visible, additional_facilities if visible, listing_office if visible, images_urls if visible, and listing_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_REAL_LEBONCOIN_002_DETAIL","domain":"Real Estate","website_id":"leboncoin","website_name":"Leboncoin",
     "start_url":"https://www.leboncoin.fr/cl/ventes_immobilieres/cp_ch%C3%A2tillon_92320",
     "instruction":"Open a property page from Leboncoin and extract listing_title, address, price, price_per_m2, property_type, rooms, bedrooms, bathrooms, floor_area, energy_rating, greenhouse_gas_rating, heating_type, heating_mode, monthly_fees, characteristics, description, listing_agent, listing_agent_logo, images_urls, and listing_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
]

RE_GOLD = {
    "WBV1_REAL_RIGHTMOVE_001_LISTING":       {"count":25,  "sample_detail_url":"https://www.rightmove.co.uk/properties/89583912#/?channel=RES_BUY", "fields":["address","bathrooms","bedrooms","description","images_urls","listing_agent","listing_agent_logo","listing_agent_phone","listing_url","price","property_type","published_date"]},
    "WBV1_REAL_RIGHTMOVE_002_DETAIL":        {"count":1,   "sample_detail_url":"https://www.rightmove.co.uk/properties/146059961", "fields":["address","bathrooms","bedrooms","description","furnish_type","has_parking","images_urls","key_features","listing_agent_location","listing_agent_logo","listing_office","listing_url","price","property_type","published_date","rating","review_count","reviews"]},
    "WBV1_REAL_DAFT.IE_001_LISTING":         {"count":20,  "sample_detail_url":"https://www.daft.ie/for-sale/12-knightsbrook-crescent-trim-co-meath/6595237", "fields":["address","bathrooms","bedrooms","energy_rating","floor_area","images_urls","listing_agent","listing_agent_logo","listing_agent_name","listing_agent_photo","listing_url","price","property_type"]},
    "WBV1_REAL_DAFT.IE_002_DETAIL":          {"count":1,   "sample_detail_url":"https://www.daft.ie/for-sale/14-riverwood-place-castleknock-dublin-15/6550113", "fields":["address","bathrooms","bedrooms","ber_number","description","energy_rating","estimated_stamp_duty","floor_area","key_features","listing_url","price_per_m2","property_type","published_date","sale_type","satellite_view_url","schools","street_view_url","transport"]},
    "WBV1_REAL_FINN_EIENDOM_001_LISTING":    {"count":51,  "sample_detail_url":"https://www.finn.no/realestate/homes/ad.html?finnkode=464659921", "fields":["address","bedrooms","floor_area","images_urls","listing_agent_logo","listing_office","listing_title","listing_url","monthly_fees","open_house_schedule","price","property_type","tenure","total_price"]},
    "WBV1_REAL_FINN_EIENDOM_002_DETAIL":     {"count":1,   "sample_detail_url":"https://www.finn.no/realestate/homes/ad.html?finnkode=465141868", "fields":["additional_costs","address","bedrooms","description","energy_rating","floor_area","floor_level","images_urls","internal_area","joint_debt","joint_wealth","land_area","listing_id","listing_title","listing_url","monthly_fees","price_assessment","property_type","published_date","room_layout","rooms","total_price","year_built"]},
    "WBV1_REAL_APARTMENTS_001_LISTING":      {"count":24,  "sample_detail_url":"https://www.coldwellbankerhomes.com/ca/san-francisco/899-40th-ave/pid_71927566/", "fields":["address","bathrooms","bathrooms_partial","bedrooms","floor_area","images_urls","listing_agent","listing_url","mls_number","parking","price","property_type"]},
    "WBV1_REAL_APARTMENTS_002_DETAIL":       {"count":1,   "sample_detail_url":"https://www.apartments.com/the-landing-san-francisco-ca/q9q57k2/", "fields":["address","apn","appliances","architectural_style","assoc_fee_freq","assoc_name","association","association_fee","basement_desc","bathroom_features","bathrooms","bedroom_1","bedrooms","county","cross_streets","current_bldg_use","dining_room","district","exterior_features","fencing_description","fireplace","fireplaces","floor_area","flooring","for_sale","foundation","full_bathrooms","garage","half_bathrooms","heating_type","hoa_fee","hoa_fee_freq","images_urls","interior_features","kitchen","laundry","listing_agent","listing_office","lot_features","lot_size_acres","lot_size_sq_ft","mls_number","number_of_fireplaces","number_of_rooms","parking","parking_features","price","price_sales_history","primary_bathroom","primary_bedroom","property_type","property_view","road_maintenance","roof","rooms_areas","sale_type","school_district","schools","special_conditions","status","street_road_desc","tax_history","utility_description","water","year_built"]},
    "WBV1_REAL_REDFIN_001_LISTING":          {"count":41,  "sample_detail_url":"https://www.redfin.com/NY/Bayside/21404-33rd-Ave-11361/home/20835511", "fields":["bathrooms","bedrooms","floor_area","images_urls","key_features","listing_agent","listing_url","open_house_schedule","price"]},
    "WBV1_REAL_REDFIN_002_DETAIL":           {"count":1,   "sample_detail_url":"https://www.redfin.com/NY/Bronx/2749-Fish-Ave-10469/home/44736662", "fields":["around_this_home","description","floor_area","images_urls","land_area","listing_agent","listing_url","price","property_details","property_type","public_record","status","year_built"]},
    "WBV1_REAL_MAROC_ANNONCES_001_LISTING":  {"count":20,  "sample_detail_url":"https://www.marocannonces.com/categorie/315/Appartements/annonce/10387457/Vend-joli-appart-Maarif.html", "fields":["address","images_urls","listing_title","listing_url","price","property_type","published_date"]},
    "WBV1_REAL_MAROC_ANNONCES_002_DETAIL":   {"count":1,   "sample_detail_url":"https://www.marocannonces.com/categorie/315/Appartements/annonce/10387457/Vend-joli-appart-Maarif.html", "fields":["address","bathrooms","description","floor_area","images_urls","listing_agent_name","listing_agent_phone","listing_id","listing_title","listing_url","price","published_date","rooms"]},
    "WBV1_REAL_REALESTATE.CO.NZ_001_LISTING":{"count":14,  "sample_detail_url":"https://www.realestate.co.nz/43058090/residential/sale/9-woodham-place-rototuna-north", "fields":["address","bathrooms","bedrooms","floor_area","images_urls","listing_agent_logo","listing_agent_name","listing_agent_photo","listing_office","listing_title","listing_url","price","property_type","sale_type"]},
    "WBV1_REAL_REALESTATE.CO.NZ_002_DETAIL": {"count":1,   "sample_detail_url":"https://www.realestate.co.nz/property/12b-mary-street-papanui-christchurch-city-canterbury/m1fv7m7sc", "fields":["address","bathrooms","bedrooms","floor_area","images_urls","land_area","listing_url","parking","price"]},
    "WBV1_REAL_ONTHEMARKET_001_LISTING":     {"count":30,  "sample_detail_url":"https://www.onthemarket.com/details/19328039/", "fields":["address","bathrooms","bedrooms","images_urls","key_features","listing_agent_logo","listing_agent_phone","listing_office","listing_url","price","property_type"]},
    "WBV1_REAL_ONTHEMARKET_002_DETAIL":      {"count":1,   "sample_detail_url":"https://www.onthemarket.com/details/19547756/", "fields":["about_agent","address","area_statistics","bathrooms","bedrooms","council_tax","energy_rating","floor_area","images_urls","key_features","listing_agent","listing_agent_logo","listing_agent_phone","listing_agent_website","listing_title","listing_url","mobile_signal","nearest_stations","price","property_information","property_type"]},
    "WBV1_REAL_CENTURY_21_001_LISTING":      {"count":300, "sample_detail_url":"https://www.century21.com/homes/detail/ca/san-francisco/160-noe-st/lid-P00800000HBefcSWXRC1B0KXXzmuHK6fTxoqoUkF", "fields":["address","bathrooms","bedrooms","floor_area","images_urls","listing_agent","listing_url","mls_number","open_house_schedule","price","status"]},
    "WBV1_REAL_CENTURY_21_002_DETAIL":       {"count":1,   "sample_detail_url":"https://www.century21.com/homes/detail/ca/foster-city/516-saint-vincent-ln/lid-P00800000HBedlsr85sXbFx0cqjVggkXDKwuEsSx", "fields":["address","amenities","appliances","bathrooms","bedrooms","building_area","floor_area","flooring","foundation_description","garage","heating","images_urls","kitchen_description","land_area","listing_id","listing_url","monthly_fees","parking","price","price_per_area","property_type","published_date","roof","status","water","year_built"]},
    "WBV1_REAL_LEBONCOIN_001_LISTING":       {"count":35,  "sample_detail_url":"https://www.leboncoin.fr/ad/ventes_immobilieres/3051337441", "fields":["additional_facilities","address","energy_rating","floor_area","images_urls","listing_agent_logo","listing_office","listing_url","price","price_per_m2","property_type","rooms"]},
    "WBV1_REAL_LEBONCOIN_002_DETAIL":        {"count":1,   "sample_detail_url":"https://www.leboncoin.fr/ad/ventes_immobilieres/3201084037", "fields":["address","bathrooms","bedrooms","characteristics","description","energy_rating","floor_area","greenhouse_gas_rating","heating_mode","heating_type","images_urls","listing_agent","listing_agent_logo","listing_title","monthly_fees","price","price_per_m2","property_type","rooms"]},
}

def assign_re_schema(tid):
    return "real_estate_detail_v1" if "_002_DETAIL" in tid else "real_estate_listing_v1"

re_all = [build_task(b, assign_re_schema(b["task_id"]), RE_GOLD[b["task_id"]]) for b in RE_TASKS]
re_dev_ids = {"WBV1_REAL_RIGHTMOVE_001_LISTING","WBV1_REAL_RIGHTMOVE_002_DETAIL","WBV1_REAL_DAFT.IE_001_LISTING","WBV1_REAL_DAFT.IE_002_DETAIL"}
re_dev  = [t for t in re_all if t["task_id"] in re_dev_ids]
re_test = [t for t in re_all if t["task_id"] not in re_dev_ids]

write_jsonl(os.path.join(TASKS_DIR, "realestate_all_tasks_20.jsonl"), re_all)
write_jsonl(os.path.join(TASKS_DIR, "realestate_dev_tasks_4.jsonl"),  re_dev)
write_jsonl(os.path.join(TASKS_DIR, "realestate_test_tasks_16.jsonl"), re_test)
write_csv(os.path.join(TASKS_DIR, "realestate_all_tasks_20.csv"), re_all)
print(f"REALESTATE: all={len(re_all)} dev={len(re_dev)} test={len(re_test)}")

# ============================================================
# ACADEMIC
# ============================================================
ACAD_TASKS = [
    {"task_id":"WBV1_ACAD_MIT_EVENTS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"mit_events","website_name":"Mit events",
     "start_url":"https://calendar.mit.edu",
     "instruction":"Extract event listings from the MIT Events Calendar. For each event, return event_name, event_start_date, event_end_date if visible, location, cost if visible, image_url if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_MIT_EVENTS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"mit_events","website_name":"Mit events",
     "start_url":"https://calendar.mit.edu",
     "instruction":"Open event detail pages from the MIT Events Calendar and extract event_name, event_start_date, event_end_date, location, description, event_type, cost, contact, registration_url, organizer, accessibility, other_dates, website if available, image_url, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_STANFORD_EVENTS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"stanford_events","website_name":"Stanford events",
     "start_url":"https://events.stanford.edu",
     "instruction":"Extract event listings from Stanford Events. For each event, return event_name, event_start_date, event_end_date if visible, location, event_type if visible, register_url if visible, additional_option if visible, image_url if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_STANFORD_EVENTS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"stanford_events","website_name":"Stanford events",
     "start_url":"https://events.stanford.edu",
     "instruction":"Open event detail pages from Stanford Events and extract event_name, event_start_date, event_end_date, location, event_type, description, cost if available, contact if available, speaker if available, register_url, website if available, image_url, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_CERN_INDICO_001_LISTING","domain":"Academic / Events / Conferences","website_id":"cern_indico","website_name":"Cern indico",
     "start_url":"https://indico.cern.ch",
     "instruction":"Extract event listings from CERN Indico. For each event, return event_name, event_start_date, description if visible, location if visible, name_of_responsable if visible, faculty_schoole_departement if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_CERN_INDICO_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"cern_indico","website_name":"Cern indico",
     "start_url":"https://indico.cern.ch",
     "instruction":"Open event detail pages from CERN Indico and extract event_name, event_start_date, event_end_date, location, description, chairpersons, names_of_organizers, email, register_link, invited_participants, materials, sponsors, hotel, optional_excursions, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_GRC_MEETINGS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"grc_meetings","website_name":"Grc meetings",
     "start_url":"https://www.grc.org/meetings-and-conferences/",
     "instruction":"Extract conference listings from Gordon Research Conferences. For each conference, return event_name, subtitle if visible, event_start_date, event_end_date if visible, location, image_url if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_GRC_MEETINGS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"grc_meetings","website_name":"Grc meetings",
     "start_url":"https://www.grc.org/meetings-and-conferences/",
     "instruction":"Open conference detail pages from GRC and extract event_name, subtitle, event_start_date, event_end_date, location, chairs, vice_chairs, venue_and_travel_information, apply_link, grc_label, grc_education_requirements, image_url, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_IMPERIAL_EVENTS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"imperial_events","website_name":"Imperial events",
     "start_url":"https://www.imperial.ac.uk/events",
     "instruction":"Extract event listings from Imperial College London events. For each event, return event_name, event_start_date, event_end_date if visible, location, event_type if visible, timing_start if visible, timing_end if visible, description if visible, image_url if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_IMPERIAL_EVENTS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"imperial_events","website_name":"Imperial events",
     "start_url":"https://www.imperial.ac.uk/events",
     "instruction":"Open event detail pages from Imperial College London and extract event_name, event_start_date, event_end_date, location, event_type, timing_start, timing_end, description, cost if available, contact if available, registration_url if available, image_url, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_10TIMES_001_LISTING","domain":"Academic / Events / Conferences","website_id":"10times","website_name":"10times",
     "start_url":"https://10times.com/events",
     "instruction":"Extract event listings from 10times. For each event, return event_name, event_start_date, event_end_date if visible, location, description if visible, organizer if visible, topic if visible, visitors_count if visible, rating if visible, edition if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_10TIMES_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"10times","website_name":"10times",
     "start_url":"https://10times.com/events",
     "instruction":"Open event detail pages from 10times and extract event_name, event_start_date, event_end_date, location, description, organizer, topic, rating, rating_count, edition, exhibitors_count, image_urls, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_UNESCO_EVENTS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"unesco_events","website_name":"Unesco events",
     "start_url":"https://www.unesco.org/en/events",
     "instruction":"Extract event listings from UNESCO Events. For each event, return event_name, event_start_date, event_end_date if visible, location, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_UNESCO_EVENTS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"unesco_events","website_name":"Unesco events",
     "start_url":"https://www.unesco.org/en/events",
     "instruction":"Open event detail pages from UNESCO Events and extract event_name, event_start_date, event_end_date, location, event_type, arrangement_type, organized_by, rooms if available, register_url if available, speaker if available, description, image_url, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_CONFERENCEALERTS_001_LISTING","domain":"Academic / Events / Conferences","website_id":"conferencealerts","website_name":"Conferencealerts",
     "start_url":"https://conferencealerts.com",
     "instruction":"Extract conference listings from Conference Alerts. For each conference, return event_name, acronym if visible, event_start_date, event_end_date if visible, location, participation_type if visible, edition if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_CONFERENCEALERTS_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"conferencealerts","website_name":"Conferencealerts",
     "start_url":"https://conferencealerts.com",
     "instruction":"Open conference detail pages from Conference Alerts and extract event_name, acronym, participation_type, event_start_date, event_end_date, location, edition, description, organizer, contact_person, website, abstract_deadline, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_EVENTBRITE_SCITECH_001_LISTING","domain":"Academic / Events / Conferences","website_id":"eventbrite_scitech","website_name":"Eventbrite scitech",
     "start_url":"https://www.eventbrite.com/d/online/science-and-tech--events",
     "instruction":"Extract event listings from Eventbrite Science & Tech. For each event, return event_name, event_start_date, price if visible, organizer_name if visible, image_url if visible, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_EVENTBRITE_SCITECH_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"eventbrite_scitech","website_name":"Eventbrite scitech",
     "start_url":"https://www.eventbrite.com/d/online/science-and-tech--events",
     "instruction":"Open event detail pages from Eventbrite and extract event_name, event_start_date, event_end_date, event_start_time, event_end_time, location, organizer, description, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_ALLCONFERENCEALERT_001_LISTING","domain":"Academic / Events / Conferences","website_id":"allconferencealert","website_name":"All Conference Alert",
     "start_url":"https://www.allconferencealert.com/engineering-and-technology.html",
     "instruction":"Extract academic engineering conference listings from All Conference Alert. For each conference, return event_name, event_start_date, location, and event_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ACAD_ALLCONFERENCEALERT_002_DETAIL","domain":"Academic / Events / Conferences","website_id":"allconferencealert","website_name":"All Conference Alert",
     "start_url":"https://www.allconferencealert.com/engineering-and-technology.html",
     "instruction":"Open conference detail pages from All Conference Alert and extract event_name, event_start_date, event_end_date, location, description, organizer, email, website, abstract_deadline, registration_fee, register_link, rating, rating_count, organizing_committee, keynote_speakers, and event_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
]

ACAD_GOLD = {
    "WBV1_ACAD_MIT_EVENTS_001_LISTING":             {"count":10, "sample_detail_url":"https://calendar.mit.edu/event/food-truck-wednesdays", "fields":["cost","event_end_date","event_name","event_start_date","event_url","image_url","location"]},
    "WBV1_ACAD_MIT_EVENTS_002_DETAIL":              {"count":1,  "sample_detail_url":"https://calendar.mit.edu/event/food-truck-wednesdays", "fields":["accessibility","contact","cost","description","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","organizer","other_dates","registration_url","website"]},
    "WBV1_ACAD_STANFORD_EVENTS_001_LISTING":        {"count":12, "sample_detail_url":"https://events.stanford.edu/event/burt-and-deedee-mcmurtry-lecture-with-curator-hamza-walker", "fields":["additional_option","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","register_url"]},
    "WBV1_ACAD_STANFORD_EVENTS_002_DETAIL":         {"count":1,  "sample_detail_url":"https://events.stanford.edu/event/burt-and-deedee-mcmurtry-lecture-with-curator-hamza-walker", "fields":["contact","cost","description","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","register_url","speaker","website"]},
    "WBV1_ACAD_CERN_INDICO_001_LISTING":            {"count":10, "sample_detail_url":"https://indico.cern.ch/event/429043/", "fields":["description","event_name","event_start_date","event_url","faculty_schoole_departement","location","name_of_responsable"]},
    "WBV1_ACAD_CERN_INDICO_002_DETAIL":             {"count":1,  "sample_detail_url":"https://indico.cern.ch/event/1639790/", "fields":["chairpersons","description","email","event_end_date","event_name","event_start_date","event_url","hotel","invited_participants","location","materials","names_of_organizers","optional_excursions","register_link","sponsors"]},
    "WBV1_ACAD_GRC_MEETINGS_001_LISTING":           {"count":25, "sample_detail_url":"https://www.grc.org/additive-manufacturing-of-soft-materials-conference/2026/", "fields":["event_end_date","event_name","event_start_date","event_url","image_url","location","subtitle"]},
    "WBV1_ACAD_GRC_MEETINGS_002_DETAIL":            {"count":1,  "sample_detail_url":"https://www.grc.org/additive-manufacturing-of-soft-materials-conference/2026/", "fields":["apply_link","chairs","event_end_date","event_name","event_start_date","event_url","grc_education_requirements","grc_label","image_url","location","subtitle","venue_and_travel_information","vice_chairs"]},
    "WBV1_ACAD_IMPERIAL_EVENTS_001_LISTING":        {"count":24, "sample_detail_url":"https://www.imperial.ac.uk/events/209153/great-exhibition-road-festival-2026/", "fields":["description","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","timing_end","timing_start"]},
    "WBV1_ACAD_IMPERIAL_EVENTS_002_DETAIL":         {"count":1,  "sample_detail_url":"https://www.imperial.ac.uk/events/209153/great-exhibition-road-festival-2026/", "fields":["contact","cost","description","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","registration_url","timing_end","timing_start"]},
    "WBV1_ACAD_10TIMES_001_LISTING":                {"count":40, "sample_detail_url":"https://10times.com/plast-packprint-ethiopia", "fields":["description","edition","event_end_date","event_name","event_start_date","event_url","location","organizer","rating","topic","visitors_count"]},
    "WBV1_ACAD_10TIMES_002_DETAIL":                 {"count":1,  "sample_detail_url":"https://10times.com/plast-packprint-ethiopia", "fields":["description","edition","event_end_date","event_name","event_start_date","event_url","exhibitors_count","image_urls","location","organizer","rating","rating_count","topic"]},
    "WBV1_ACAD_UNESCO_EVENTS_001_LISTING":          {"count":20, "sample_detail_url":"https://www.unesco.org/en/event/session-3-ecosystems-climate-and-adaptive-strategies-building-climate-resilience-gender-", "fields":["event_end_date","event_name","event_start_date","event_url","location"]},
    "WBV1_ACAD_UNESCO_EVENTS_002_DETAIL":           {"count":1,  "sample_detail_url":"https://www.unesco.org/en/articles/thought-leaders-series-le-nguyen-hoang", "fields":["arrangement_type","description","event_end_date","event_name","event_start_date","event_type","event_url","image_url","location","organized_by","register_url","rooms","speaker"]},
    "WBV1_ACAD_CONFERENCEALERTS_001_LISTING":       {"count":100,"sample_detail_url":"https://conferencealerts.com/show-event?id=274920", "fields":["acronym","edition","event_end_date","event_name","event_start_date","event_url","location","participation_type"]},
    "WBV1_ACAD_CONFERENCEALERTS_002_DETAIL":        {"count":1,  "sample_detail_url":"https://conferencealerts.com/show-event?id=274920", "fields":["abstract_deadline","acronym","contact_person","description","edition","event_end_date","event_name","event_start_date","event_url","location","organizer","participation_type","website"]},
    "WBV1_ACAD_EVENTBRITE_SCITECH_001_LISTING":     {"count":30, "sample_detail_url":"https://www.eventbrite.com/e/get-started-algo-bot-trading-101-tickets-1990019024472?aff=ebdssbcategorybrowse", "fields":["event_name","event_start_date","event_url","image_url","organizer_name","price"]},
    "WBV1_ACAD_EVENTBRITE_SCITECH_002_DETAIL":      {"count":1,  "sample_detail_url":"https://www.eventbrite.com/e/get-started-algo-bot-trading-101-tickets-1990019024472", "fields":["description","event_end_date","event_end_time","event_name","event_start_date","event_start_time","event_url","location","organizer"]},
    "WBV1_ACAD_ALLCONFERENCEALERT_001_LISTING":     {"count":57, "sample_detail_url":"https://www.allconferencealert.com/event/2553709", "fields":["event_name","event_start_date","event_url","location"]},
    "WBV1_ACAD_ALLCONFERENCEALERT_002_DETAIL":      {"count":1,  "sample_detail_url":"https://www.allconferencealert.com/event/2553709", "fields":["abstract_deadline","description","email","event_end_date","event_name","event_start_date","event_url","keynote_speakers","location","organizer","organizing_committee","rating","rating_count","register_link","registration_fee","website"]},
}

def assign_acad_schema(tid):
    return "academic_event_detail_v1" if "_002_DETAIL" in tid else "academic_event_listing_v1"

acad_all = [build_task(b, assign_acad_schema(b["task_id"]), ACAD_GOLD[b["task_id"]]) for b in ACAD_TASKS]
acad_dev_ids = {"WBV1_ACAD_MIT_EVENTS_001_LISTING","WBV1_ACAD_MIT_EVENTS_002_DETAIL","WBV1_ACAD_STANFORD_EVENTS_001_LISTING","WBV1_ACAD_STANFORD_EVENTS_002_DETAIL"}
acad_dev  = [t for t in acad_all if t["task_id"] in acad_dev_ids]
acad_test = [t for t in acad_all if t["task_id"] not in acad_dev_ids]

write_jsonl(os.path.join(TASKS_DIR, "academic_all_tasks_20.jsonl"), acad_all)
write_jsonl(os.path.join(TASKS_DIR, "academic_dev_tasks_4.jsonl"),  acad_dev)
write_jsonl(os.path.join(TASKS_DIR, "academic_test_tasks_16.jsonl"), acad_test)
write_csv(os.path.join(TASKS_DIR, "academic_all_tasks_20.csv"), acad_all)
print(f"ACADEMIC: all={len(acad_all)} dev={len(acad_dev)} test={len(acad_test)}")

# ============================================================
# ECOMMERCE
# ============================================================
ECOM_TASKS = [
    {"task_id":"WBV1_ECOM_01_IKEA_US_LISTING","domain":"E-commerce / Products","website_id":"ikea_us","website_name":"IKEA US",
     "start_url":"https://www.ikea.com/us/en/cat/sofas-sectionals-fu003/",
     "instruction":"Extract product listings from the IKEA sofas and sectionals category page. For each product, return product_name, short_description if visible, price_raw, currency, old_price_raw if on sale, discount_percentage if on sale, rating if visible, review_count if visible, brand, availability if visible, category if visible, seller_name if visible, color if visible, color_options if visible, image_url, and product_url.",
     "requires_pagination":False,"requires_detail_page":False,"max_pages":1,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_01_IKEA_US_DETAIL","domain":"E-commerce / Products","website_id":"ikea_us","website_name":"IKEA US",
     "start_url":"https://www.ikea.com/us/en/cat/sofas-armchairs-700640/",
     "instruction":"Open a product page from IKEA and extract product_name, price_raw, currency, old_price_raw if on sale, discount_percentage if on sale, seller_name, description, brand, color, size_or_volume if visible, rating, review_count, sku if visible, shipping_text if visible, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_02_NIKE_US_LISTING","domain":"E-commerce / Products","website_id":"nike_us","website_name":"Nike US",
     "start_url":"https://www.nike.com/w/mens-shoes-nik1zy7ok",
     "instruction":"Extract product listings from the Nike men's shoes page. For each product, return product_name, product_subtitle if visible, price_raw, old_price_raw if on sale, color_options if visible, image_url, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_02_NIKE_US_DETAIL","domain":"E-commerce / Products","website_id":"nike_us","website_name":"Nike US",
     "start_url":"https://www.nike.com/w/mens-shoes-nik1zy7ok",
     "instruction":"Open a product page from Nike and extract product_name, price_raw, description, available_colors if visible, fit if available, style_color if available, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_03_CASPER_US_LISTING","domain":"E-commerce / Products","website_id":"casper_us","website_name":"Casper US",
     "start_url":"https://casper.com/collections/mattresses",
     "instruction":"Extract mattress product listings from Casper. For each product, return product_name, short_description if visible, price_raw, old_price_raw if on sale, discount_percentage if on sale, rating, review_count, image_url, and product_url.",
     "requires_pagination":False,"requires_detail_page":False,"max_pages":1,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_03_CASPER_US_DETAIL","domain":"E-commerce / Products","website_id":"casper_us","website_name":"Casper US",
     "start_url":"https://casper.com/collections/mattresses",
     "instruction":"Open a product page from Casper and extract product_name, price_raw, old_price_raw, discount_percentage, brand, description, rating, review_count, available_sizes if visible, foam_model if visible, measurements if visible, materials if visible, first_review if visible, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_04_WARBYPARKER_US_LISTING","domain":"E-commerce / Products","website_id":"warbyparker_us","website_name":"Warby Parker",
     "start_url":"https://www.warbyparker.com/eyeglasses",
     "instruction":"Extract eyeglasses listings from Warby Parker. For each product, return product_name, price_raw, color_name if visible, available_colors if visible, available_widths if visible, rating if visible, review_count if visible, image_url, image_urls if visible, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_04_WARBYPARKER_US_DETAIL","domain":"E-commerce / Products","website_id":"warbyparker_us","website_name":"Warby Parker",
     "start_url":"https://www.warbyparker.com/eyeglasses",
     "instruction":"Open a product page from Warby Parker and extract product_name, price_raw, color_name, short_description, selected_width, available_colors, available_widths, rating, review_count, first_review_title, first_review_content, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_05_DECATHLON_US_LISTING","domain":"E-commerce / Products","website_id":"decathlon_us","website_name":"Decathlon",
     "start_url":"https://www.decathlon.com/collections/all-hiking-backpacks",
     "instruction":"Extract hiking backpack listings from Decathlon. For each product, return product_name, brand if visible, price_raw, old_price_raw if on sale, discount_percentage if on sale, currency, color if visible, color_options if visible, rating if visible, review_count if visible, availability if visible, short_description if visible, category if visible, seller_name if visible, image_url, and product_url.",
     "requires_pagination":False,"requires_detail_page":False,"max_pages":1,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_05_DECATHLON_US_DETAIL","domain":"E-commerce / Products","website_id":"decathlon_us","website_name":"Decathlon",
     "start_url":"https://www.decathlon.com/collections/all-hiking-backpacks",
     "instruction":"Open a product page from Decathlon and extract product_name, brand, price_raw, description, color, color_options, capacity_or_size if available, key_features if available, sku if available, rating, review_count, first_review_title, first_review_content, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_06_JUMIA_EGYPT_LISTING","domain":"E-commerce / Products","website_id":"jumia_egypt","website_name":"Jumia Egypt",
     "start_url":"https://www.jumia.com.eg/mobile-phones/",
     "instruction":"Extract mobile phone listings from Jumia Egypt. For each product, return product_name, brand if visible, price_raw, old_price_raw if on sale, discount_percentage if on sale, currency, rating if visible, review_count if visible, availability if visible, short_description if visible, seller_name if visible, color if visible, color_options if visible, image_url, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_06_JUMIA_EGYPT_DETAIL","domain":"E-commerce / Products","website_id":"jumia_egypt","website_name":"Jumia Egypt",
     "start_url":"https://www.jumia.com.eg/mobile-phones/",
     "instruction":"Open a product page from Jumia Egypt and extract product_name, brand, price_raw, old_price_raw, discount_percentage, description, color, colors_options if visible, size_or_volume if visible, rating, review_count, seller_name if available, sku if available, shipping_info if available, shipping_text if available, first_review if available, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_07_ALLBIRDS_US_LISTING","domain":"E-commerce / Products","website_id":"allbirds_us","website_name":"Allbirds",
     "start_url":"https://www.allbirds.com/collections/mens",
     "instruction":"Extract men's shoe listings from Allbirds. For each product, return product_name, price_raw, currency, old_price_raw if on sale, discount_percentage if on sale, color if visible, color_options if visible, brand if visible, availability if visible, short_description if visible, rating if visible, review_count if visible, image_url, and product_url.",
     "requires_pagination":False,"requires_detail_page":False,"max_pages":1,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_07_ALLBIRDS_US_DETAIL","domain":"E-commerce / Products","website_id":"allbirds_us","website_name":"Allbirds",
     "start_url":"https://www.allbirds.com/collections/mens",
     "instruction":"Open a product page from Allbirds and extract product_name, brand, price_raw, description, color, color_options if visible, size_or_volume if visible, material if available, care if available, rating, review_count, sku if available, shipping_text if available, first_review if available, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_08_GLOSSIER_US_LISTING","domain":"E-commerce / Products","website_id":"glossier_us","website_name":"Glossier",
     "start_url":"https://www.glossier.com/collections/skincare",
     "instruction":"Extract skincare product listings from Glossier. For each product, return product_name, short_description if visible, price_raw, old_price_raw if on sale, discount_percentage if on sale, currency, color if visible, color_options if visible, size_or_volume if visible, brand if visible, availability if visible, rating if visible, review_count if visible, image_url, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_08_GLOSSIER_US_DETAIL","domain":"E-commerce / Products","website_id":"glossier_us","website_name":"Glossier",
     "start_url":"https://www.glossier.com/collections/skincare",
     "instruction":"Open a product page from Glossier and extract product_name, brand, price_raw, description, color, size_or_volume if available, rating, review_count, sku if available, shipping_text if available, first_review if available, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_09_ETSY_HOME_LIVING_LISTING","domain":"E-commerce / Products","website_id":"etsy_home_living","website_name":"Etsy",
     "start_url":"https://www.etsy.com/c/home-and-living",
     "instruction":"Extract home-and-living listings from Etsy. For each listing, return product_name, price_raw, old_price_raw if visible, discount_percentage if visible, currency, seller_name if visible, rating if visible, review_count if visible, color if visible, color_options if visible, size_or_volume if visible, short_description if visible, image_url, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_09_ETSY_HOME_LIVING_DETAIL","domain":"E-commerce / Products","website_id":"etsy_home_living","website_name":"Etsy",
     "start_url":"https://www.etsy.com/c/home-and-living",
     "instruction":"Open a listing page from Etsy and extract product_name, brand if visible, price_raw, old_price_raw if visible, description, color if visible, size_or_volume if visible, rating, review_count, sku if available, shipping_text if available, first_review_text, first_review_details, first_review_rating, availability if visible, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"hard",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_10_ASOS_US_LISTING","domain":"E-commerce / Products","website_id":"asos_us","website_name":"ASOS",
     "start_url":"https://www.asos.com/women/dresses/cat/?cid=8799",
     "instruction":"Extract product listings from the ASOS women's dresses page. For each product, return product_name, brand if visible, price_raw, old_price_raw if on sale, discount_percentage if on sale, currency, color if visible, color_options if visible, availability if visible, short_description if visible, seller_name if visible, rating if visible, review_count if visible, image_url, and product_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"easy",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_ECOM_10_ASOS_US_DETAIL","domain":"E-commerce / Products","website_id":"asos_us","website_name":"ASOS",
     "start_url":"https://www.asos.com/women/dresses/cat/?cid=8799",
     "instruction":"Open a product page from ASOS and extract product_name, brand, price_raw, currency, discount_percentage if on sale, seller_name if available, description, color, size_or_volume if available, rating, review_count, sku if available, shipping_text if available, availability, image_url, image_urls, and product_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
]

ECOM_GOLD = {
    "WBV1_ECOM_01_IKEA_US_LISTING":        {"count":23,  "sample_detail_url":"https://www.ikea.com/us/en/p/lillesater-sectional-5-seat-gunnared-bright-green-yellow-s39614282/", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description"]},
    "WBV1_ECOM_01_IKEA_US_DETAIL":         {"count":1,   "sample_detail_url":"https://www.ikea.com/us/en/p/lillesater-sectional-5-seat-gunnared-bright-green-yellow-s39614282/", "fields":["availability","brand","color","currency","description","discount_percentage","image_url","image_urls","price_raw","product_name","product_url","rating","review_count","seller_name","shipping_text","size_or_volume","sku"]},
    "WBV1_ECOM_02_NIKE_US_LISTING":        {"count":48,  "sample_detail_url":"https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600", "fields":["color_options","image_url","price_raw","product_name","product_subtitle","product_url"]},
    "WBV1_ECOM_02_NIKE_US_DETAIL":         {"count":1,   "sample_detail_url":"https://www.nike.com/t/air-jordan-4-toro-mens-shoes-Aey77D4l/FQ8138-600", "fields":["available_colors","description","fit","image_urls","price_raw","product_name","product_url","style_color"]},
    "WBV1_ECOM_03_CASPER_US_LISTING":      {"count":9,   "sample_detail_url":"https://casper.com/products/casper-one-foam?variant=41670971261009", "fields":["discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","short_description"]},
    "WBV1_ECOM_03_CASPER_US_DETAIL":       {"count":1,   "sample_detail_url":"https://casper.com/products/casper-one-foam?variant=41670971261009", "fields":["available_sizes","brand","description","discount_percentage","first_review","foam_model","image_urls","measurements","materials","old_price_raw","price_raw","product_name","product_url","rating","review_count"]},
    "WBV1_ECOM_04_WARBYPARKER_US_LISTING": {"count":111, "sample_detail_url":"https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium", "fields":["available_colors","available_widths","color_name","image_url","image_urls","price_raw","product_name","product_url","rating","review_count"]},
    "WBV1_ECOM_04_WARBYPARKER_US_DETAIL":  {"count":1,   "sample_detail_url":"https://www.warbyparker.com/eyeglasses/wilkie/black-matte-eclipse?w=medium", "fields":["available_colors","available_widths","color_name","first_review_content","first_review_title","image_urls","price_raw","product_name","product_url","rating","review_count","selected_width","short_description"]},
    "WBV1_ECOM_05_DECATHLON_US_LISTING":   {"count":16,  "sample_detail_url":None, "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description"]},
    "WBV1_ECOM_05_DECATHLON_US_DETAIL":    {"count":1,   "sample_detail_url":None, "fields":["availability","brand","capacity_or_size","color","color_options","description","first_review_content","first_review_title","image_url","image_urls","key_features","price_raw","product_name","product_url","rating","review_count","sku"]},
    "WBV1_ECOM_06_JUMIA_EGYPT_LISTING":    {"count":40,  "sample_detail_url":"https://www.jumia.com.eg/galaxy-a17-6.7-128gb6gb-dual-sim-4g-mobile-phone-light-blue-samsung-mpg3916850.html", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description"]},
    "WBV1_ECOM_06_JUMIA_EGYPT_DETAIL":     {"count":1,   "sample_detail_url":"https://www.jumia.com.eg/galaxy-a17-6.7-128gb6gb-dual-sim-4g-mobile-phone-light-blue-samsung-mpg3916850.html", "fields":["availability","brand","color","colors_options","description","discount_percentage","first_review","image_url","image_urls","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","shipping_info","shipping_text","size_or_volume","sku"]},
    "WBV1_ECOM_07_ALLBIRDS_US_LISTING":    {"count":43,  "sample_detail_url":"https://www.allbirds.com/products/mens-dasher-nz-anthracite", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description"]},
    "WBV1_ECOM_07_ALLBIRDS_US_DETAIL":     {"count":1,   "sample_detail_url":"https://www.allbirds.com/products/mens-dasher-nz-anthracite", "fields":["availability","brand","care","color","color_options","description","first_review","image_url","image_urls","material","price_raw","product_name","product_url","rating","review_count","shipping_text","size_or_volume","sku"]},
    "WBV1_ECOM_08_GLOSSIER_US_LISTING":    {"count":21,  "sample_detail_url":"https://www.glossier.com/en-ma/products/futuredew", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description","size_or_volume"]},
    "WBV1_ECOM_08_GLOSSIER_US_DETAIL":     {"count":1,   "sample_detail_url":"https://www.glossier.com/en-ma/products/milky-jelly-cleanser?variant=44415832752373", "fields":["availability","brand","color","description","first_review","image_url","image_urls","price_raw","product_name","product_url","rating","review_count","shipping_text","size_or_volume","sku"]},
    "WBV1_ECOM_09_ETSY_HOME_LIVING_LISTING":{"count":64, "sample_detail_url":"https://www.etsy.com/listing/4512009488/beige-terracotta-gray-abstract-geometric", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description","size_or_volume"]},
    "WBV1_ECOM_09_ETSY_HOME_LIVING_DETAIL":{"count":1,   "sample_detail_url":"https://www.etsy.com/listing/237835079/wood-pendant-light-mid-century-modern", "fields":["availability","brand","color","description","first_review_details","first_review_rating","first_review_text","image_url","image_urls","old_price_raw","price_raw","product_name","product_url","rating","review_count","shipping_text","size_or_volume","sku"]},
    "WBV1_ECOM_10_ASOS_US_LISTING":        {"count":72,  "sample_detail_url":"https://www.asos.com/vila/vila-chiffon-trapeze-mini-dress-in-light-pink/prd/210606626?colourWayId=210606627", "fields":["availability","brand","category","color","color_options","currency","discount_percentage","image_url","old_price_raw","price_raw","product_name","product_url","rating","review_count","seller_name","short_description"]},
    "WBV1_ECOM_10_ASOS_US_DETAIL":         {"count":1,   "sample_detail_url":"https://www.asos.com/vila/vila-chiffon-trapeze-mini-dress-in-light-pink/prd/210606626", "fields":["availability","brand","color","currency","description","discount_percentage","image_url","image_urls","price_raw","product_name","product_url","rating","review_count","seller_name","shipping_text","size_or_volume","sku"]},
}

def assign_ecom_schema(tid):
    return "product_detail_v1" if "_DETAIL" in tid else "product_listing_v1"

ecom_all = [build_task(b, assign_ecom_schema(b["task_id"]), ECOM_GOLD[b["task_id"]]) for b in ECOM_TASKS]
ecom_dev_ids = {"WBV1_ECOM_01_IKEA_US_LISTING","WBV1_ECOM_01_IKEA_US_DETAIL","WBV1_ECOM_02_NIKE_US_LISTING","WBV1_ECOM_02_NIKE_US_DETAIL"}
ecom_dev  = [t for t in ecom_all if t["task_id"] in ecom_dev_ids]
ecom_test = [t for t in ecom_all if t["task_id"] not in ecom_dev_ids]

write_jsonl(os.path.join(TASKS_DIR, "ecommerce_all_tasks_20.jsonl"), ecom_all)
write_jsonl(os.path.join(TASKS_DIR, "ecommerce_dev_tasks_4.jsonl"),  ecom_dev)
write_jsonl(os.path.join(TASKS_DIR, "ecommerce_test_tasks_16.jsonl"), ecom_test)
write_csv(os.path.join(TASKS_DIR, "ecommerce_all_tasks_20.csv"), ecom_all)
print(f"ECOMMERCE: all={len(ecom_all)} dev={len(ecom_dev)} test={len(ecom_test)}")

# ============================================================
# GOVERNMENT
# ============================================================
GOV_TASKS = [
    {"task_id":"WBV1_GOV_TED_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"ted","website_name":"TED",
     "start_url":"https://ted.europa.eu/en/search/result",
     "instruction":"Extract tender notices from TED (Tenders Electronic Daily) search results. For each notice, return tender_title, buyer_name, notice_id, notice_type, contract_nature, procedure_type, location, place_of_performance, publication_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_TED_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"ted","website_name":"TED",
     "start_url":"https://ted.europa.eu/en/search/result",
     "instruction":"Open a tender notice from TED and extract tender_title, notice_id, notice_type, form_type, status, buyer, buyer_name, buyer_address, publication_date, closing_date, description, classification, legal_basis, procedure_type, procedure_identifier, estimated_value_excluding_vat, selection_criteria, award_criteria, contract_terms, lot_details, procurement_documents, submission, review, notice_information, notice_dispatch_date, internal_identifier, url_pdf_spanish_language, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"hard",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_FAT_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"fat","website_name":"Find a Tender",
     "start_url":"https://www.find-tender.service.gov.uk/Search/Results",
     "instruction":"Extract tender notices from Find a Tender (UK). For each notice, return tender_title, tender_reference, agency, procurement_category, type_submission, published_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_FAT_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"fat","website_name":"Find a Tender",
     "start_url":"https://www.find-tender.service.gov.uk/Search/Results",
     "instruction":"Open a tender notice from Find a Tender and extract tender_title, agency, awarding_agency, quotation_no, quotation_type, procurement_category, procurement_method, procurement_nature, procurement_type, published_date, status, items_to_respond, offer_validity_duration, payment_terms, contact_persons_details, remarks, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_CFIN_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"cfin","website_name":"Contracts Finder",
     "start_url":"https://www.contractsfinder.service.gov.uk/Search/Results",
     "instruction":"Extract contract notices from Contracts Finder (UK). For each notice, return tender_title, buyer, status, procurement_stage, contract_value, contract_location, description, publication_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_CFIN_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"cfin","website_name":"Contracts Finder",
     "start_url":"https://www.contractsfinder.service.gov.uk/Search/Results",
     "instruction":"Open a contract notice from Contracts Finder and extract tender_title, buyer, procurement_reference, contract_type, contract_value, contract_location, contract_start_date, contract_end_date, publication_date, closing_date, closing_time, procedure_type, suitable_for_smes, suitable_for_vcses, industry, description, address, contact_name, email, telephone, website, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_SAM_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"sam","website_name":"SAM.gov",
     "start_url":"https://sam.gov/search/?index=opp&keywords=software",
     "instruction":"Extract contract opportunities from SAM.gov for 'software'. For each listing, return tender_title, reference_number, department_ind_agency, subtier, office, notice_type, description, published_date, updated_date, current_date_offers_due, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_SAM_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"sam","website_name":"SAM.gov",
     "start_url":"https://sam.gov/search/?index=opp&keywords=software",
     "instruction":"Open a contract opportunity from SAM.gov and extract tender_title, notice_id, notice_type, buyer_name, status, publication_date, original_publication_date, closing_date, original_closing_date, inactive_date, description, classification, contact_information, attachments, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_CANADA_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"canada","website_name":"CanadaBuys",
     "start_url":"https://canadabuys.canada.ca/en/tender-opportunities",
     "instruction":"Extract tender opportunities from CanadaBuys. For each notice, return tender_title, buyer, category, publication_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_CANADA_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"canada","website_name":"CanadaBuys",
     "start_url":"https://canadabuys.canada.ca/en/tender-opportunities",
     "instruction":"Open a tender from CanadaBuys and extract tender_title, notice_id, notice_type, status, procurement_method, publication_date, closing_date, contract_duration, trade_agreements, language, apply_portal_link, description, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_GETS_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"gets","website_name":"GETS NZ",
     "start_url":"https://www.gets.govt.nz/",
     "instruction":"Extract tender notices from GETS (New Zealand Government Electronic Tenders Service). For each notice, return tender_title, rfx_id, reference, organisation, tender_type, close_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_GETS_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"gets","website_name":"GETS NZ",
     "start_url":"https://www.gets.govt.nz/",
     "instruction":"Open a tender notice from GETS and extract tender_title, rfx_id, reference, tender_type, department, contact, open_date, close_date, overview, categories, regions, tender_coverage, required_pre_qualifications, alternate_physical_delivery_address, alternate_physical_fax_number, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_PUBLICCONTRACTSSCOTLAND_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"publiccontractsscotland","website_name":"Public Contracts Scotland",
     "start_url":"https://www.publiccontractsscotland.gov.uk/search/search_mainpage.aspx",
     "instruction":"Extract tender listings from Public Contracts Scotland. For each notice, return tender_title, reference_no, ocid, notice_type, published_by, publication_date, deadline_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_PUBLICCONTRACTSSCOTLAND_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"publiccontractsscotland","website_name":"Public Contracts Scotland",
     "start_url":"https://www.publiccontractsscotland.gov.uk/search/search_mainpage.aspx",
     "instruction":"Open a tender notice from Public Contracts Scotland and extract tender_title, notice_id, notice_type, buyer_name, status, classification, description, contact_information, publication_date, closing_date, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_SELL2WALES_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"sell2wales","website_name":"Sell2Wales",
     "start_url":"https://www.sell2wales.gov.wales/search/search_mainpage.aspx",
     "instruction":"Extract tender listings from Sell2Wales. For each notice, return tender_title, notice_id, ocid, notice_type, buyer_name, location, value if visible, published_to if visible, description if visible, publication_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_SELL2WALES_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"sell2wales","website_name":"Sell2Wales",
     "start_url":"https://www.sell2wales.gov.wales/search/search_mainpage.aspx",
     "instruction":"Open a tender notice from Sell2Wales and extract tender_title, notice_id, ocid, notice_type, buyer, buyer_name, authority_id, status, classification, procurement_reference, description, documents, engagement, contract_details, contact_information, last_modified_date, publication_date, closing_date, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_UNGM_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"ungm","website_name":"UNGM",
     "start_url":"https://www.ungm.org/Public/Notice",
     "instruction":"Extract procurement notices from UNGM (United Nations Global Marketplace). For each notice, return tender_title, notice_id, notice_type, buyer_name, location, publication_date, closing_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_UNGM_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"ungm","website_name":"UNGM",
     "start_url":"https://www.ungm.org/Public/Notice",
     "instruction":"Open a procurement notice from UNGM and extract tender_title, notice_type, buyer_name, reference, publication_date, closing_date, registration_level, description, beneficiary_countries_or_territories, unspsc_codes, revisions, links, contact_information, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_WORLDBANK_PROCUREMENT_001_LISTING","domain":"Government / Tenders / Announcements","website_id":"worldbank_procurement","website_name":"World Bank Procurement",
     "start_url":"https://projects.worldbank.org/en/projects-operations/procurement",
     "instruction":"Extract procurement notices from World Bank Procurement. For each notice, return project_title, notice_type, location, language, description, publication_date, and tender_url.",
     "requires_pagination":True,"requires_detail_page":False,"max_pages":3,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
    {"task_id":"WBV1_GOV_WORLDBANK_PROCUREMENT_002_DETAIL","domain":"Government / Tenders / Announcements","website_id":"worldbank_procurement","website_name":"World Bank Procurement",
     "start_url":"https://projects.worldbank.org/en/projects-operations/procurement",
     "instruction":"Open a procurement notice from World Bank and extract tender_title, project_title, notice_id, notice_type, buyer, status, country, language, project_id, project_financing, procurement_method, publication_date, closing_date, borrower_bid_reference, reference_no_in_notice_text, description, bidding_details, bid_security, lots, contact_information, and tender_url.",
     "requires_pagination":False,"requires_detail_page":True,"max_pages":1,"difficulty":"medium",
     "verified_status":"final_verified","verification_basis":"manual_agent_mode_conversation_verification","snapshot_required":True},
]

GOV_GOLD = {
    "WBV1_GOV_TED_001_LISTING":                         {"count":50, "sample_detail_url":None, "fields":["buyer_name","closing_date","contract_nature","location","notice_id","place_of_performance","procedure_type","publication_date","tender_title","tender_url"]},
    "WBV1_GOV_TED_002_DETAIL":                          {"count":1,  "sample_detail_url":None, "fields":["award_criteria","buyer","buyer_address","buyer_name","classification","closing_date","contract_terms","description","estimated_value_excluding_vat","form_type","internal_identifier","legal_basis","lot_details","notice_dispatch_date","notice_id","notice_information","notice_type","procedure_identifier","procedure_type","procurement_documents","publication_date","review","selection_criteria","status","submission","tender_title","tender_url","url_pdf_spanish_language"]},
    "WBV1_GOV_FAT_001_LISTING":                         {"count":10, "sample_detail_url":None, "fields":["agency","closing_date","procurement_category","published_date","tender_reference","tender_title","tender_url","type_submission"]},
    "WBV1_GOV_FAT_002_DETAIL":                          {"count":1,  "sample_detail_url":None, "fields":["agency","awarding_agency","contact_persons_details","items_to_respond","offer_validity_duration","payment_terms","procurement_category","procurement_method","procurement_nature","procurement_type","published_date","quotation_no","quotation_type","remarks","status","tender_title","tender_url"]},
    "WBV1_GOV_CFIN_001_LISTING":                        {"count":20, "sample_detail_url":None, "fields":["buyer","closing_date","contract_location","contract_value","description","procurement_stage","publication_date","status","tender_title","tender_url"]},
    "WBV1_GOV_CFIN_002_DETAIL":                         {"count":1,  "sample_detail_url":None, "fields":["address","buyer","closing_date","closing_time","contact_name","contract_end_date","contract_location","contract_start_date","contract_type","contract_value","description","email","industry","procedure_type","procurement_reference","publication_date","suitable_for_smes","suitable_for_vcses","telephone","tender_title","tender_url","website"]},
    "WBV1_GOV_SAM_001_LISTING":                         {"count":25, "sample_detail_url":None, "fields":["current_date_offers_due","department_ind_agency","description","notice_type","office","published_date","reference_number","subtier","tender_title","tender_url","updated_date"]},
    "WBV1_GOV_SAM_002_DETAIL":                          {"count":1,  "sample_detail_url":None, "fields":["attachments","buyer_name","classification","closing_date","contact_information","description","inactive_date","notice_id","notice_type","original_closing_date","original_publication_date","publication_date","status","tender_title","tender_url"]},
    "WBV1_GOV_CANADA_001_LISTING":                      {"count":50, "sample_detail_url":None, "fields":["buyer","category","closing_date","publication_date","tender_title","tender_url"]},
    "WBV1_GOV_CANADA_002_DETAIL":                       {"count":1,  "sample_detail_url":None, "fields":["apply_portal_link","closing_date","contract_duration","description","language","notice_id","notice_type","procurement_method","publication_date","status","tender_title","tender_url","trade_agreements"]},
    "WBV1_GOV_GETS_001_LISTING":                        {"count":25, "sample_detail_url":None, "fields":["close_date","organisation","reference","rfx_id","tender_title","tender_type","tender_url"]},
    "WBV1_GOV_GETS_002_DETAIL":                         {"count":1,  "sample_detail_url":None, "fields":["alternate_physical_delivery_address","alternate_physical_fax_number","categories","close_date","contact","department","open_date","overview","reference","regions","required_pre_qualifications","rfx_id","tender_coverage","tender_title","tender_type","tender_url"]},
    "WBV1_GOV_PUBLICCONTRACTSSCOTLAND_001_LISTING":     {"count":10, "sample_detail_url":"https://www.publiccontractsscotland.gov.uk/search/show/search_view.aspx?ID=MAY506720", "fields":["deadline_date","notice_type","ocid","publication_date","published_by","reference_no","tender_title","tender_url"]},
    "WBV1_GOV_PUBLICCONTRACTSSCOTLAND_002_DETAIL":      {"count":1,  "sample_detail_url":"https://www.publiccontractsscotland.gov.uk/search/show/search_view.aspx?ID=MAY506720", "fields":["buyer_name","classification","closing_date","contact_information","description","notice_id","notice_type","publication_date","status","tender_title","tender_url"]},
    "WBV1_GOV_SELL2WALES_001_LISTING":                  {"count":10, "sample_detail_url":"https://www.sell2wales.gov.wales/search/show/search_view.aspx?ID=MAY492383", "fields":["buyer_name","closing_date","description","location","notice_id","notice_type","ocid","publication_date","published_to","tender_title","tender_url","value"]},
    "WBV1_GOV_SELL2WALES_002_DETAIL":                   {"count":1,  "sample_detail_url":"https://www.sell2wales.gov.wales/search/show/search_view.aspx?ID=MAY492383", "fields":["authority_id","buyer","buyer_name","classification","closing_date","contact_information","contract_details","description","documents","engagement","last_modified_date","notice_id","notice_type","ocid","procurement_reference","publication_date","status","tender_title","tender_url"]},
    "WBV1_GOV_UNGM_001_LISTING":                        {"count":30, "sample_detail_url":"https://www.ungm.org/Public/Notice/235889", "fields":["buyer_name","closing_date","location","notice_id","notice_type","publication_date","tender_title","tender_url"]},
    "WBV1_GOV_UNGM_002_DETAIL":                         {"count":1,  "sample_detail_url":"https://www.ungm.org/Public/Notice/235889", "fields":["beneficiary_countries_or_territories","buyer_name","closing_date","contact_information","description","links","notice_type","publication_date","reference","registration_level","revisions","tender_title","tender_url","unspsc_codes"]},
    "WBV1_GOV_WORLDBANK_PROCUREMENT_001_LISTING":       {"count":20, "sample_detail_url":"https://projects.worldbank.org/en/projects-operations/procurement-detail/OP00293150", "fields":["description","language","location","notice_type","project_title","publication_date","tender_url"]},
    "WBV1_GOV_WORLDBANK_PROCUREMENT_002_DETAIL":        {"count":1,  "sample_detail_url":"https://projects.worldbank.org/en/projects-operations/procurement-detail/OP00293150", "fields":["bid_security","bidding_details","borrower_bid_reference","buyer","closing_date","contact_information","country","description","language","lots","notice_id","notice_type","procurement_method","project_financing","project_id","project_title","publication_date","reference_no_in_notice_text","status","tender_title","tender_url"]},
}

def assign_gov_schema(tid):
    return "tender_notice_detail_v1" if "_002_DETAIL" in tid else "tender_notice_listing_v1"

gov_all = [build_task(b, assign_gov_schema(b["task_id"]), GOV_GOLD[b["task_id"]]) for b in GOV_TASKS]
gov_dev_ids = {"WBV1_GOV_TED_001_LISTING","WBV1_GOV_TED_002_DETAIL","WBV1_GOV_FAT_001_LISTING","WBV1_GOV_FAT_002_DETAIL"}
gov_dev  = [t for t in gov_all if t["task_id"] in gov_dev_ids]
gov_test = [t for t in gov_all if t["task_id"] not in gov_dev_ids]

write_jsonl(os.path.join(TASKS_DIR, "government_all_tasks.jsonl"),    gov_all)
write_jsonl(os.path.join(TASKS_DIR, "government_dev_tasks_4.jsonl"),  gov_dev)
write_jsonl(os.path.join(TASKS_DIR, "government_test_tasks_16.jsonl"),gov_test)
write_csv(os.path.join(TASKS_DIR, "government_all_tasks.csv"),        gov_all)
print(f"GOVERNMENT: all={len(gov_all)} dev={len(gov_dev)} test={len(gov_test)}")

print("\nAll task files written successfully.")
