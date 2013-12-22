DROP TABLE IF EXISTS epidb_results_intake;

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

INSERT INTO epidb_results_intake
SELECT 'ES',
    global_id, "timestamp", "Q0", "NOTE", "Q1", "Q2", "Q3", "Q4", "Q4b", "Q4b_0_open", "Q4c", "Q4d_0", "Q4d_1", "Q4d_2", "Q4d_3", "Q4d_4", "Q4d_5", "Q5_0", "Q5_1", "Q5_2", "Q5_3", "Q5_4", "Q6_0", "Q6_0_open", "Q6_1", "Q6_1_open", "Q6_2", "Q6_2_open", "Q6_3", "Q6_3_open", "Q6_4", "Q6_4_open", "Q6b", "Q7", "Q7b", "Q8", "Q9", "Q10", "Q10b", "Q10b_1_open", "Q10c_0", "Q10c_1", "Q10c_2", "Q10c_3", "Q10c_4", "Q10c_5", "Q10c_6", "Q10c_7", "Q10c_8", "Q10c_9", "Q10d_0", "Q10d_1", "Q10d_2", "Q10d_3", "Q10d_4", "Q10d_5", "Q10d_6", "Q10d_7", "Q10d_8", "Q10d_9", "Q10d_10", "Q10d_11", "Q10d_12", "Q10d_13", "Q10d_14", "Q11_0", "Q11_1", "Q11_2", "Q11_3", "Q11_4", "Q11_5", "Q11_6", "Q12", "Q12b", "Q13", "Q14_1", "Q14_2", "Q14_3", "Q14_4", "Q14_5", "Q15_0", "Q15_1", "Q15_2", "Q15_3", "Q15_4", "Q16_0", "Q16_1", "Q16_2", "Q16_3", "Q16_4", "Q17_0", "Q17_1", "Q17_2", "Q17_3", "Q17_4", "Q17_5" FROM pollster_results_intake;

