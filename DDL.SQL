
CREATE TABLE tender_master (
	tndr_pk bigserial NOT NULL,
	tndr_source_file varchar NULL,
	dst_source_file varchar NULL,
	dept_source_file varchar NULL,
	crt_dt timestamp NULL,
	crt_user varchar NULL,
	CONSTRAINT tender_master_pkey PRIMARY KEY (tndr_pk)
);

CREATE TABLE users (
	id serial4 NOT NULL,
	username varchar(255) NOT NULL,
	email varchar(255) NOT NULL,
	"password" varchar(255) NOT NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT users_email_key UNIQUE (email),
	CONSTRAINT users_pkey PRIMARY KEY (id),
	CONSTRAINT users_username_key UNIQUE (username)
);

CREATE TABLE "DEPT_DTLS" (
	"DEPT_DTLS_PK" bigserial NOT NULL,
	"SR_NO" varchar(50) NULL,
	"DEPT_NAME" varchar(255) NULL,
	"SUB_DEPT_NAME" varchar(255) NULL,
	"DEPT_SUB_DEPT_CODE" varchar(100) NULL,
	CONSTRAINT "DEPT_DTLS_pkey" PRIMARY KEY ("DEPT_DTLS_PK"),
	CONSTRAINT dept_dtls_fk FOREIGN KEY ("DEPT_DTLS_PK") REFERENCES tender_master(tndr_pk)
);


CREATE TABLE "DISTRICT_DETAILS" (
	"DIST_DTLS_PK" serial4 NOT NULL,
	"DIST_CODE" int4 NULL,
	"DIST_NAME" varchar(255) NULL,
	"ZONE" varchar(255) NULL,
	CONSTRAINT "DISTRICT_DETAILS_pkey" PRIMARY KEY ("DIST_DTLS_PK"),
	CONSTRAINT dist_dtls_fk FOREIGN KEY ("DIST_DTLS_PK") REFERENCES tender_master(tndr_pk)
);


CREATE TABLE "TENDER_DATA_DTLS" (
	"TDM_PK" bigserial NOT NULL,
	"DISTRICT_CODE" int4 NULL,
	"WORK_CODE" int4 NULL,
	"DEPARTMENT_CODE" varchar(255) NULL,
	"PROJECT_NAME" varchar(255) NULL,
	"SANCTION_COST" float8 NULL,
	"SANCTION_DATE" varchar NULL,
	"FUND_RECEIVED" float8 NULL,
	"FUND_RECEIVED_DATE" varchar NULL,
	"LAND_RECEIVED_DATE" varchar NULL,
	"WIP_PREVIOUS_YEAR" float8 NULL,
	"WIP_CURRENT_YEAR" float8 NULL,
	"WIP_CURRENT_MONTH" float8 NULL,
	"WIP_TOTAL" float8 NULL,
	"PHYSICAL_PROGRESS" float8 NULL,
	"PHYSICAL_PROGRESS_REMARK" varchar(255) NULL,
	CONSTRAINT "TENDER_DATA_DTLS_pkey" PRIMARY KEY ("TDM_PK"),
	CONSTRAINT tndr_fk FOREIGN KEY ("TDM_PK") REFERENCES tender_master(tndr_pk)
);