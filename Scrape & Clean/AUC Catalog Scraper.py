from selenium import webdriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
import mysql.connector
import time
import json
import re


def scrape():

    departments_list = []
    courses_list = []
    courses_list2 = []
    course_comp = []

    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    desired_capabilities = options.to_capabilities()
    chrome_path = 'D:/AUC/Fall 20/Database/Project/MS2/auc_catalog/auc_catalog/chromedriver.exe'

    link = 'http://catalog.aucegypt.edu/content.php?catoid=36&navoid=1738'
    driver = webdriver.Chrome(
        executable_path=chrome_path, desired_capabilities=desired_capabilities)
    driver.get(link)

    next_page = 2
    while True:

        wait = WebDriverWait(driver, 5)
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".width a")))

        departments = driver.find_elements_by_css_selector("p strong")
        departments_count = 0
        courses = driver.find_elements_by_css_selector(".width a")
        courses_count = 0

        for department in departments:
            departments_count += 1
            department_name = department.text
            department_code = department.find_element_by_xpath(
                "../../../following-sibling::tr").find_element_by_css_selector(
                ".width a").text.split(' ')[0]
            departments_list.append(
                {'Dept_Code': department_code, 'Dept_Name': department_name})

        for course in courses:
            courses_list.append(course.text.split(
                ' ')[0] + ' ' + re.search(r"(?<= ).*(?=/)", course.text).group() + '/' + re.search(r"(?<=/)\d{4}", course.text).group())
            course.click()
            time.sleep(1)
            courses_count += 1
        time.sleep(3)
        courses = driver.find_elements_by_css_selector(".clearfix+ div")

        for course in courses:

            header = course.find_element_by_css_selector(
                "h3").text
            dept_code = header.split(' ')[0]

            try:
                old_course_code = re.search(
                    r"(\d{2,3}|\d{3}\w)(?=/)", header).group()
            except:
                print("ERROR is here: ", header)
                raise
            new_course_code = re.search(
                r"(?<=/)\d{4}", header).group()

            if header.count('(') == 1:
                course_name = header.split('- ')[1].split(' (')[0]
                credits_number = header.split('(')[1][:-1]
            elif header.count('(') == 0:
                course_name = header.split('- ')[1]
                credits_number = 'Null'
            else:
                course_name = header.split(
                    '- ')[1].split(' (')[0] + ' (' + header.split(' (')[1]
                credits_number = header.split('(')[header.count('(')][:-1]

            try:
                course_description = re.search(
                    r"(?<=Description\n).+", course.text).group()
            except:
                course_description = 'Null'

            try:
                course_notes = re.search(
                    r"(?<=Notes\n).+", course.text).group()
            except:
                course_notes = 'Null'

            try:
                course_prerequisites = re.search(
                    r"(?<=Prerequisites\n).+", course.text).group()
            except:
                course_prerequisites = 'Null'

            try:
                offered_in = re.search(
                    r"(?<=When Offered\n).+", course.text).group()
            except:
                offered_in = 'Null'

            try:
                cross_listed_as = re.search(
                    r"(?<=Cross-listed\n).+", course.text).group()
            except:
                cross_listed_as = 'Null'

            course_comp.append(dept_code + ' ' +
                               old_course_code + '/' + new_course_code)
            courses_list2.append({'Dept_Code': dept_code, 'Old_Course_Code': old_course_code, 'New_Course_Code': new_course_code, 'Course_Name': course_name, 'Credits_Number': credits_number,
                                  'Description': course_description, 'Notes': course_notes, 'Prerequisites': course_prerequisites, 'Semesters_Offered': offered_in, 'Cross_Listed': cross_listed_as})
        try:
            driver.find_element_by_link_text(str(next_page)).click()
            next_page += 1
        except:
            break

    driver.quit()
    with open("Courses_List2.json", "w") as cf2:
        json.dump(courses_list2, cf2)

    with open("Departments.json", "w") as df:
        json.dump(departments_list, df)


