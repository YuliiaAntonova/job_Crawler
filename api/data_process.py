import pandas as pd
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from decimal import Decimal
from jinja2 import Environment, FileSystemLoader


# Define a function to convert salary strings to Decimal and add the corresponding label
def convert_salary(salary_str):
    if isinstance(salary_str, str):
        match = re.search(r'\d+(\.\d+)?', salary_str)
        if match:
            numeric_part = match.group()
            numeric_value = Decimal(numeric_part.replace(',', ''))
            if 'K' in salary_str:
                return int(numeric_value), 'per year'
            elif ',' in salary_str:
                return int(numeric_value), 'per year'
            elif '.' in salary_str:
                return int(numeric_value), 'per hour'
            else:
                return int(numeric_value), 'per hour'
    else:
        return salary_str, ''


# Define a function to extract experience information
def extract_experience(text):
    sentences = sent_tokenize(text)
    words = [word_tokenize(sentence) for sentence in sentences]
    experience_pattern = r'(\d+)(\s*[\+]?|[\+]\s*)years'
    years_of_experience = None
    for sentence_words in words:
        sentence = ' '.join(sentence_words)
        match = re.search(experience_pattern, sentence, re.IGNORECASE)
        if match:
            years_of_experience = int(match.group(1))
            break
    return years_of_experience


# Define a function to categorize experience levels
def categorize_experience(row):
    title = row['title']
    experience = row['experience']
    if not pd.isna(experience):
        if 'software' in title.lower():
            if experience <= 2:
                return "Junior Software Engineer"
            elif 3 <= experience <= 4:
                return "Middle Software Engineer"
            else:
                return "Senior Software Engineer"
        elif 'data' in title.lower():
            if experience <= 2:
                return "Junior Data Engineer"
            elif 3 <= experience <= 4:
                return "Middle Data Engineer"
            else:
                return "Senior Data Engineer"
    return "Other"


def convert_utf8(s):
    return str(s)


def process_data(data_file):
    df = pd.read_csv('new_combined_results.csv')

    df['min_salary_year'], df['salary_type'] = zip(*df['min_salary'].apply(convert_salary))
    df['max_salary_year'], _ = zip(*df['max_salary'].apply(convert_salary))

    df.loc[df['salary_type'] == 'per hour', ['min_salary_year', 'max_salary_year']] *= 40 * 52
    df.loc[df['salary_type'] == 'per hour', ['min_salary_year', 'max_salary_year']] /= 1000

    df = df.fillna(value=0)
    df = df.astype({"min_salary_year": 'int', "max_salary_year": 'int'})

    df['description'] = df['description'].map(convert_utf8)

    df['experience'] = df['description'].apply(extract_experience)

    df['experience_level'] = df.apply(categorize_experience, axis=1)

    grouped_df = df.groupby('experience_level')

    new_df = pd.concat([group_data for _, group_data in grouped_df], ignore_index=True)

    result_df = df.groupby(['experience_level'])[['min_salary_year', 'max_salary_year']].mean().reset_index()
    result_df.columns = ['experience_level', 'avg_min_salary', 'avg_max_salary']
    result_df['avg_min_salary'] = result_df['avg_min_salary'].round(0).astype(int)
    result_df['avg_max_salary'] = result_df['avg_max_salary'].round(0).astype(int)
    res = result_df.to_dict('records')

    # Load the Jinja2 template environment
    # env = Environment(loader=FileSystemLoader('/Users/yuliiaantonova/job_Crowler/api/templates'))
    # Assuming you have a Jinja2 environment set up
    template_env = Environment(loader=FileSystemLoader('/api/templates'))
    template = template_env.get_template('index.html')

    # Assuming result_df is your DataFrame
    if res is not None and not result_df.empty:
        rendered_html = template.render(result_df=res)

    else:
        # Handle the case where result_df is None or empty
        # For example, you can render an error message
        rendered_html = "No data available"
    # print(rendered_html)
    return res


if __name__ == "__main__":
    process_data('new_combined_results.csv')
