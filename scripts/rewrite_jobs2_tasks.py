"""
Rewrite jobs task files based on ground truth from data/gold/by_task/jobs2/.
Generates:
  - data/tasks/jobs_all_tasks_20.jsonl
  - data/tasks/jobs_all_tasks_20.csv
  - data/tasks/jobs_dev_tasks_4.jsonl
  - data/tasks/jobs_test_tasks_16.jsonl
"""
import json
import os
import csv

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD_DIR = os.path.join(REPO, "data", "gold", "by_task", "jobs2")
TASKS_DIR = os.path.join(REPO, "data", "tasks")

# ------------------------------------------------------------------
# Ground truth derived from the gold files in jobs2/
# ------------------------------------------------------------------
GOLD = {
    "WBV1_JOBS_REED_001_LISTING": {
        "count": 25,
        "fields": ["company_name", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.reed.co.uk/jobs/senior-developer/56875053?source=searchResults&filter=%2Fjobs%2Fdeveloper-jobs",
    },
    "WBV1_JOBS_REED_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.reed.co.uk/jobs/junior-developer/57037836",
    },
    "WBV1_JOBS_POSTJOBFREE_001_LISTING": {
        "count": 10,
        "fields": ["company_name", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.postjobfree.com/job/bwv490/mechanical-engineer-iii-santa-barbara-ca",
    },
    "WBV1_JOBS_POSTJOBFREE_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.postjobfree.com/job/bwv490/mechanical-engineer-iii-santa-barbara-ca",
    },
    "WBV1_JOBS_REMOTEOK_001_LISTING": {
        "count": 150,
        "fields": ["company_name", "job_title", "job_url", "location", "salary", "tags"],
        "sample_detail_url": "https://remoteok.com/remote-jobs/remote-events-marketing-manager-pivotal-health-1132436",
    },
    "WBV1_JOBS_REMOTEOK_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location", "salary", "tags"],
        "sample_detail_url": "https://remoteok.com/remote-jobs/remote-digital-solutions-specialist-newport-water-1132423",
    },
    "WBV1_JOBS_RELIEFWEB_001_LISTING": {
        "count": 20,
        "fields": ["application_deadline", "company_name", "country", "job_title", "job_url", "posted_date"],
        "sample_detail_url": "https://reliefweb.int/job/4215856/medical-doctor-gaza",
    },
    "WBV1_JOBS_RELIEFWEB_002_DETAIL": {
        "count": 1,
        "fields": ["application_deadline", "company_name", "job_description", "job_title", "job_url", "location", "posted_date"],
        "sample_detail_url": "https://reliefweb.int/job/4215856/medical-doctor-gaza",
    },
    "WBV1_JOBS_EUROBRUSSELS_001_LISTING": {
        "count": 19,
        "fields": ["company_name", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.eurobrussels.com/job_display/291646/Public_Affairs_Consultant_EFC_European_Football_Clubs_Brussels_Belgium",
    },
    "WBV1_JOBS_EUROBRUSSELS_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "job_description", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.eurobrussels.com/job_display/291628/Senior_Communications_Officer_REScoopeu_Brussels_Belgium",
    },
    "WBV1_JOBS_UNJOBS_001_LISTING": {
        "count": 25,
        "fields": ["company_name", "job_title", "job_url"],
        "sample_detail_url": "https://unjobs.org/vacancies/1779896650956",
    },
    "WBV1_JOBS_UNJOBS_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location", "qualifications"],
        "sample_detail_url": "https://unjobs.org/vacancies/1778623830833",
    },
    "WBV1_JOBS_THTJOBS_001_LISTING": {
        "count": 21,
        "fields": ["company_name", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.timeshighereducation.com/unijobs/listing/408414/global-search-for-excellence-the-90-scholars-for-90th-anniversary-strategic-hiring-scheme/?LinkSource=TopJob",
    },
    "WBV1_JOBS_THTJOBS_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location"],
        "sample_detail_url": "https://www.timeshighereducation.com/unijobs/listing/408414/global-search-for-excellence-the-90-scholars-for-90th-anniversary-strategic-hiring-scheme/",
    },
    "WBV1_JOBS_NATURECAREERS_001_LISTING": {
        "count": 20,
        "fields": ["company_name", "job_description", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.nature.com/naturecareers/job/12860948/-associate-senior-editor-nature-communications-human-behaviour-/?LinkSource=PremiumListing",
    },
    "WBV1_JOBS_NATURECAREERS_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "employment_type", "job_description", "job_title", "job_url", "location", "salary"],
        "sample_detail_url": "https://www.nature.com/naturecareers/job/12859405/full-professorship-w3-for-biochemistry-f-m-d-/?LinkSource=PremiumListing",
    },
    "WBV1_JOBS_GITHUB_001_LISTING": {
        "count": 10,
        "fields": ["job_title", "job_url", "location"],
        "sample_detail_url": None,
    },
    "WBV1_JOBS_GITHUB_002_DETAIL": {
        "count": 1,
        "fields": ["employment_type", "job_description", "job_title", "job_url", "location"],
        "sample_detail_url": None,
    },
    "WBV1_JOBS_GOOGLE_001_LISTING": {
        "count": 20,
        "fields": ["company_name", "employment_type", "job_title", "job_url", "location"],
        "sample_detail_url": "https://www.google.com/about/careers/applications/jobs/results/137691136725525190-director-business-intelligence",
    },
    "WBV1_JOBS_GOOGLE_002_DETAIL": {
        "count": 1,
        "fields": ["company_name", "job_description", "job_title", "job_url", "location", "salary_range"],
        "sample_detail_url": None,
    },
}