def parse():
    df_courses = pd.read_json('Courses_List2.json', dtype='object')

    df_departments = pd.read_json('Departments.json', dtype='object')

    # Clean the Credits Column

    # remove whitespaces from credits
    df_courses.Credits_Number = df_courses.Credits_Number.str.strip()

    # replace all representaions of 3 credit by 3
    credits_to_replace = df_courses[df_courses.Credits_Number.str.contains(
        '-3') | df_courses.Credits_Number.str.contains('- 3')].Credits_Number.unique()
    credits_to_replace = np.append(credits_to_replace, ['up to 3 cr.', '3 cr. Max.', '3cr.', '3 cr.',
                                                        '1, 2, or 3 cr.', '3 cr. per semester', '3 cr. each per semester', '3 cr. each', '3 cr', '3 cr. max.'])
    to_replace_with = '3'
    df_courses.Credits_Number.replace(
        credits_to_replace, to_replace_with, inplace=True)

    # replace all representaions of 4 credit by 4
    credits_to_replace = df_courses[df_courses.Credits_Number.str.contains(
        '-4')].Credits_Number.unique()
    to_replace_with = '4'
    df_courses.Credits_Number.replace(
        credits_to_replace, to_replace_with, inplace=True)

    # replace all representaions of 0 credit by 0
    credits_to_replace = df_courses[df_courses.Credits_Number.str.contains(
        'no ') | df_courses.Credits_Number.str.contains('0 ')].Credits_Number.unique()
    to_replace_with = '0'
    df_courses.Credits_Number.replace(
        credits_to_replace, to_replace_with, inplace=True)

    # replace all representaions of 6 credit by 6
    credits_to_replace = df_courses[df_courses.Credits_Number.str.contains(
        '6')].Credits_Number.unique()
    to_replace_with = '6'
    df_courses.Credits_Number.replace(
        credits_to_replace, to_replace_with, inplace=True)

    # replace all credits with x + y with their sum
    credits_to_replace = df_courses[df_courses.Credits_Number.str.contains(
        '\+')].Credits_Number.unique()
    to_replace_with = []

    for x in credits_to_replace:
        y = np.array(re.findall(r"(\d)", x)).astype(int)
        y = sum(y)
        to_replace_with.append(str(y))
    df_courses.Credits_Number.replace(
        credits_to_replace, to_replace_with, inplace=True)

    # remove all the non number characters from credits while  saving the NUlls
    df_courses.Credits_Number.replace('Null', '10', inplace=True)
    df_courses.Credits_Number = df_courses.Credits_Number.str.replace(
        r'[^?<=\d]+$', '')
    df_courses.Credits_Number = df_courses.Credits_Number.astype(float)
    df_courses.Credits_Number.replace(10, np.nan, inplace=True)

    df_prerequisites = df_courses[[
        'Dept_Code', 'Old_Course_Code', 'New_Course_Code', 'Prerequisites']].copy()
    df_semesters = df_courses[[
        'Dept_Code', 'Old_Course_Code', 'New_Course_Code', 'Semesters_Offered']].copy()
    df_courses.drop(['Prerequisites', 'Semesters_Offered'],
                    axis=1, inplace=True)

    # Clean the Prerequisite Column in df_prerequisites
    concurrent = []
    updated_prerequesits = []
    for i, j in enumerate(df_prerequisites.Prerequisites):
        if(re.search(r"(\w.*\d{4})", j)):
            if(re.search(r"(concurrent)|(Co-requisite)", j, flags=re.IGNORECASE)):
                concurrent.append('Yes')
            else:
                concurrent.append('No')
            j = re.search(r"(\w.*\d{4})", j).group()
            if(re.search(r" or", j, flags=re.IGNORECASE)):
                if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", j)):
                    j = re.search(
                        r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", j).group()
                else:
                    j = re.search(r"(\b\w{4} .*?\d{4}){1}", j).group()

            if(',' in j):
                j = j.split(',')

                j_temp = []
                for y in j:
                    if(re.search(r"(\b(\w{4}|\w{3}) .*?(\d{4})){1}", y)):
                        if(re.search(r" and ", y, flags=re.IGNORECASE)):
                            y = y.split(' and ')

                            y_temp = []
                            for z in y:
                                if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", z)):
                                    z = re.search(
                                        r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", z).group()
                                    y_temp.append(z)
                            j_temp.extend(y_temp)

                        elif(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y)):
                            y = re.search(
                                r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y).group()
                            j_temp.append(y)
                j = j_temp

            elif(re.search(r" and ", j, flags=re.IGNORECASE)):
                j = re.split(r" and ", j, flags=re.IGNORECASE)

                j_temp = []
                for y in j:
                    if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y)):
                        y = re.search(
                            r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y).group()
                        j_temp.append(y)
                j = j_temp

            elif(re.search(r"-", j)):
                j_temp = []
                if(re.search(r"\d-\d", j)):
                    y = re.split(r"-", j)
                    y[0] = re.search(
                        r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y[0]).group()
                    copied_code = re.search(
                        r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y[0]).group()
                    copied_code = re.search(
                        r"\b(\w{4}|\w{3})", copied_code).group()
                    for z in range(1, len(y)):
                        y[z] = copied_code + ' ' + y[z]
                    j_temp.extend(y)
                    j = j_temp

                elif(re.search(r" - ", j)):
                    y = re.split(r" - ", j)
                    y_temp = []
                    for z in range(len(y)):
                        if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y[z])):
                            y_temp.append(
                                re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|\d{3}\/\d{4})){1}", y[z]).group())
                    j_temp.extend(y_temp)
                    j = j_temp
                elif(re.search(r"(\b(?:\w{4}|\w{3}) .?(?:\d{4}|(?:\d{3}/\d{4}))){1}", j)):
                    j = re.findall(
                        r"(\b(?:\w{4}|\w{3}) .?(?:\d{4}|(?:\d{3}/\d{4}))){1}", j)
            elif(re.search(r"(\b(?:\w{4}|\w{3}) .?(?:\d{4}|(?:\d{3}/\d{4}))){1}", j)):
                j = re.findall(
                    r"(\b(?:\w{4}|\w{3}) .?(?:\d{4}|(?:\d{3}/\d{4}))){1}", j)

            # elif(j !='PHYS 1021. Co-requisite MACT 2141'):
            #    j='Null'

            # if(j=='PHYS 1021. Co-requisite MACT 2141'):
            #    j=['PHYS 1021', 'MACT 2141']
        else:
            j = "Null"
            concurrent.append('Null')
        if(type(j) == list):
            j = ",".join(j)
        updated_prerequesits.append(j)
    df_prerequisites.Prerequisites = updated_prerequesits
    df_prerequisites['Concurrent'] = concurrent

    df_prerequisites = split_df_rows_for_comma_separated_key(
        "Prerequisites", df_prerequisites)

    prerequisites_list = df_prerequisites.Prerequisites.unique()
    for i, b in enumerate(prerequisites_list):
        if re.search(r"\w{4} \d{3}/\d{4}", b):
            prerequisites_list[i] = re.sub(r"\w{4} \d{3}/\d{4}", "", b)

    prerequisites_change_dict = {}
    for w in prerequisites_list:
        found_match = False
        for index in df_prerequisites.index:
            if (df_prerequisites.loc[index, "Dept_Code"] + ' ' + df_prerequisites.loc[index, "New_Course_Code"]) == w:
                prerequisites_change_dict[w] = df_prerequisites.loc[index, "Dept_Code"] + ' ' + \
                    df_prerequisites.loc[index, 'Old_Course_Code'] + \
                    '/' + df_prerequisites.loc[index, "New_Course_Code"]
                found_match = True
                break
        if not found_match:
            prerequisites_change_dict[w] = "NULL"
    df_prerequisites.Prerequisites.replace(
        prerequisites_change_dict, inplace=True)

    df_prerequisites[['Prerequisites_Dept_Code', 'Prerequisites_Course_Code']] = df_prerequisites.Prerequisites.apply(
        lambda x: pd.Series(str(x).split(" ")) if x != 'NULL' else pd.Series([x] * 2))
    df_prerequisites[['Prerequisites_Old_Curse_Code', 'Prerequisites_New_Course_Code']] = df_prerequisites.Prerequisites_Course_Code.apply(
        lambda x: pd.Series(str(x).split("/")) if x != 'NULL' else pd.Series([x] * 2))
    df_prerequisites.drop(['Prerequisites_Course_Code',
                           'Prerequisites'], axis=1, inplace=True)
    df_prerequisites = df_prerequisites.reindex(['Dept_Code', 'Old_Course_Code', 'New_Course_Code', 'Prerequisites_Dept_Code',
                                                 'Prerequisites_Old_Curse_Code', 'Prerequisites_New_Course_Code', 'Concurrent'], axis=1)

    # Clean Semesters Column in df_Semesters
    parsed_semesters = []
    for i, j in enumerate(df_semesters.Semesters_Offered):
        if(re.search(r"fall|spring|summer|winter", j, flags=re.IGNORECASE)):
            j = re.findall(r"fall|spring|summer|winter",
                           j, flags=re.IGNORECASE)
        else:
            j = 'Null'
        if(type(j) == list):
            j = ",".join(j)
        parsed_semesters.append(j)

    df_semesters.Semesters_Offered = parsed_semesters
    df_semesters = split_df_rows_for_comma_separated_key(
        "Semesters_Offered", df_semesters)

    parsed_cross_listed = []
    for i, j in enumerate(df_courses.Cross_Listed):
        if(j != 'Null'):
            if(re.search(r"same as", j, flags=re.IGNORECASE)):
                j = re.sub(r"same as", "", j, flags=re.IGNORECASE).strip()
            elif(re.search(r"Cross-listed with", j, flags=re.IGNORECASE)):
                j = re.sub(r"Cross-listed with", "", j,
                           flags=re.IGNORECASE).strip()
            if(re.search(r",", j)):
                j = re.split(r",", j)
                j_temp = []
                for z in range(len(j)):
                    j[z] = j[z].strip()
                    if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z])):
                        j_temp.append(
                            re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z]).group())
                j = j_temp
            elif(re.search(r"/", j)):
                j = re.split(r"/", j)
                j_temp = []
                for z in range(len(j)):
                    j[z] = j[z].strip()
                    if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z])):
                        j_temp.append(
                            re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z]).group())
                j = j_temp
            elif(re.search(r" and ", j, flags=re.IGNORECASE)):
                j = re.split(r" and ", j, flags=re.IGNORECASE)
                j_temp = []
                for z in range(len(j)):
                    j[z] = j[z].strip()
                    if(re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z])):
                        j_temp.append(
                            re.search(r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j[z]).group())
                j = j_temp
            else:
                j = re.search(
                    r"(\b(\w{4}|\w{3}) .?(\d{4}|(\d{3}/\d{4}))){1}", j).group()
        if(type(j) == list):
            j = ",".join(j)
        parsed_cross_listed.append(j)
    df_courses.Cross_Listed = parsed_cross_listed

    df_courses.loc[df_courses['Cross_Listed'].duplicated(),
                   'Cross_Listed'] = 'Null'

    s = df_courses.set_index('Cross_Listed')['Dept_Code'] + ' ' + df_courses.set_index('Cross_Listed')[
        'Old_Course_Code'] + '/' + df_courses.set_index('Cross_Listed')['New_Course_Code']
    courses_list = s.index

    for index in df_courses.index:
        for c in courses_list:
            if ((df_courses.loc[index, "Dept_Code"] + ' ' + df_courses.loc[index, "New_Course_Code"]) in c) or ((df_courses.loc[index, "Dept_Code"] + ' ' + df_courses.loc[index, "New_Course_Code"]) == c):
                df_courses.loc[index, "Cross_Listed"] = s[c]

            elif ((df_courses.loc[index, "Dept_Code"] + ' ' + df_courses.loc[index, 'Old_Course_Code'] + '/' + df_courses.loc[index, "New_Course_Code"]) in c) or ((df_courses.loc[index, "Dept_Code"] + ' ' + df_courses.loc[index, 'Old_Course_Code'] + '/' + df_courses.loc[index, "New_Course_Code"]) == c):
                df_courses.loc[index, "Cross_Listed"] = s[c]

    df_courses.Cross_Listed = df_courses.Cross_Listed.replace(
        to_replace='\w{4} \d{4}', value='Null', regex=True)

    df_courses[['CrossListedDept_Code', 'CrossListed_Course_Code']] = df_courses.Cross_Listed.apply(
        lambda x: pd.Series(str(x).split(" ")) if x != 'Null' else pd.Series([x] * 2))
    df_courses[['CrossListed_Old_Course_Code', 'CrossListed_New_Course_Code']] = df_courses.CrossListed_Course_Code.apply(
        lambda x: pd.Series(str(x).split("/")) if x != 'Null' else pd.Series([x] * 2))
    df_courses.drop(['Cross_Listed', 'CrossListed_Course_Code'],
                    axis=1, inplace=True)

    df_semesters = df_semesters.rename(
        columns={'Semesters_Offered': 'Semester'})

    df_prerequisites = df_prerequisites.rename(columns={'Prerequisites_Dept_Code': 'Prerequisite_Dept_Code',
                                                        'Prerequisites_Old_Curse_Code': 'Prerequisite_Old_Curse_Code', 'Prerequisites_New_Course_Code': 'Prerequisite_New_Course_Code'})

    df_departments.drop_duplicates(subset=['Dept_Code'], inplace=True)

    # Insert tables to the database

    mydb = mysql.connector.connect(
        host="host IP",
        user="username",
        password="password",
        database="database name"
    )

    mycursor = mydb.cursor()

    for i, row in df_departments.iterrows():
        sql = "INSERT INTO department (Dept_Code, Dept_Name) VALUES (%s, %s)"
        mycursor.execute(sql, tuple(row))

        mydb.commit()

    df_courses = df_courses.replace(np.nan, 'NULL')
    df_courses.drop_duplicates(
        subset=['Dept_Code', 'Old_Course_Code', 'New_Course_Code'], inplace=True)

    for i, row in df_courses.iterrows():

        sql = "INSERT INTO `course` (Dept_Code, Old_Course_Code, New_Course_Code, Course_Name, Credits_Number, Description, Notes, CrossListedDept_Code, CrossListed_Old_Course_Code, CrossListed_New_Course_Code) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        try:
            mycursor.execute(sql, tuple(row)[:])
        except:
            continue
        mydb.commit()

    for i, row in df_semesters.iterrows():
        sql = "INSERT INTO `coursesemestersoffered` (Dept_Code, Old_Course_Code, New_Course_Code, Semester) VALUES (%s, %s, %s, %s)"
        mycursor.execute(sql, tuple(row)[:])

        mydb.commit()

    for i, row in df_prerequisites.iterrows():
        try:
            sql = "INSERT INTO `prerequisites` (Dept_Code, Old_Course_Code, New_Course_Code, Prerequisite_Dept_Code, Prerequisite_Old_Course_Code, Prerequisite_New_Course_Code, Concurrent) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            mycursor.execute(sql, tuple(row)[:])
        except:
            continue
        mydb.commit()


def split_df_rows_for_comma_separated_key(key, df):
    df = df.set_index(df.columns.drop(key, 1).tolist())[key].str.split(
        ',', expand=True).stack().reset_index().rename(columns={0: key}).loc[:, df.columns]
    df = df[df[key] != '']
    return df


def main():
    scrape()
    parse()


if __name__ == "__main__":
    main()
