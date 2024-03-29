import re
import json
import requests


def lookup_dictionaryapi_parse(word):
    word = word.lower()
    resp = requests.get('https://api-portal.dictionary.com/dcom/pageData/%s' % word)
    if resp.status_code == 200:
        return lookup_dictionaryapi(word, resp.text)
    return None


def lookup_dictionaryapi(word, resp_text):
    resp_json = json.loads(resp_text)
    if resp_json['data']:
        try:
            definition = resp_json['data']['content'][0]['entries'][0]['posBlocks'][0]['definitions'][0]['definition']
            plural_match = re.search(r'the plural of <a[^>]*>(\w+)(<sup>\d+</sup>)?</a>', definition)
            past_match = re.search(r'past tense of <a[^>]*>(\w+)(<sup>\d+</sup>)?</a>', definition)
            pp_match = re.search(r'past participle of <a[^>]*>(\w+)(<sup>\d+</sup>)?</a>', definition)
            if plural_match:
                return plural_match.group(1).lower(), resp_text
            elif past_match:
                return past_match.group(1).lower(), resp_text
            elif pp_match:
                return pp_match.group(1).lower(), resp_text
            else:
                if re.match(r'^[a-z]+ed$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ed(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp_text
                elif re.match(r'^[a-z]+ly$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ly(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp_text
                elif re.match(r'^[a-z]+ing$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ing(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp_text
        except KeyError:
            pass
        return resp_json['data']['displayForm'].lower(), resp_text
    else:
        return None, None
