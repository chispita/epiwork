--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

DROP TABLE public.epidb_results_weekly;
DROP TABLE public.epidb_results_intake;
SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: epidb_results_intake; Type: TABLE; Schema: public; Owner: admin; Tablespace: 
--

CREATE TABLE epidb_results_intake (
    country character(2),
    global_id character varying(36),
    "timestamp" timestamp with time zone,
    "Q0" integer,
    "NOTE" text,
    "Q1" integer,
    "Q2" character varying(7),
    "Q3" character varying(30),
    "Q4" integer,
    "Q4b" integer,
    "Q4b_0_open" character varying(30),
    "Q4c" integer,
    "Q4d_0" boolean NOT NULL,
    "Q4d_1" boolean NOT NULL,
    "Q4d_2" boolean NOT NULL,
    "Q4d_3" boolean NOT NULL,
    "Q4d_4" boolean NOT NULL,
    "Q4d_5" boolean NOT NULL,
    "Q5_0" boolean NOT NULL,
    "Q5_1" boolean NOT NULL,
    "Q5_2" boolean NOT NULL,
    "Q5_3" boolean NOT NULL,
    "Q5_4" boolean NOT NULL,
    "Q6_0" boolean NOT NULL,
    "Q6_0_open" integer,
    "Q6_1" boolean NOT NULL,
    "Q6_1_open" integer,
    "Q6_2" boolean NOT NULL,
    "Q6_2_open" integer,
    "Q6_3" boolean NOT NULL,
    "Q6_3_open" integer,
    "Q6_4" boolean NOT NULL,
    "Q6_4_open" integer,
    "Q6b" integer,
    "Q7" integer,
    "Q7b" integer,
    "Q8" integer,
    "Q9" integer,
    "Q10" integer,
    "Q10b" integer,
    "Q10b_1_open" date,
    "Q10c_0" boolean NOT NULL,
    "Q10c_1" boolean NOT NULL,
    "Q10c_2" boolean NOT NULL,
    "Q10c_3" boolean NOT NULL,
    "Q10c_4" boolean NOT NULL,
    "Q10c_5" boolean NOT NULL,
    "Q10c_6" boolean NOT NULL,
    "Q10c_7" boolean NOT NULL,
    "Q10c_8" boolean NOT NULL,
    "Q10c_9" boolean NOT NULL,
    "Q10d_0" boolean NOT NULL,
    "Q10d_1" boolean NOT NULL,
    "Q10d_2" boolean NOT NULL,
    "Q10d_3" boolean NOT NULL,
    "Q10d_4" boolean NOT NULL,
    "Q10d_5" boolean NOT NULL,
    "Q10d_6" boolean NOT NULL,
    "Q10d_7" boolean NOT NULL,
    "Q10d_8" boolean NOT NULL,
    "Q10d_9" boolean NOT NULL,
    "Q10d_10" boolean NOT NULL,
    "Q10d_11" boolean NOT NULL,
    "Q10d_12" boolean NOT NULL,
    "Q10d_13" boolean NOT NULL,
    "Q10d_14" boolean NOT NULL,
    "Q11_0" boolean NOT NULL,
    "Q11_1" boolean NOT NULL,
    "Q11_2" boolean NOT NULL,
    "Q11_3" boolean NOT NULL,
    "Q11_4" boolean NOT NULL,
    "Q11_5" boolean NOT NULL,
    "Q11_6" boolean NOT NULL,
    "Q12" integer,
    "Q12b" integer,
    "Q13" integer,
    "Q14_1" boolean NOT NULL,
    "Q14_2" boolean NOT NULL,
    "Q14_3" boolean NOT NULL,
    "Q14_4" boolean NOT NULL,
    "Q14_5" boolean NOT NULL,
    "Q15_0" boolean NOT NULL,
    "Q15_1" boolean NOT NULL,
    "Q15_2" boolean NOT NULL,
    "Q15_3" boolean NOT NULL,
    "Q15_4" boolean NOT NULL,
    "Q16_0" boolean NOT NULL,
    "Q16_1" boolean NOT NULL,
    "Q16_2" boolean NOT NULL,
    "Q16_3" boolean NOT NULL,
    "Q16_4" boolean NOT NULL,
    "Q17_0" boolean NOT NULL,
    "Q17_1" boolean NOT NULL,
    "Q17_2" boolean NOT NULL,
    "Q17_3" boolean NOT NULL,
    "Q17_4" boolean NOT NULL,
    "Q17_5" boolean NOT NULL,
    CONSTRAINT "pollster_results_intake_Q0_check2" CHECK (("Q0" >= 0)),
    CONSTRAINT "pollster_results_intake_Q10_check2" CHECK (("Q10" >= 0)),
    CONSTRAINT "pollster_results_intake_Q10b_check2" CHECK (("Q10b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q12_check2" CHECK (("Q12" >= 0)),
    CONSTRAINT "pollster_results_intake_Q12b_check2" CHECK (("Q12b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q13_check2" CHECK (("Q13" >= 0)),
    CONSTRAINT "pollster_results_intake_Q1_check2" CHECK (("Q1" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4_check2" CHECK (("Q4" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4b_check2" CHECK (("Q4b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q4c_check2" CHECK (("Q4c" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6_0_open_check2" CHECK (("Q6_0_open" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6_1_open_check2" CHECK (("Q6_1_open" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6_2_open_check2" CHECK (("Q6_2_open" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6_3_open_check2" CHECK (("Q6_3_open" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6_4_open_check2" CHECK (("Q6_4_open" >= 0)),
    CONSTRAINT "pollster_results_intake_Q6b_check2" CHECK (("Q6b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q7_check2" CHECK (("Q7" >= 0)),
    CONSTRAINT "pollster_results_intake_Q7b_check2" CHECK (("Q7b" >= 0)),
    CONSTRAINT "pollster_results_intake_Q8_check2" CHECK (("Q8" >= 0)),
    CONSTRAINT "pollster_results_intake_Q9_check2" CHECK (("Q9" >= 0))
);



--
-- Name: epidb_results_weekly; Type: TABLE; Schema: public; Owner: admin; Tablespace: 
--

CREATE TABLE epidb_results_weekly (
    country character(2),
    global_id character varying(36),
    "timestamp" timestamp with time zone,
    "Q1_0" boolean NOT NULL,
    "Q1_1" boolean NOT NULL,
    "Q1_2" boolean NOT NULL,
    "Q1_3" boolean NOT NULL,
    "Q1_4" boolean NOT NULL,
    "Q1_5" boolean NOT NULL,
    "Q1_6" boolean NOT NULL,
    "Q1_7" boolean NOT NULL,
    "Q1_8" boolean NOT NULL,
    "Q1_9" boolean NOT NULL,
    "Q1_10" boolean NOT NULL,
    "Q1_11" boolean NOT NULL,
    "Q1_12" boolean NOT NULL,
    "Q1_13" boolean NOT NULL,
    "Q1_14" boolean NOT NULL,
    "Q1_15" boolean NOT NULL,
    "Q1_16" boolean NOT NULL,
    "Q1_17" boolean NOT NULL,
    "Q1_18" boolean NOT NULL,
    "Q1_19" boolean NOT NULL,
    "Q2" integer,
    "N1" text,
    "Q3" integer,
    "Q3_0_open" date,
    "Q4" integer,
    "Q4_0_open" date,
    "Q5" integer,
    "Q6" integer,
    "Q6_1_open" date,
    "Q6b" integer,
    "Q6c" integer,
    "Q6d" integer,
    "Q7_0" boolean NOT NULL,
    "Q7_1" boolean NOT NULL,
    "Q7_3" boolean NOT NULL,
    "Q7_2" boolean NOT NULL,
    "Q7_4" boolean NOT NULL,
    "Q7_5" boolean NOT NULL,
    "Q7b" integer,
    "Q8_0" boolean NOT NULL,
    "Q8_1" boolean NOT NULL,
    "Q8_2" boolean NOT NULL,
    "Q8_3" boolean NOT NULL,
    "Q8_4" boolean NOT NULL,
    "Q8_5" boolean NOT NULL,
    "Q8b" integer,
    "Q9_0" boolean NOT NULL,
    "Q9_1" boolean NOT NULL,
    "Q9_2" boolean NOT NULL,
    "Q9_3" boolean NOT NULL,
    "Q9_4" boolean NOT NULL,
    "Q9_5" boolean NOT NULL,
    "Q9_6" boolean NOT NULL,
    "Q9b" integer,
    "Q10" integer,
    "Q10b" integer,
    "Q10c" integer,
    "Q11" integer,
    "Q12_multi_row1_col1" integer,
    "Q13_multi_row1_col1" integer,
    CONSTRAINT "pollster_results_weekly_Q10_check1" CHECK (("Q10" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q10b_check1" CHECK (("Q10b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q10c_check1" CHECK (("Q10c" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q11_check1" CHECK (("Q11" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q12_multi_row1_col1_check1" CHECK (("Q12_multi_row1_col1" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q13_multi_row1_col1_check1" CHECK (("Q13_multi_row1_col1" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q2_check1" CHECK (("Q2" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q3_check1" CHECK (("Q3" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q4_check1" CHECK (("Q4" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q5_check1" CHECK (("Q5" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6_check1" CHECK (("Q6" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6b_check1" CHECK (("Q6b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6c_check1" CHECK (("Q6c" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q6d_check1" CHECK (("Q6d" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q7b_check1" CHECK (("Q7b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q8b_check1" CHECK (("Q8b" >= 0)),
    CONSTRAINT "pollster_results_weekly_Q9b_check1" CHECK (("Q9b" >= 0))
);



--
-- Data for Name: epidb_results_intake; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY epidb_results_intake (country, global_id, "timestamp", "Q0", "NOTE", "Q1", "Q2", "Q3", "Q4", "Q4b", "Q4b_0_open", "Q4c", "Q4d_0", "Q4d_1", "Q4d_2", "Q4d_3", "Q4d_4", "Q4d_5", "Q5_0", "Q5_1", "Q5_2", "Q5_3", "Q5_4", "Q6_0", "Q6_0_open", "Q6_1", "Q6_1_open", "Q6_2", "Q6_2_open", "Q6_3", "Q6_3_open", "Q6_4", "Q6_4_open", "Q6b", "Q7", "Q7b", "Q8", "Q9", "Q10", "Q10b", "Q10b_1_open", "Q10c_0", "Q10c_1", "Q10c_2", "Q10c_3", "Q10c_4", "Q10c_5", "Q10c_6", "Q10c_7", "Q10c_8", "Q10c_9", "Q10d_0", "Q10d_1", "Q10d_2", "Q10d_3", "Q10d_4", "Q10d_5", "Q10d_6", "Q10d_7", "Q10d_8", "Q10d_9", "Q10d_10", "Q10d_11", "Q10d_12", "Q10d_13", "Q10d_14", "Q11_0", "Q11_1", "Q11_2", "Q11_3", "Q11_4", "Q11_5", "Q11_6", "Q12", "Q12b", "Q13", "Q14_1", "Q14_2", "Q14_3", "Q14_4", "Q14_5", "Q15_0", "Q15_1", "Q15_2", "Q15_3", "Q15_4", "Q16_0", "Q16_1", "Q16_2", "Q16_3", "Q16_4", "Q17_0", "Q17_1", "Q17_2", "Q17_3", "Q17_4", "Q17_5") FROM stdin;
\.


--
-- Data for Name: epidb_results_weekly; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY epidb_results_weekly (country, global_id, "timestamp", "Q1_0", "Q1_1", "Q1_2", "Q1_3", "Q1_4", "Q1_5", "Q1_6", "Q1_7", "Q1_8", "Q1_9", "Q1_10", "Q1_11", "Q1_12", "Q1_13", "Q1_14", "Q1_15", "Q1_16", "Q1_17", "Q1_18", "Q1_19", "Q2", "N1", "Q3", "Q3_0_open", "Q4", "Q4_0_open", "Q5", "Q6", "Q6_1_open", "Q6b", "Q6c", "Q6d", "Q7_0", "Q7_1", "Q7_3", "Q7_2", "Q7_4", "Q7_5", "Q7b", "Q8_0", "Q8_1", "Q8_2", "Q8_3", "Q8_4", "Q8_5", "Q8b", "Q9_0", "Q9_1", "Q9_2", "Q9_3", "Q9_4", "Q9_5", "Q9_6", "Q9b", "Q10", "Q10b", "Q10c", "Q11", "Q12_multi_row1_col1", "Q13_multi_row1_col1") FROM stdin;
\.


--
-- PostgreSQL database dump complete
--

