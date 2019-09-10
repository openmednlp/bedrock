import os
import sys
import glob
import string
import re
import time
import random
from datetime import datetime
from datetime import timedelta

# import pandas
import pandas as pd

# import types
from typing import Pattern
from typing import List


class Deidentificator:
    def __init__(self, lastnames: List, prenames: List, postcodes: List, street_names: List=[], city_names: List=[]):
        # swiss postcode regex
        self.post_code_regex = re.compile(r'[^\.]\b([1-9]\d{3})\s\b')

        # regex for street names
        street_reg_string = '\\b('+'|'.join(street_names)+')\\s\\d{1,4}\\b'
        street_reg_string = street_reg_string.replace(' ', '\s')
        self.street_list = street_names
        self.street_regex = re.compile(street_reg_string)

        # postcode set
        self.postcode_set = set(postcodes)
        self.postcode_list = postcodes

        # name sets
        self.prename_list = prenames
        self.lastname_list = lastnames
        self.lastname_set = set(lastnames)
        self.prename_set = set(prenames)

        # regex for cities
        city_reg_string = '\\b('+'|'.join(city_names)+')\\b'
        city_reg_string = city_reg_string.replace(' ', '\s')
        self.city_regex = re.compile(city_reg_string)
        self.city_list = city_names

        self.abbreviation_regex = re.compile(r'(?:(?:\s?Professo[reni]+)|(?:\s?Prof\.?)|(?:\s?Dr\.?)|(?:\s[mM]ed\.?)|(?:Doktor)|(?:Kolleg[ine]+)|(?:\sP[D|d])|(?:Her[ren]+)|(?:Fra[uen]+)|(?:[A-Za-z]*[AÄaä]rzt(?:in)))+\s(?:(?:[A-Z]{1,2}\s)|(?:(?:[A-Z]\.?\s){0,2}))?(?P<prename>[A-Z]\w{1,64}\s)?(?P<name>[A-Z]\w{1,64})', re.U)

        # regex for dates
        self.date_regex = re.compile(r'(3[01]|[12][0-9]|0?[1-9])\.(1[012]|0?[1-9])\.((?:19|20)\d{2})')

        # regex for swiss phone number
        self.phone_regex = re.compile(r'(\+41|0041|0|00)(\s|-)?(\d{2})(\s|-)?(\d{3})(\s|-)?(\d{2})(\s|-)?(\d{2})')

        # email adresses regex
        self.email_regex = re.compile(r"""\b(
            [a-zA-Z0-9_.+-@\"]+@[a-zA-Z0-9-\:\]\[]+[a-zA-Z0-9-.]*
        )\b""", re.X | re.I)

        self.email_providers = ['gmail.com', 'yahoo.de', 'yahoo.com', 'mail.com', 'gmx.net', 'gmx.de', 'gmx.ch', 'bluewin.ch', 'windowslive.com', 'hotmail.com', 'msn.com', 'aol.de', 'aol.com', 'outlook.com', 'me.com']
        self.seps = ['.', '', '_', '-']

    def __tag_abbreviation(self, document: str, substitution_list: pd.DataFrame) -> (str, pd.DataFrame):
        for match in re.finditer(self.abbreviation_regex, document):
            prename_group = match.group('prename')
            name_group = match.group('name')

            if prename_group is None and name_group is not None:
                span = match.span('name')
                group = match.group('name')
                type = 'abbreviation_name'
            elif prename_group is not None and name_group is not None:
                if prename_group in self.prename_set and name_group in self.lastname_set:
                    span = match.span('prename')
                    group = match.group('prename')
                    type = 'abbreviation_prename'
                    substitution_list = substitution_list.append({
                        'start': span[0],
                        'end': span[1],
                        'type': type,
                        'span': group
                    }, ignore_index=True)
                    span = match.span('name')
                    group = match.group('name')
                    type = 'abbreviation_name'
                else:
                    span = match.span('name')
                    group = match.group('name')
                    type = 'abbreviation_name'
            elif prename_group is not None and name_group is None:
                span = match.span('prename')
                group = match.group('prename')
                type = 'abbreviation_name'
            else:
                continue

            substitution_list = substitution_list.append({
                'start': span[0],
                'end': span[1],
                'type': type,
                'span': group
            }, ignore_index=True)

        return substitution_list

    def __tag_regex(self, document: str, compiled_regex: Pattern, type: str, substitution_list: pd.DataFrame, group: int = -1, recheck_list = None) -> (str, pd.DataFrame):
        for match in compiled_regex.finditer(document):
            if group < 0:
                group_name = match.group()
            else:
                group_name = match.group(group)
            if group < 0:
                span = match.span()
            else:
                span = match.span(group)
            substitution_list = substitution_list.append({
                'start': span[0],
                'end': span[1],
                'type': type,
                'span': group_name
            }, ignore_index=True)
        return substitution_list

    def __tag_postcode(self, document, substitution_list) -> (str, pd.DataFrame):
        for match in re.finditer(self.post_code_regex, document):
            group = match.group(1)
            if int(group) not in self.postcode_set:
                continue
            span = match.span(1)
            substitution_list = substitution_list.append({
                'start': span[0],
                'end': span[1],
                'type': 'postcode',
                'span': group
            }, ignore_index=True)
        return substitution_list 

    def detect_identifiers(self, text: str, patient_prenames: List[str] = None, patient_lastname: str = None) -> pd.DataFrame:
        # initialize substituion list
        substitutions = pd.DataFrame(columns=['start', 'end', 'type', 'span', 'replacement'])

        substitutions = self.__tag_postcode(text, substitutions)
        substitutions = self.__tag_regex(text, self.email_regex, 'email', substitutions)
        substitutions = self.__tag_regex(text, self.date_regex, 'date', substitutions)
        substitutions = self.__tag_regex(text, self.city_regex, 'city', substitutions, group=1)
        substitutions = self.__tag_regex(text, self.street_regex, 'street', substitutions, group=1)
        substitutions = self.__tag_regex(text, self.phone_regex, 'phone', substitutions)
        substitutions = self.__tag_abbreviation(text, substitutions)
        if patient_prenames is not None:
            for prename in patient_prenames:
                substitutions = self.__tag_regex(text, re.compile('\\b' + prename + '\\b'), 'patient_prename', substitutions)
        if patient_lastname is not None:
            substitutions = self.__tag_regex(text, re.compile('\\b' + patient_lastname + '\\b'), 'patient_lastname', substitutions)
        return substitutions

    def create_nicknames(self, replacement_lists: List):
        replacements = {}
        lastnames = pd.DataFrame(self.lastname_list, columns=['names'])
        prenames = pd.DataFrame(self.prename_list, columns=['names'])
        days_to_add_to_dates = random.randint(-31, 31)
        for replacement_list in replacement_lists:
            replacement_list['replacement'] = replacement_list['replacement'].astype(str)
            for index, replacement in replacement_list.iterrows():
                if replacement['span'] in replacements and replacement['type'] != 'postcode':
                    replacement_list.at[index, 'replacement'] = replacements[replacement['span']]
                    continue
                if replacement['type'] == 'abbreviation_name' or replacement['type'] == 'lastname' or replacement['type'] == 'patient_lastname':
                    span = replacement['span']
                    first_char = span[0]
                    with_same_char_list = lastnames[lastnames['names'].str.startswith(first_char)]
                    replaced_name = with_same_char_list.sample().iloc[0]['names']
                    replacement_list.at[index, 'replacement'] = replaced_name
                    replacements[replacement['span']] = replaced_name
                    continue
                if replacement['type'] == 'abbreviation_firstname' or replacement['type'] == 'firstname' or replacement['type'] == 'patient_prename':
                    span = replacement['span']
                    first_char = span[0]
                    with_same_char_list = prenames[prenames['names'].str.startswith(first_char)]
                    replaced_name = with_same_char_list.sample()['names']
                    replacement_list.at[index, 'replacement'] = replaced_name
                    replacements[replacement['span']] = replaced_name
                    continue
                if replacement['type'] == 'date':
                    span = replacement['span']
                    date = datetime.strptime(span, '%d.%m.%Y') + timedelta(days=days_to_add_to_dates)
                    date_str = date.strftime('%d.%m.%Y')
                    replacement_list.at[index, 'replacement'] = date_str
                    replacements[replacement['span']] = date_str
                    continue
                if replacement['type'] == 'email':
                    prename_sample = prenames.sample().iloc[0]['names']
                    lastname_sample = lastnames.sample().iloc[0]['names']
                    sep = random.choice(self.seps)
                    provider = random.choice(self.email_providers)
                    end = ''
                    if random.randint(0, 10) > 5:
                        end = str(random.randint(1, 9))+str(random.randint(1, 9))
                    prename = prename_sample.lower()[0:random.randint(2, len(prename_sample))]
                    lastname = lastname_sample.lower()[0:random.randint(2, len(lastname_sample))]
                    email = prename + sep + lastname + end + '@' + provider
                    replacement_list.at[index, 'replacement'] = email
                    replacements[replacement['span']] = email
                if replacement['type'] == 'postcode':
                    near_cities = replacement_list[((replacement_list['start'] - replacement['end'] ) < 4) & (replacement['end'] < replacement_list['start']) & (replacement_list['type'] == 'city')].shape[0]
                    if near_cities < 1:
                        replacement_list.at[index, 'replacement'] = replacement['span']
                        continue
                    elif replacement['span'] in replacements:
                        replacement_list.at[index, 'replacement'] = replacements[replacement['span']]
                        continue
                    postcode = random.choice(self.postcode_list)
                    replacement_list.at[index, 'replacement'] = postcode
                    replacements[replacement['span']] = postcode
                    continue
                if replacement['type'] == 'city':
                    new_city = random.choice(self.city_list)
                    replacement_list.at[index, 'replacement'] = new_city
                    replacements[replacement['span']] = new_city
                    continue
                if replacement['type'] == 'street':
                    new_street = random.choice(self.street_list)
                    replacement_list.at[index, 'replacement'] = new_street
                    replacements[replacement['span']] = new_street
                    continue
                if replacement['type'] == 'street':
                    new_street = random.choice(self.street_list)
                    replacement_list.at[index, 'replacement'] = new_street
                    replacements[replacement['span']] = new_street
                    continue
                if replacement['type'] == 'phone':
                    new_phone = random.randint(100000000, 999999999)
                    code = ['0', '0041', '+41', '00']
                    return random.choice(code) + str(new_phone)
                    continue

        return replacement_lists

    def replace_text(self, text: str, replacement_list: pd.DataFrame) -> str:
        shift = 0
        replacement_list = replacement_list.sort_values(by=['start', 'end'])
        for _, replacement in replacement_list.iterrows():
            start = replacement['start'] + shift
            end = replacement['end'] + shift
            old_word = str(replacement['span'])
            new_word = str(replacement['replacement'])
            text = text[:start] + new_word + text[end:]
            shift = shift + len(new_word) - len(old_word)
        return text
        
    