# ------------------------------------------------------------------
# Base task definitions (instruction, urls, pagination flags, etc.)
# ------------------------------------------------------------------
BASE_TASKS = [
    {
        "task_id": "WBV1_JOBS_REED_001_LISTING",
        "domain": "Jobs",
        "website_id": "reed",
        "website_name": "Reed",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.reed.co.uk/jobs/it-jobs",
        "instruction": (
            "Extract job postings from the Reed IT jobs listing page. "
            "For each job, return job_title, company_name, location, employment_type if visible, "
            "salary if visible, posted_date if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_REED_002_DETAIL",
        "domain": "Jobs",
        "website_id": "reed",
        "website_name": "Reed",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.reed.co.uk/jobs/it-jobs",
        "instruction": (
            "Open a job posting from the Reed IT jobs listing page and extract "
            "job_title, company_name, location, employment_type if available, "
            "salary if available, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_POSTJOBFREE_001_LISTING",
        "domain": "Jobs",
        "website_id": "postjobfree",
        "website_name": "Postjobfree",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.postjobfree.com/jobs?q=engineer",
        "instruction": (
            "Extract job postings from the PostJobFree search results for 'engineer'. "
            "For each job, return job_title, company_name, location, salary if visible, "
            "posted_date if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_POSTJOBFREE_002_DETAIL",
        "domain": "Jobs",
        "website_id": "postjobfree",
        "website_name": "Postjobfree",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.postjobfree.com/jobs?q=engineer",
        "instruction": (
            "Open a job listing from the PostJobFree search results and extract "
            "job_title, company_name, location, employment_type if available, "
            "salary if available, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_REMOTEOK_001_LISTING",
        "domain": "Jobs",
        "website_id": "remoteok",
        "website_name": "Remoteok",
        "schema_id": "job_posting_v1",
        "start_url": "https://remoteok.com/remote-dev-jobs",
        "instruction": (
            "Extract remote developer job postings from the RemoteOK remote developer jobs listing page. "
            "For each job, return job_title, company_name, location (remote tag), "
            "salary if visible, tags if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 2,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_REMOTEOK_002_DETAIL",
        "domain": "Jobs",
        "website_id": "remoteok",
        "website_name": "Remoteok",
        "schema_id": "job_posting_v1",
        "start_url": "https://remoteok.com/remote-dev-jobs",
        "instruction": (
            "Open a remote developer job posting from the RemoteOK listing page and extract "
            "job_title, company_name, location, employment_type if available, "
            "salary if available, job_description, tags, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_RELIEFWEB_001_LISTING",
        "domain": "Jobs",
        "website_id": "reliefweb",
        "website_name": "Reliefweb",
        "schema_id": "job_posting_v1",
        "start_url": "https://reliefweb.int/jobs",
        "instruction": (
            "Extract humanitarian job postings from the ReliefWeb jobs listing page. "
            "For each job, return job_title, company_name or organization, country, "
            "application_deadline, posted_date if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_RELIEFWEB_002_DETAIL",
        "domain": "Jobs",
        "website_id": "reliefweb",
        "website_name": "Reliefweb",
        "schema_id": "job_posting_v1",
        "start_url": "https://reliefweb.int/jobs",
        "instruction": (
            "Open a job posting from the ReliefWeb jobs listing page and extract "
            "job_title, company_name or organization, location, application_deadline, "
            "posted_date, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_EUROBRUSSELS_001_LISTING",
        "domain": "Jobs",
        "website_id": "eurobrussels",
        "website_name": "Eurobrussels",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.eurobrussels.com",
        "instruction": (
            "Extract EU job postings from the EuroBrussels homepage listing. "
            "For each job, return job_title, company_name or organization, location, "
            "salary if visible, application_deadline if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_EUROBRUSSELS_002_DETAIL",
        "domain": "Jobs",
        "website_id": "eurobrussels",
        "website_name": "Eurobrussels",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.eurobrussels.com",
        "instruction": (
            "Open a job posting from the EuroBrussels listing page and extract "
            "job_title, company_name or organization, location, salary if available, "
            "job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_UNJOBS_001_LISTING",
        "domain": "Jobs",
        "website_id": "unjobs",
        "website_name": "Unjobs",
        "schema_id": "job_posting_v1",
        "start_url": "https://unjobs.org",
        "instruction": (
            "Extract United Nations job postings from the UN Jobs listing page. "
            "For each job, return job_title, company_name or organization, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_UNJOBS_002_DETAIL",
        "domain": "Jobs",
        "website_id": "unjobs",
        "website_name": "Unjobs",
        "schema_id": "job_posting_v1",
        "start_url": "https://unjobs.org",
        "instruction": (
            "Open a job posting from the UN Jobs listing page and extract "
            "job_title, company_name or organization, location, employment_type if available, "
            "qualifications if available, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_THTJOBS_001_LISTING",
        "domain": "Jobs",
        "website_id": "thtjobs",
        "website_name": "thtjobs",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.timeshighereducation.com/unijobs/listings/academic-posts/",
        "instruction": (
            "Extract academic job postings from the Times Higher Education academic posts listing page. "
            "For each job, return job_title, company_name or institution, location, "
            "salary if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_THTJOBS_002_DETAIL",
        "domain": "Jobs",
        "website_id": "thtjobs",
        "website_name": "thtjobs",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.timeshighereducation.com/unijobs/listings/academic-posts/",
        "instruction": (
            "Open a job posting from the Times Higher Education academic posts listing and extract "
            "job_title, company_name or institution, location, employment_type if available, "
            "job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_NATURECAREERS_001_LISTING",
        "domain": "Jobs",
        "website_id": "naturecareers",
        "website_name": "Naturecareers",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.nature.com/naturecareers/jobs",
        "instruction": (
            "Extract scientific job postings from the Nature Careers jobs listing page. "
            "For each job, return job_title, company_name or employer, location, "
            "salary if visible, job_description summary if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_NATURECAREERS_002_DETAIL",
        "domain": "Jobs",
        "website_id": "naturecareers",
        "website_name": "Naturecareers",
        "schema_id": "job_posting_v1",
        "start_url": "https://www.nature.com/naturecareers/jobs",
        "instruction": (
            "Open a job posting from the Nature Careers jobs listing page and extract "
            "job_title, company_name or employer, location, employment_type if available, "
            "salary if available, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_GITHUB_001_LISTING",
        "domain": "Jobs",
        "website_id": "github",
        "website_name": "github",
        "schema_id": "job_posting_v1",
        "start_url": "https://github.com/about/careers",
        "instruction": (
            "Extract job postings from the GitHub careers listing page. "
            "For each job, return job_title, location if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_GITHUB_002_DETAIL",
        "domain": "Jobs",
        "website_id": "github",
        "website_name": "github",
        "schema_id": "job_posting_v1",
        "start_url": "https://github.com/about/careers",
        "instruction": (
            "Open a job posting from the GitHub careers listing page and extract "
            "job_title, location, employment_type if available, job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_GOOGLE_001_LISTING",
        "domain": "Jobs",
        "website_id": "google",
        "website_name": "google",
        "schema_id": "job_posting_v1",
        "start_url": "https://careers.google.com/jobs/results/",
        "instruction": (
            "Extract job postings from the Google careers search results page. "
            "For each job, return job_title, company_name (Google), location, "
            "employment_type if visible, and job_url."
        ),
        "requires_pagination": True,
        "requires_detail_page": False,
        "max_pages": 3,
        "difficulty": "easy",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
    {
        "task_id": "WBV1_JOBS_GOOGLE_002_DETAIL",
        "domain": "Jobs",
        "website_id": "google",
        "website_name": "google",
        "schema_id": "job_posting_v1",
        "start_url": "https://careers.google.com/jobs/results/",
        "instruction": (
            "Open a job posting from the Google careers listing page and extract "
            "job_title, company_name (Google), location, salary_range if available, "
            "job_description, and job_url."
        ),
        "requires_pagination": False,
        "requires_detail_page": True,
        "max_pages": 1,
        "difficulty": "medium",
        "verified_status": "final_verified",
        "verification_basis": "manual_agent_mode_conversation_verification",
        "snapshot_required": True,
    },
]

# ------------------------------------------------------------------
# Build merged task records
# ------------------------------------------------------------------
ORDERED_KEYS = [
    "task_id", "domain", "website_id", "website_name", "schema_id",
    "start_url", "sample_detail_url", "instruction",
    "requires_pagination", "requires_detail_page", "max_pages",
    "target_records", "difficulty", "verified_status",
    "verification_basis", "snapshot_required", "expected_fields",
]

all_tasks = []
for base in BASE_TASKS:
    tid = base["task_id"]
    g = GOLD[tid]
    task = {k: base.get(k) for k in ORDERED_KEYS if k in base}
    task["sample_detail_url"] = g["sample_detail_url"]
    task["target_records"] = g["count"]
    task["expected_fields"] = g["fields"]
    # Re-order
    ordered = {k: task[k] for k in ORDERED_KEYS}
    all_tasks.append(ordered)

# Dev split: REED + POSTJOBFREE (first 4 tasks)
dev_ids = {
    "WBV1_JOBS_REED_001_LISTING",
    "WBV1_JOBS_REED_002_DETAIL",
    "WBV1_JOBS_POSTJOBFREE_001_LISTING",
    "WBV1_JOBS_POSTJOBFREE_002_DETAIL",
}
dev_tasks = [t for t in all_tasks if t["task_id"] in dev_ids]
test_tasks = [t for t in all_tasks if t["task_id"] not in dev_ids]


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


write_jsonl(os.path.join(TASKS_DIR, "jobs_all_tasks_20.jsonl"), all_tasks)
write_jsonl(os.path.join(TASKS_DIR, "jobs_dev_tasks_4.jsonl"), dev_tasks)
write_jsonl(os.path.join(TASKS_DIR, "jobs_test_tasks_16.jsonl"), test_tasks)
write_csv(os.path.join(TASKS_DIR, "jobs_all_tasks_20.csv"), all_tasks)

print(f"Written {len(all_tasks)} tasks to jobs_all_tasks_20.*")
print(f"Written {len(dev_tasks)} tasks to jobs_dev_tasks_4.jsonl")
print(f"Written {len(test_tasks)} tasks to jobs_test_tasks_16.jsonl")

# Sanity check
for t in all_tasks:
    tid = t["task_id"]
    g = GOLD[tid]
    assert t["target_records"] == g["count"], f"{tid}: count mismatch"
    assert t["expected_fields"] == g["fields"], f"{tid}: fields mismatch"
print("All sanity checks passed.")
