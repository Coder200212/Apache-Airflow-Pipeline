version: 1
name: support.customer_requests
primary_key: [request_id]
unique_constraints:
- [request_id]
indexes:
- name: idx_customer_requests_status
columns: [status]
- name: idx_customer_requests_created_at
columns: [created_at]


columns:
- name: request_id
type: varchar(64)
nullable: false
- name: created_at
type: timestamptz
nullable: false
- name: last_updated
type: timestamptz
nullable: true
- name: customer_email
type: text
nullable: true
- name: category
type: text
nullable: true
- name: priority
type: varchar(16)
nullable: true
- name: subject
type: text
nullable: true
- name: body
type: text
nullable: true
- name: status
type: varchar(32)
nullable: false
- name: source_file
type: text
nullable: true
- name: row_hash
type: varchar(64)
nullable: true
- name: ingested_at
type: timestamptz
nullable: true