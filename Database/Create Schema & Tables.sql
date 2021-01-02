CREATE DATABASE AUC_Catalog;

CREATE TABLE Department (
    Dept_Code VARCHAR(10) NOT NULL PRIMARY KEY,
    Dept_Name VARCHAR(200) NOT NULL
);

CREATE TABLE Student (
    AUC_ID INT NOT NULL PRIMARY KEY,
    Student_Name VARCHAR(50) NOT NULL,
    Grade VARCHAR(20) NOT NULL,
    GPA	Decimal(6,5)	NOT NULL
);

CREATE	TABLE Major (
	AUC_ID INT NOT NULL,
    Dept_Code VARCHAR(10) NOT NULL,
    PRIMARY	KEY(AUC_ID, Dept_Code),
    FOREIGN KEY (Dept_Code)
        REFERENCES Department (Dept_Code)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (AUC_ID)
        REFERENCES Student (AUC_ID)
        ON DELETE CASCADE ON UPDATE CASCADE	
);

CREATE TABLE Course (
    Dept_Code VARCHAR(10) NOT NULL,
    Old_Course_Code	VARCHAR(4)	NOT NULL,
    New_Course_Code CHAR(4) NOT NULL,
    Course_Name VARCHAR(200) NOT NULL,
    Credits_Number INT,
    Description TEXT,
    Notes TEXT,
    CrossListedDept_Code VARCHAR(10),
    CrossListed_Old_Course_Code	VARCHAR(4),
    CrossListed_New_Course_Code CHAR(4),
    PRIMARY KEY (Dept_Code , Old_Course_Code, New_Course_Code),
    FOREIGN KEY (Dept_Code)
        REFERENCES Department (Dept_Code)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (CrossListedDept_Code , CrossListed_Old_Course_Code, CrossListed_New_Course_Code)
        REFERENCES Course (Dept_Code , Old_Course_Code, New_Course_Code)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE CourseSemestersOffered (
    Dept_Code VARCHAR(10) NOT NULL,
    Old_Course_Code	VARCHAR(4)	NOT NULL,
    New_Course_Code CHAR(4) NOT NULL,
    Semester VARCHAR(10) NOT NULL,
    PRIMARY KEY (Dept_Code , Old_Course_Code, New_Course_Code , Semester),
    FOREIGN KEY (Dept_Code , Old_Course_Code, New_Course_Code)
        REFERENCES Course (Dept_Code , Old_Course_Code, New_Course_Code)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Prerequisites (
    Dept_Code VARCHAR(10) NOT NULL,
    Old_Course_Code	VARCHAR(4)	NOT NULL,
    New_Course_Code CHAR(4) NOT NULL,
    Prerequisite_Dept_Code VARCHAR(10) NOT NULL,
    Prerequisite_Old_Course_Code VARCHAR(4) NOT NULL,
    Prerequisite_New_Course_Code CHAR(4) NOT NULL,
    Concurrent VARCHAR(4) NOT NULL,
    PRIMARY KEY (Dept_Code, Old_Course_Code, New_Course_Code, Prerequisite_Dept_Code , Prerequisite_Old_Course_Code, Prerequisite_New_Course_Code),
    FOREIGN KEY (Dept_Code, Old_Course_Code, New_Course_Code)
        REFERENCES Course (Dept_Code, Old_Course_Code, New_Course_Code)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Prerequisite_Dept_Code , Prerequisite_Old_Course_Code, Prerequisite_New_Course_Code)
        REFERENCES Course (Dept_Code, Old_Course_Code, New_Course_Code)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Finished (
    AUC_ID INT NOT NULL,
    Dept_Code VARCHAR(10) NOT NULL,
    Old_Course_Code	VARCHAR(4)	NOT NULL,
    New_Course_Code CHAR(4) NOT NULL,
    Letter_Grade VARCHAR(3) NOT NULL,
    Year	CHAR(4)	NOT	NULL,
	Semester	VARCHAR(10)	NOT NULL,
	PRIMARY KEY (AUC_ID, Dept_Code, Old_Course_Code, New_Course_Code),
    FOREIGN KEY (AUC_ID)
        REFERENCES Student (AUC_ID)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Dept_Code, Old_Course_Code, New_Course_Code)
        REFERENCES Course (Dept_Code, Old_Course_Code, New_Course_Code)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE Reviews (
    AUC_ID INT NOT NULL,
    Dept_Code VARCHAR(10) NOT NULL,
    Old_Course_Code	VARCHAR(4)	NOT NULL,
    New_Course_Code CHAR(4) NOT NULL,
    Rating INT NOT NULL,
    Text_Review TEXT NOT NULL,
    PRIMARY KEY (AUC_ID , Dept_Code, Old_Course_Code, New_Course_Code),
    FOREIGN KEY (AUC_ID)
        REFERENCES Student (AUC_ID)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (Dept_Code , Old_Course_Code, New_Course_Code)
        REFERENCES Course (Dept_Code , Old_Course_Code, New_Course_Code)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE VIEW verified_reviews AS SELECT
    R.AUC_ID,
    R.Dept_Code,
    R.Old_Course_Code,
    R.New_Course_Code,
    C.Course_Name,
    R.Rating,
    R.Text_Review,
    CASE WHEN(ISNULL(F.Semester)) THEN 'No' ELSE 'Yes'
END AS Verified
FROM
    reviews R
LEFT OUTER JOIN finished F ON
    R.AUC_ID = F.AUC_ID AND R.Dept_Code = F.Dept_Code AND R.Old_Course_Code = F.Old_Course_Code AND R.New_Course_Code = F.New_Course_Code
INNER JOIN course C ON
    R.Dept_Code = C.Dept_Code AND R.Old_Course_Code = C.Old_Course_Code AND R.New_Course_Code = C.New_Course_Code
GROUP BY
    R.AUC_ID,
    R.Dept_Code,
    R.Old_Course_Code,
    R.New_Course_Code;
