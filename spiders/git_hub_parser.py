import json
import re


class GitHubParser:
    @staticmethod
    def parse_api_keys(response):
        api_key_pattern = r'AIza[a-zA-Z0-9_\-]{26,46}'
        api_keys = []

        script_text = response.xpath('//script[contains(text(), "results")]/text()').get()
        json_data = json.loads(script_text)
        results = json_data['payload']['results']
        for result in results:
            snippets = result.get('snippets')
            if not snippets:
                continue
            for snippet in snippets:
                lines = snippet.get('lines')
                if not lines:
                    continue
                line_str = ''.join([line for line in lines if line]).replace('</mark>', '')
                matches = re.findall(api_key_pattern, line_str)
                api_keys.extend(matches)
        return api_keys
