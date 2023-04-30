import time
import json
import requests
import tqdm
import pandas as pd
from collections import Counter
from IPython.display import display, clear_output
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
import config

'''Функция для сохранения JSON-файла в рабочую папку'''
'''Save JSON file to the working directory'''

def dump_json(obj, filename):
        with open(filename, 'w', encoding='UTF-8') as f: 
            json.dump(obj, f, ensure_ascii=False, indent=4)

            
'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨'''          
            
'''Функция для парсинга вакансий с сайта hh.ru'''
'''Parse vacancies at hh.ru'''

def get_vacancies(page = config.PAGE,
    per_page = config.PER_PAGE,
    period = config.PERIOD,
    text = config.TEXT,
    experience = config.EXPERIENCE,
    employment= config.EMPLOYMENT,
    schedule = config.SCHEDULE,
    area= config.AREA,
    industry = config.INDUSTRY,
    salary = config.SALARY,
    only_with_salary = config.ONLY_WITH_SALARY):

    params = {
        'page': page,
        'per_page': per_page,
        'period': period,
        'text': text,
        'experience': experience,
        'employment': employment,
        'schedule': schedule,
        'area': area,
        'industry': industry,
        'salary': salary,
        'only_with_salary': only_with_salary,
        }
    
    res = requests.get('https://api.hh.ru/vacancies', params=params)
    if not res.ok:
        print('Error:', res)
    vacancies = res.json()['items']
    pages = res.json()['pages']

    for page in tqdm.trange(1, pages):
        params['page'] = page
        res = requests.get('https://api.hh.ru/vacancies', params=params)
        if res.ok:
            response_json = res.json()
            vacancies.extend(response_json['items'])
        else:
            print(res)
            
    # dump_json(vacancies, 'vacancies.json')
    return vacancies


'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨''' 

'''Функция для получения файла с описаниями вакансий (примерно 100 вакансий в минуту)'''
'''Get a new file with job descriptions (around 100 descriptions per min)'''

def get_full_descriptions(vacancies):
    vacancies_full = []
    for entry in tqdm.tqdm(vacancies):
        vacancy_id = entry['id']
        description = requests.get(f'https://api.hh.ru/vacancies/{vacancy_id}')
        vacancies_full.append(description.json())
        print(description.json())
        time.sleep(0.2)
        clear_output()
    dump_json(vacancies_full, 'vacancies_full.json')
    return vacancies_full


'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨''' 

'''Функция для скачивания существующего файла c описаниями вакансий c Гугл Диска'''
'''Download an existing file with job descriptions from Google Drive'''

def load_from_gdrive(file_id, filename):
    url = f'https://drive.google.com/uc?export=view&id={file_id}'
    res = requests.get(url)
    vacancies_full = res.json()
    dump_json(vacancies_full, filename)
    return vacancies_full


'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨''' 

'''Функция для открытия существующего локального файла c описаниями вакансий'''
'''Open an existing local file with job descriptions'''

def load_from_device(file_path):
    with open(f'{file_path}', encoding='utf8') as f: vacancies_full = json.load(f)
    return vacancies_full


'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨''' 

'''Составить список ключевых навыков, отсортированных по популярности'''
'''Make a list of key skills sorted by frequency'''

def sort_skills_by_freq(vacancies_full):
    all_skills = []
    for vacancy in vacancies_full:
        if vacancy['key_skills'] is None:
            continue
        else:
            for skill in vacancy['key_skills']:
                all_skills.append(skill['name'])
    frequencies = Counter(all_skills)

    freq_table = pd.DataFrame.from_dict(frequencies, orient='index', columns=['Frequency'])
    freq_table = freq_table.sort_values('Frequency', ascending=False)
    pd.set_option('display.max_rows', None)
    print(freq_table)
    
    return frequencies
    

'''✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨🐳✨🐬✨🐟✨🐠✨''' 

'''Отобразить и сохранить вордклауд с ключевыми навыками'''
'''Display and save key skills as a wordcloud'''

def make_cloud(frequencies):
    print(f'Топ навыков для позиции {config.TEXT}:')
    cloud = WordCloud(background_color='black', width=800, height=600, color_func=lambda *args, **kwargs: "white")
    my_image = cloud.generate_from_frequencies(frequencies=frequencies).to_image()
    display(my_image)
    my_image.save(f'top_skill_wordcloud.png')