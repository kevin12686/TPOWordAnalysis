import re
import requests


def lookup_dictionaryapi(word):
    word = word.lower()
    resp = requests.get('https://api-portal.dictionary.com/dcom/pageData/%s' % word)
    if resp.status_code == 200:
        resp_json = resp.json()
        if resp_json['data']:
            definition = resp_json['data']['content'][0]['entries'][0]['posBlocks'][0]['definitions'][0]['definition']
            plural_match = re.search(r'the plural of <a[^>]*>(\w+)</a>', definition)
            past_match = re.search(r'past tense of <a[^>]*>(\w+)</a>', definition)
            pp_match = re.search(r'past participle of <a[^>]*>(\w+)</a>', definition)
            if plural_match:
                return plural_match.group(1).lower(), resp.text
            elif past_match:
                return past_match.group(1).lower(), resp.text
            elif pp_match:
                return pp_match.group(1).lower(), resp.text
            else:
                if re.match(r'^[a-z]+ed$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ed(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp.text
                elif re.match(r'^[a-z]+ly$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ly(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp.text
                elif re.match(r'^[a-z]+ing$', word) and word == resp_json['data']['displayForm']:
                    origin = resp_json['data']['content'][0]['entries'][0]['origin']
                    origin_match = re.search(r'<a[^>]*>(\w+)(<sup>\d+</sup>)?</a>\s*.\s*<a[^>]*>-ing(<sup>\d+</sup>)?</a>', origin)
                    if origin_match:
                        return origin_match.group(1).lower(), resp.text
            return resp_json['data']['displayForm'].lower(), resp.text
        else:
            return None
    return None
